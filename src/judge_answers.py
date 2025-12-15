import argparse
from tqdm import tqdm
from typing import List, Dict, Any

from utils import (
    load_config, load_json, save_json, generate_timestamp,
    anonymize_and_shuffle, format_judge_prompt, extract_json_from_response
)
from models import ModelFactory


def judge_prompt_answers(
    prompt_id: str,
    prompt_text: str,
    answers: List[Dict[str, Any]],
    judge_model,
    judge_name: str,
    shuffle_seed: int,
    verbose: bool = False
) -> Dict[str, Any]:
    anonymized, mapping = anonymize_and_shuffle(answers, seed=shuffle_seed)
    judge_prompt = format_judge_prompt(prompt_text, anonymized)
    
    if verbose:
        print(f"  Judge prompt: {len(judge_prompt)} chars")
        print(f"  Mapping: {mapping}")
    
    try:
        response = judge_model.generate(judge_prompt, temperature=0.3)
        
        if verbose:
            print(f"  Judge response: {response[:200]}...")
        
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
        print(f"  ✗ Error judging {prompt_id} with {judge_name}: {e}")
        return {
            "prompt_id": prompt_id,
            "judge_model": judge_name,
            "error": str(e),
            "mapping": mapping
        }


def judge_all_answers(
    answers: List[Dict[str, Any]],
    model_factory: ModelFactory,
    config: Dict[str, Any],
    judges: List[str],
    verbose: bool = True
) -> List[Dict[str, Any]]:
    all_judgments = []
    
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
    
    total_tasks = len(answers_by_prompt) * len(judges)
    pbar = tqdm(total=total_tasks, desc="Judging answers") if verbose else None
    
    for prompt_id, prompt_answers in answers_by_prompt.items():
        prompt_text = prompt_answers[0]['prompt_text']
        category = prompt_answers[0]['category']
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Judging: {prompt_id} ({category})")
            print(f"Question: {prompt_text[:80]}...")
            print(f"Answers: {len(prompt_answers)}")
        
        for judge_key in judges:
            judge_model = judge_models[judge_key]
            
            if verbose:
                print(f"  → Judge: {judge_key}...")
            
            judgment = judge_prompt_answers(
                prompt_id=prompt_id,
                prompt_text=prompt_text,
                answers=prompt_answers,
                judge_model=judge_model,
                judge_name=judge_key,
                shuffle_seed=shuffle_seed,
                verbose=verbose
            )
            
            all_judgments.append(judgment)
            
            if verbose and 'error' not in judgment:
                top_answer = judgment['mapping'][judgment['ranking'][0]]
                print(f"  ✓ Top answer: {top_answer}")
            
            if pbar:
                pbar.update(1)
    
    if pbar:
        pbar.close()
    
    return all_judgments


def main():
    parser = argparse.ArgumentParser(description="Judge answers for bias evaluation")
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--answers", type=str, required=True)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--judges", type=str, nargs='+', default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--verbose", action="store_true", default=True)
    
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
        verbose=args.verbose
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
