#!/usr/bin/env python3
"""
Swap failed/empty answers in answers.json with regenerated ones from regenerated_answers.json.

Definition:
- "bad" answer_text: "" OR contains "[ERROR: Failed to generate answer"
- "good" answer_text: non-empty AND does NOT contain that substring

Usage:
  python swap_answers.py \
    --answers /path/to/answers.json \
    --regenerated /path/to/regenerated_answers.json \
    --out /path/to/answers.patched.json

Optionally, write in-place with a backup:
  python swap_answers.py --answers answers.json --regenerated regenerated_answers.json --inplace
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

ERROR_SUBSTR = "[ERROR: Failed to generate answer"


JSONType = dict[str, Any] | list[Any]


def is_bad_answer_text(text: Any) -> bool:
    if not isinstance(text, str):
        return True
    return text == "" or (ERROR_SUBSTR in text)


def is_good_answer_text(text: Any) -> bool:
    if not isinstance(text, str):
        return False
    return text != "" and (ERROR_SUBSTR not in text)


def load_json(path: Path) -> JSONType:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, obj: JSONType) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def iter_records(data: JSONType) -> list[dict[str, Any]]:
    """
    Supports:
      - list[dict] (your files look like this)
      - dict with top-level "answers" list (common variant)
    """
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("answers"), list):
        return [x for x in data["answers"] if isinstance(x, dict)]
    raise ValueError("Unsupported JSON shape. Expected a list of dicts, or a dict with an 'answers' list.")


def set_records(data: JSONType, new_records: list[dict[str, Any]]) -> JSONType:
    if isinstance(data, list):
        return new_records
    # dict with "answers"
    assert isinstance(data, dict)
    data = dict(data)  # shallow copy
    data["answers"] = new_records
    return data


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", type=Path, required=True, help="Path to answers.json")
    ap.add_argument("--regenerated", type=Path, required=True, help="Path to regenerated_answers.json")
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Where to write patched JSON. Required unless --inplace is set.",
    )
    ap.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite --answers in-place (creates a .bak backup).",
    )
    args = ap.parse_args()

    if not args.inplace and args.out is None:
        ap.error("Provide --out, or pass --inplace to overwrite answers.json.")

    answers_data = load_json(args.answers)
    regen_data = load_json(args.regenerated)

    answers = iter_records(answers_data)
    regen = iter_records(regen_data)

    regen_by_id: dict[str, dict[str, Any]] = {}
    for r in regen:
        aid = r.get("answer_id")
        if isinstance(aid, str):
            regen_by_id[aid] = r

    swapped = 0
    missing_regen = 0
    regen_not_good = 0

    new_answers: list[dict[str, Any]] = []
    for a in answers:
        aid = a.get("answer_id")
        a_text = a.get("answer_text", "")

        if not isinstance(aid, str):
            new_answers.append(a)
            continue

        if is_bad_answer_text(a_text):
            r = regen_by_id.get(aid)
            if r is None:
                missing_regen += 1
                new_answers.append(a)
                continue

            r_text = r.get("answer_text", "")
            if is_good_answer_text(r_text):
                # swap in the entire regenerated entry
                new_answers.append(r)
                swapped += 1
            else:
                regen_not_good += 1
                new_answers.append(a)
        else:
            new_answers.append(a)

    out_data = set_records(answers_data, new_answers)

    if args.inplace:
        backup_path = args.answers.with_suffix(args.answers.suffix + ".bak")
        shutil.copy2(args.answers, backup_path)
        dump_json(args.answers, out_data)
        print(f"Wrote patched answers in-place: {args.answers}")
        print(f"Backup saved to: {backup_path}")
    else:
        assert args.out is not None
        dump_json(args.out, out_data)
        print(f"Wrote patched answers to: {args.out}")

    print(f"Done. swapped={swapped}, missing_regen={missing_regen}, regen_not_good={regen_not_good}")


if __name__ == "__main__":
    main()
