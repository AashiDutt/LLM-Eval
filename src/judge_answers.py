import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from pydantic import BaseModel, Field

from .utils import (
    load_config, load_json, save_json, generate_timestamp,
    anonymize_and_shuffle, format_judge_prompt, extract_json_from_response
)
from .models import ModelFactory, ModelWrapper

print_lock = threading.Lock()

TEMPERATURE_MAP = {
    "claude-haiku-4-5": 0.5,
    "claude-sonnet-4-5": 0.5,
    "google/gemini-2.5-flash": 0.5,
    "google/gemini-3-pro-preview": 1.0,
    "gemini-2.5-flash": 0.5,
    "gemini-3-pro-preview": 1.0
}

class JudgmentSchema(BaseModel):
    ranking: list[str] = Field(
        ..., description="Ordered list of anonymized answer labels from best to worst."
    )
    scores: dict[str, int] = Field(
        ..., description="Dictionary mapping each label to an integer score between 0 and 10."
    )
    justification: str = Field(
        ..., description="Short explanation referencing concrete qualities that justify the ranking."
    )


def thread_safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)


def judge_prompt_answers(
    prompt_id: str,
    prompt_text: str,
    answers: list[dict[str, str]],
    judge_model: ModelWrapper,
    judge_name: str,
    shuffle_seed: int,
    verbose: bool = False
) -> dict[str, str]:
    anonymized, mapping = anonymize_and_shuffle(answers, seed=shuffle_seed)
    system_prompt, judge_prompt = format_judge_prompt(prompt_text, anonymized)
    
    if verbose:
        thread_safe_print(f"  Judge prompt: {len(judge_prompt)} chars")
        thread_safe_print(f"  Mapping: {mapping}")
    
    try:
        model_id = judge_model.model_name
        is_openai = "gpt" in model_id
        generate_kwargs = {
            "prompt": judge_prompt, "system_prompt": system_prompt, "response_model": JudgmentSchema
        }
        if not is_openai:
            generate_kwargs.update({"temperature": TEMPERATURE_MAP[model_id]})
        response = judge_model.generate(**generate_kwargs)
        
        if verbose:
            preview = response if isinstance(response, str) else str(response)
            thread_safe_print(f"  Judge response: {preview[:200]}...")
        
        if isinstance(response, BaseModel):
            judgment = response.model_dump()
        elif isinstance(response, dict):
            judgment = response
        else:
            judgment = extract_json_from_response(response)
        
        required_fields = ['ranking', 'scores', 'justification']
        for field in required_fields:
            if field not in judgment:
                raise ValueError(f"Missing required field: {field}")
        
        judgment_record = {
            "prompt_id": prompt_id,
            "judge_model": judge_name,
            "ranking": judgment['ranking'],
            "scores": judgment['scores'],
            "justification": judgment['justification'],
            "mapping": mapping,
            "anonymized_answers": [{"label": a['label'], "text": a['text'][:200] + "..."} 
                                   for a in anonymized]
        }
        
        return judgment_record
        
    except Exception as e:
        thread_safe_print(f"  ✗ Error judging {prompt_id} with {judge_name}: {e}")
        return {
            "prompt_id": prompt_id,
            "judge_model": judge_name,
            "error": str(e),
            "mapping": mapping
        }


