#!/usr/bin/env python3
"""
Regenerate dubious answers (empty strings or API failures) in answers.json.

The script reuses the `generate_answer` helper from `utils/generate_answers.py`
to keep retry behavior identical to the main generation pipeline.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from tqdm import tqdm

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils import load_config, load_json, save_json
from src.models import ModelFactory
from src.generate_answers import generate_answer  # type: ignore


def regenerate_entry(model, prompt_text: str, retries: int) -> str:
    return generate_answer(model, prompt_text, retries=retries, retry_delay=45)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate dubious answers (empty or failed outputs)."
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )
    parser.add_argument(
        "--answers",
        default="experiments/exp2_mt_bench/data/answers/answers.json",
        help="Path to the answers JSON file to patch.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional destination. Defaults to in-place update of --answers.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Concurrent workers when regenerating (default: 4).",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retries per answer (default: 3).",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    answers: list[dict[str, Any]] = load_json(args.answers)

    dubious_indices = [
        idx for idx, answer in enumerate(answers) if "error" in answer and answer.get("error", "")
    ]

    if not dubious_indices:
        print("No dubious answers detected. Nothing to do.")
        return

    print(f"Found {len(dubious_indices)} dubious answers. Regenerating...")

    model_factory = ModelFactory(config)
    model_cache: dict[tuple[str, str, str], Any] = {}

    def get_model_instance(vendor: str, tier: str, model_name: str):
        key = (vendor, tier, model_name)
        if key not in model_cache:
            model_cache[key] = model_factory.get_model(
                vendor, tier, model_name_override=model_name
            )
        return model_cache[key]

    tasks = []
    for idx in dubious_indices:
        answer = answers[idx]
        vendor = answer["model_vendor"].lower()
        tier = answer["model_tier"].lower()
        model_name = answer.get("model_name")
        if not model_name:
            raise ValueError(f"Missing model_name for answer {answer['answer_id']}")
        tasks.append(
            {
                "index": idx,
                "prompt_text": answer["prompt_text"],
                "answer_id": answer["answer_id"],
                "model_key": f"{vendor}_{tier}",
                "model": get_model_instance(vendor, tier, model_name),
            }
        )

    pbar = tqdm(total=len(tasks), desc="Regenerating answers")
    failures = 0
    ordered_outputs = [None] * len(tasks)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_index = {
            executor.submit(
                regenerate_entry,
                task["model"],
                task["prompt_text"],
                args.retries,
            ): idx
            for idx, task in enumerate(tasks)
        }

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                ordered_outputs[idx] = future.result()
            except Exception as e:
                ordered_outputs[idx] = f"[ERROR: Failed to regenerate answer - {e}]"
                failures += 1
            finally:
                pbar.update(1)

    pbar.close()

    for idx, task in enumerate(tasks):
        new_answer = ordered_outputs[idx]
        if new_answer is None:
            failures += 1
            if "answer_text" in answers[task["index"]]:
                del answers[task["index"]]["answer_text"]
            # answers[task["index"]]["answer_text"] = "[ERROR: Failed to regenerate answer - Unknown error]"
            # continue
        elif isinstance(new_answer, dict) and "error" in new_answer:
            failures += 1
            if "answer_text" in answers[task["index"]]:
                del answers[task["index"]]["answer_text"]
            # answers[task["index"]]["answer_text"] = f"[ERROR: Failed to regenerate answer - {new_answer['error']}]"
        else:
            answers[task["index"]]["answer_text"] = new_answer
            if "error" in answers[task["index"]]:
                del answers[task["index"]]["error"]

    if failures:
        print(f"⚠ Failed to regenerate {failures} answers. See updated JSON for details.")
    else:
        print("✓ Successfully regenerated all dubious answers.")

    output_path = args.output or args.answers
    save_json(answers, output_path)
    print(f"Updated answers written to {output_path}")


if __name__ == "__main__":
    main()
