#!/usr/bin/env python3
"""
Collate judgments_2.json with regenerated_judgments_2.json.

Rule:
- Identify an entry by (prompt_id, judge_model)
- If an entry in judgments_2.json has an "error" key (truthy or present),
  and regenerated has the same key AND regenerated does NOT have "error",
  then replace the original entry with the regenerated one.

Optionally:
- You can also choose to append regenerated entries that don't exist in the original
  via --add-missing.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def key_of(entry: dict[str, Any]) -> tuple[str, str] | None:
    pid = entry.get("prompt_id")
    jm = entry.get("judge_model")
    if isinstance(pid, str) and isinstance(jm, str):
        return (pid, jm)
    return None


def has_error(entry: dict[str, Any]) -> bool:
    # Treat presence of the key as error, even if it's an empty string.
    return "error" in entry and entry.get("error") is not None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgments", type=Path, required=True, help="Path to judgments_2.json")
    ap.add_argument("--regenerated", type=Path, required=True, help="Path to regenerated_judgments_2.json")
    ap.add_argument("--out", type=Path, default=None, help="Output path (required unless --inplace).")
    ap.add_argument("--inplace", action="store_true", help="Overwrite --judgments in place (creates .bak).")
    ap.add_argument(
        "--add-missing",
        action="store_true",
        help="Also append regenerated non-error entries missing from judgments_2.json.",
    )
    args = ap.parse_args()

    if not args.inplace and args.out is None:
        ap.error("Provide --out, or pass --inplace to overwrite judgments_2.json.")

    base = load_json(args.judgments)
    regen = load_json(args.regenerated)

    if not isinstance(base, list) or not isinstance(regen, list):
        raise ValueError("Expected both JSON files to be top-level lists of objects.")

    regen_good: dict[tuple[str, str], dict[str, Any]] = {}
    for r in regen:
        if not isinstance(r, dict):
            continue
        k = key_of(r)
        if k is None:
            continue
        if not has_error(r):
            regen_good[k] = r

    replaced = 0
    no_regen_match = 0
    regen_still_bad = 0
    kept_ok = 0

    seen_keys = set()

    out_list: list[dict[str, Any]] = []
    for e in base:
        if not isinstance(e, dict):
            # preserve non-dict items as-is (rare)
            out_list.append(e)
            continue

        k = key_of(e)
        if k is not None:
            seen_keys.add(k)

        if has_error(e):
            if k is None:
                out_list.append(e)
                continue

            r = regen_good.get(k)
            if r is None:
                # either missing entirely, or regenerated also had error
                # differentiate for logging:
                if any(isinstance(x, dict) and key_of(x) == k for x in regen):
                    regen_still_bad += 1
                else:
                    no_regen_match += 1
                out_list.append(e)
            else:
                out_list.append(r)
                replaced += 1
        else:
            out_list.append(e)
            kept_ok += 1

    added = 0
    if args.add_missing:
        for k, r in regen_good.items():
            if k not in seen_keys:
                out_list.append(r)
                added += 1

    if args.inplace:
        backup = args.judgments.with_suffix(args.judgments.suffix + ".bak")
        shutil.copy2(args.judgments, backup)
        dump_json(args.judgments, out_list)
        print(f"Wrote merged judgments in-place: {args.judgments}")
        print(f"Backup saved to: {backup}")
    else:
        assert args.out is not None
        dump_json(args.out, out_list)
        print(f"Wrote merged judgments to: {args.out}")

    print(
        "Done. "
        f"replaced={replaced}, kept_ok={kept_ok}, "
        f"no_regen_match={no_regen_match}, regen_still_bad={regen_still_bad}, added={added}"
    )


if __name__ == "__main__":
    main()