def judge_all_answers(
    answers: list[dict[str, str]],
    model_factory: ModelFactory,
    config: dict[str, str],
    judges: list[str],
    verbose: bool = True,
    max_workers: int = 4
) -> list[dict[str, str]]:
    
    answers_by_prompt = {}
    for answer in answers:
        prompt_id = answer['prompt_id']
        if prompt_id not in answers_by_prompt:
            answers_by_prompt[prompt_id] = []
        answers_by_prompt[prompt_id].append(answer)
    
    shuffle_seed = config.get('judging', {}).get('shuffle_seed', 42)
    
    print(f"Judging {len(answers_by_prompt)} prompts with {len(judges)} judge(s)")
    
    judge_models = {}
    for judge_key in judges:
        vendor, tier = judge_key.split('_')
        judge_models[judge_key] = model_factory.get_model(vendor, tier)
    
    tasks = []
    for prompt_id, prompt_answers in answers_by_prompt.items():
        prompt_text = prompt_answers[0]['prompt_text']
        category = prompt_answers[0]['category']
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Judging: {prompt_id} ({category})")
            print(f"Question: {prompt_text[:80]}...")
            print(f"Answers: {len(prompt_answers)}")
        
        for judge_key in judges:
            if judge_models[judge_key] is not None:
                tasks.append({
                    "prompt_id": prompt_id,
                    "prompt_text": prompt_text,
                    "answers": prompt_answers,
                    "judge_key": judge_key,
                    "judge_model": judge_models[judge_key]
                })
    
    total_tasks = len(tasks)
    if verbose:
        print(f"\nRunning {total_tasks} judgment tasks with {max_workers} concurrent workers...")
    
    if total_tasks == 0:
        return []
    
    ordered_judgments: list[dict[str, str] | None] = [None] * total_tasks
    pbar = tqdm(total=total_tasks, desc="Judging answers") if verbose else None
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(
                judge_prompt_answers,
                prompt_id=task["prompt_id"],
                prompt_text=task["prompt_text"],
                answers=task["answers"],
                judge_model=task["judge_model"],
                judge_name=task["judge_key"],
                shuffle_seed=shuffle_seed,
                verbose=verbose
            ): idx for idx, task in enumerate(tasks)
        }
        
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            task = tasks[idx]
            try:
                judgment = future.result()
                ordered_judgments[idx] = judgment
                
                if verbose:
                    if 'error' in judgment:
                        thread_safe_print(f"  ✗ {task['judge_key']} → {task['prompt_id']}: {judgment['error']}")
                    else:
                        top_label = judgment['ranking'][0]
                        top_answer = judgment['mapping'].get(top_label, top_label)
                        thread_safe_print(f"  ✓ {task['judge_key']} → {task['prompt_id']} (top: {top_answer})")
            except Exception as e:
                thread_safe_print(f"  ✗ {task['judge_key']} → {task['prompt_id']} FAILED: {e}")
            finally:
                if pbar:
                    pbar.update(1)
    
    if pbar:
        pbar.close()
    
    return [judgment for judgment in ordered_judgments if judgment is not None]


def main():
    parser = argparse.ArgumentParser(description="Judge answers for bias evaluation")
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--answers", type=str, required=True)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--judges", type=str, nargs='+', default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--verbose", action="store_true", default=True)
    parser.add_argument("--workers", type=int, default=6, help="Number of concurrent judging workers (default: 4)")
    
    args = parser.parse_args()
    
    print("Loading configuration...")
    config = load_config(args.config)
    
    print(f"Loading answers from {args.answers}...")
    answers = load_json(args.answers)
    
    if args.judges:
        judges = args.judges
    else:
        primary_judge = config.get('judges', {}).get('primary', 'gemini_thinking')
        additional_judges = config.get('judges', {}).get('additional', [])
        judges = [primary_judge] + additional_judges
    
    print(f"Using judges: {', '.join(judges)}")
    
    if args.limit:
        prompt_ids = list(set(a['prompt_id'] for a in answers))[:args.limit]
        answers = [a for a in answers if a['prompt_id'] in prompt_ids]
        print(f"Limited to {len(prompt_ids)} prompts ({len(answers)} answers)")
    
    print(f"Loaded {len(answers)} answers")
    
    print("\nInitializing model factory...")
    model_factory = ModelFactory(config)
    
    print("\n" + "="*60)
    print("STARTING JUDGING PROCESS")
    print("="*60)
    
    judgments = judge_all_answers(
        answers=answers,
        model_factory=model_factory,
        config=config,
        judges=judges,
        verbose=args.verbose,
        max_workers=args.workers
    )
    
    if args.output is None:
        timestamp = generate_timestamp()
        output_path = f"data/judgments/judgments_{timestamp}.json"
    else:
        output_path = args.output
    
    print(f"\nSaving {len(judgments)} judgments to {output_path}")
    save_json(judgments, output_path)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    by_judge = {}
    errors = 0
    
    for judgment in judgments:
        judge = judgment['judge_model']
        by_judge[judge] = by_judge.get(judge, 0) + 1
        if 'error' in judgment:
            errors += 1
    
    print("\nJudgments by judge:")
    for judge, count in sorted(by_judge.items()):
        print(f"  {judge}: {count}")
    
    if errors > 0:
        print(f"\n⚠ Errors: {errors} judgments failed")
    
    print(f"\n✓ Done! Judgments saved to: {output_path}")


if __name__ == "__main__":
    main()
