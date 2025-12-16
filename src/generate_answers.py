import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .utils import load_config, load_prompts, save_json, generate_timestamp
from .models import ModelFactory

print_lock = threading.Lock()


def generate_answer(model_wrapper, prompt_text: str, retries: int = 3) -> str | dict[str, str]:
    for attempt in range(retries):
        try:
            answer = model_wrapper.generate(prompt_text)
            return answer
        except Exception as e:
            if attempt == retries - 1:
                return {"error": str(e)}
            continue


def generate_single_task(task: dict[str, str]) -> dict[ str, str]:
    model = task['model']
    prompt = task['prompt']
    vendor = task['vendor']
    tier = task['tier']
    
    answer_text = generate_answer(model, prompt['text'])
    
    return_dict =  {
        "answer_id": f"ans_{prompt['id']}_{vendor}_{tier}",
        "prompt_id": prompt['id'],
        "category": prompt['category'],
        "model_vendor": vendor,
        "model_tier": tier,
        "model_name": model.model_name,
        "prompt_text": prompt['text'],
    }
    if isinstance(answer_text, dict) and "error" in answer_text:
        return_dict.update(answer_text)
    else:
        return_dict["answer_text"] = answer_text

    return return_dict


def generate_all_answers(
    prompts: list[dict[str, str]],
    model_factory: ModelFactory,
    verbose: bool = True,
    max_workers: int = 6
) -> list[dict[str, str]]:
    models = model_factory.get_all_models()
    vendors = ['claude', 'gpt', 'gemini']
    tiers = ['fast', 'thinking']
    
    tasks = []
    for prompt in prompts:
        for vendor in vendors:
            for tier in tiers:
                model_key = f"{vendor}_{tier}"
                if models[model_key] is not None:
                    tasks.append({
                        'model': models[model_key],
                        'prompt': prompt,
                        'vendor': vendor,
                        'tier': tier
                    })
    
    total_tasks = len(tasks)
    if verbose:
        print(f"\nRunning {total_tasks} tasks with {max_workers} concurrent workers...")
    
    all_answers = []
    completed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {executor.submit(generate_single_task, task): task for task in tasks}
        
        pbar = tqdm(total=total_tasks, desc="Generating answers") if verbose else None
        
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result()
                all_answers.append(result)
                completed += 1
                
                if verbose:
                    with print_lock:
                        status = "✓" if "error" not in result else "✗"
                        tqdm.write(f"  {status} {task['vendor']}_{task['tier']} → {task['prompt']['id']} ({len(result['answer_text'])} chars)")
                
            except Exception as e:
                if verbose:
                    with print_lock:
                        tqdm.write(f"  ✗ {task['vendor']}_{task['tier']} → {task['prompt']['id']} FAILED: {e}")
            
            if pbar:
                pbar.update(1)
        
        if pbar:
            pbar.close()
    
    return all_answers


def main():
    parser = argparse.ArgumentParser(description="Generate answers from all models for bias evaluation")
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--prompts", type=str, default="prompts.json")
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--category", type=str, default=None)
    parser.add_argument("--verbose", action="store_true", default=True)
    parser.add_argument("--workers", type=int, default=6, help="Number of concurrent workers (default: 6)")
    
    args = parser.parse_args()
    
    print("Loading configuration...")
    config = load_config(args.config)
    
    print("Loading prompts...")
    prompts = load_prompts(args.prompts)
    
    if args.category:
        prompts = [p for p in prompts if p['category'] == args.category]
        print(f"Filtered to {len(prompts)} prompts in category '{args.category}'")
    
    if args.limit:
        prompts = prompts[:args.limit]
        print(f"Limited to first {args.limit} prompts")
    
    print(f"Processing {len(prompts)} prompts across 6 models (3 vendors × 2 tiers)")
    print(f"Total API calls: {len(prompts) * 6}")
    print(f"Concurrent workers: {args.workers}")
    
    print("\nInitializing model factory...")
    model_factory = ModelFactory(config)
    
    print("\nTesting API connections...")
    models = model_factory.get_all_models()
    for name, model in models.items():
        vendor, tier = name.split('_')
        if model and tier:
            print(f"  {vendor.capitalize()} ({tier}): {model.model_name}")
    
    print("\n" + "="*60)
    print("STARTING ANSWER GENERATION")
    print("="*60)
    
    answers = generate_all_answers(
        prompts=prompts,
        model_factory=model_factory,
        verbose=args.verbose,
        max_workers=args.workers
    )
    
    if args.output is None:
        timestamp = generate_timestamp()
        output_path = f"data/answers/answers_{timestamp}.json"
    else:
        output_path = args.output
    
    print(f"\nSaving {len(answers)} answers to {output_path}")
    save_json(answers, output_path)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    by_vendor = {}
    by_category = {}
    
    for answer in answers:
        vendor = answer['model_vendor']
        category = answer['category']
        
        by_vendor[vendor] = by_vendor.get(vendor, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1
    
    print("\nAnswers by vendor:")
    for vendor, count in sorted(by_vendor.items()):
        print(f"  {vendor.capitalize()}: {count}")
    
    print("\nAnswers by category:")
    for category, count in sorted(by_category.items()):
        print(f"  {category}: {count}")
    
    print(f"\n✓ Done! Answers saved to: {output_path}")


if __name__ == "__main__":
    main()
