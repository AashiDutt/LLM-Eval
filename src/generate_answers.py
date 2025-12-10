import argparse
import json
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Any

from utils import load_config, load_prompts, save_json, generate_timestamp
from models import ModelFactory


def generate_answer(model_wrapper, prompt_text: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            answer = model_wrapper.generate(prompt_text)
            return answer
        except Exception as e:
            if attempt == retries - 1:
                print(f"Failed after {retries} attempts: {e}")
                return f"[ERROR: Failed to generate answer - {str(e)}]"
            print(f"Attempt {attempt + 1} failed, retrying...")
            continue


def generate_all_answers(
    prompts: List[Dict[str, Any]],
    model_factory: ModelFactory,
    output_dir: str,
    verbose: bool = True
) -> List[Dict[str, Any]]:
    all_answers = []
    models = model_factory.get_all_models()
    
    vendors = ['claude', 'gpt', 'gemini']
    tiers = ['fast', 'thinking']
    
    total_tasks = len(prompts) * len(vendors) * len(tiers)
    pbar = tqdm(total=total_tasks, desc="Generating answers") if verbose else None
    
    for prompt in prompts:
        prompt_id = prompt['id']
        prompt_text = prompt['text']
        category = prompt['category']
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Processing: {prompt_id} ({category})")
            print(f"Question: {prompt_text[:80]}...")
        
        for vendor in vendors:
            for tier in tiers:
                model_key = f"{vendor}_{tier}"
                model = models[model_key]
                
                if verbose:
                    print(f"  → {vendor.capitalize()} ({tier})...", end=" ")
                
                answer_text = generate_answer(model, prompt_text)
                
                answer_id = f"ans_{prompt_id}_{vendor}_{tier}"
                answer_record = {
                    "answer_id": answer_id,
                    "prompt_id": prompt_id,
                    "category": category,
                    "model_vendor": vendor,
                    "model_tier": tier,
                    "model_name": model.model_name,
                    "prompt_text": prompt_text,
                    "answer_text": answer_text
                }
                
                all_answers.append(answer_record)
                
                if verbose:
                    print(f"✓ ({len(answer_text)} chars)")
                
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
    
    print("\nInitializing model factory...")
    model_factory = ModelFactory(config)
    
    print("\nTesting API connections...")
    models = model_factory.get_all_models()
    for name, model in models.items():
        vendor, tier = name.split('_')
        print(f"  {vendor.capitalize()} ({tier}): {model.model_name}")
    
    print("\n" + "="*60)
    print("STARTING ANSWER GENERATION")
    print("="*60)
    
    answers = generate_all_answers(
        prompts=prompts,
        model_factory=model_factory,
        output_dir="data/answers",
        verbose=args.verbose
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
