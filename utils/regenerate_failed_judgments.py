#!/usr/bin/env python3
"""
Re-run failed judgments present in a judgments JSON file.

The script scans the judgments file for entries containing an `error` field,
reloads the corresponding prompt + answers from the main answers file, and
re-evaluates them with only the judge model responsible for the failure.
"""
from __future__ import annotations

import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple, Callable

from tqdm import tqdm

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils import load_config, load_json, save_json
from src.models import ModelFactory
from src.judge_answers import judge_prompt_answers


def build_answers_index(answers: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    answers_by_prompt: Dict[str, List[Dict[str, Any]]] = {}
    for ans in answers:
        answers_by_prompt.setdefault(ans["prompt_id"], []).append(ans)
    return answers_by_prompt


def run_with_retries(
    task: Dict[str, Any],
    get_model_fn: Callable[[str, Optional[str]], Any],
    shuffle_seed: int,
    verbose: bool,
    retries: int,
    retry_delay: float,
):
    last_exc: Optional[Exception] = None
    for attempt in range(retries):
        try:
            judge_model = get_model_fn(task["judge_key"], task["judge_model_name"])
            return judge_prompt_answers(
                prompt_id=task["prompt_id"],
                prompt_text=task["prompt_text"],
                answers=task["answers"],
                judge_model=judge_model,
                judge_name=task["judge_key"],
                shuffle_seed=shuffle_seed,
                verbose=verbose,
            )
        except Exception as exc:
            last_exc = exc
            if attempt < retries - 1:
                time.sleep(retry_delay)
    raise RuntimeError(f"Failed after {retries} attempts: {last_exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate failed judgments.")
    parser.add_argument(
        "--config", default="config.yaml", help="Path to config file (default: config.yaml)"
    )
    parser.add_argument(
        "--answers",
        default="experiments/exp2_mt_bench/data/answers/answers.json",
        help="Path to the master answers JSON (default: experiments/.../answers.json)",
    )
    parser.add_argument(
        "--judgments",
        default="experiments/exp2_mt_bench/data/judgments/judgments.json",
        help="Path to the judgments JSON file to repair.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output path. Defaults to overwriting --judgments.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Number of concurrent judge re-runs (default: 4).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose logging from judge function.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=4,
        help="How many times to retry a failed judgment before giving up (default: 1).",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=1.0,
        help="Seconds to wait between retry attempts (default: 1.0).",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    answers = load_json(args.answers)
    judgments = load_json(args.judgments)

    answers_by_prompt = build_answers_index(answers)
    shuffle_seed = config.get("judging", {}).get("shuffle_seed", 42)

    failed_entries = [
        (idx, entry)
        for idx, entry in enumerate(judgments)
        if isinstance(entry, dict) and "error" in entry
    ]

    if not failed_entries:
        print("No failed judgments found. Nothing to do.")
        return

    print(f"Found {len(failed_entries)} failed judgments. Regenerating...")

    model_factory = ModelFactory(config)
    model_cache: Dict[Tuple[str, Optional[str]], Any] = {}

    def get_model(judge_key: str, model_name_override: Optional[str]):
        cache_key = (judge_key, model_name_override)
        if cache_key not in model_cache:
            vendor, tier = judge_key.split("_", 1)
            model_cache[cache_key] = model_factory.get_model(
                vendor, tier, model_name_override=model_name_override
            )
        return model_cache[cache_key]

    tasks = []
    skipped = 0

    for idx, entry in failed_entries:
        prompt_id = entry.get("prompt_id")
        judge_key = entry.get("judge_model")
        if not prompt_id or not judge_key:
            skipped += 1
            continue

        prompt_answers = answers_by_prompt.get(prompt_id)
        if not prompt_answers:
            print(f"⚠ Skipping {prompt_id} - no answers found.")
            skipped += 1
            continue

        tasks.append(
            {
                "index": idx,
                "prompt_id": prompt_id,
                "judge_key": judge_key,
                "judge_model_name": entry.get("judge_model_name"),
                "answers": prompt_answers,
                "prompt_text": prompt_answers[0]["prompt_text"],
            }
        )

    if not tasks:
        print("No runnable tasks (likely due to missing prompt data).")
        return

    pbar = tqdm(total=len(tasks), desc="Regenerating judgments")

    ordered_results: List[Optional[Dict[str, Any]]] = [None] * len(tasks)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_index = {
            executor.submit(
                run_with_retries,
                task,
                get_model,
                shuffle_seed,
                args.verbose,
                args.retries,
                args.retry_delay,
            ): idx
            for idx, task in enumerate(tasks)
        }

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            task = tasks[idx]
            try:
                ordered_results[idx] = future.result()
            except Exception as e:
                ordered_results[idx] = {
                    "prompt_id": task["prompt_id"],
                    "judge_model": task["judge_key"],
                    "error": f"Regeneration failed: {e}",
                }
            finally:
                pbar.update(1)

    pbar.close()

    for idx, task in enumerate(tasks):
        if ordered_results[idx] is not None:
            judgments[task["index"]] = ordered_results[idx]

    if skipped:
        print(f"Skipped {skipped} entries due to missing data.")

    output_path = args.output or args.judgments
    save_json(judgments, output_path)
    print(f"Updated judgments written to {output_path}")


if __name__ == "__main__":
    main()
