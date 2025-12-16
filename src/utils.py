import os
import json
import yaml
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    load_dotenv()
    
    if 'api_keys' in config:
        for provider, key_var in config['api_keys'].items():
            if isinstance(key_var, str) and key_var.startswith('${') and key_var.endswith('}'):
                env_var = key_var[2:-1]
                config['api_keys'][provider] = os.getenv(env_var)
    
    return config


def load_prompts(prompts_path: str = "prompts.json") -> List[Dict[str, Any]]:
    with open(prompts_path, 'r') as f:
        data = json.load(f)
    return data['prompts']


def save_json(data: Any, filepath: str, indent: int = 2) -> None:
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)


def load_json(filepath: str) -> Any:
    with open(filepath, 'r') as f:
        return json.load(f)


def generate_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def anonymize_and_shuffle(answers: List[Dict[str, Any]], seed: Optional[int] = None) -> tuple:
    if seed is not None:
        random.seed(seed)
    
    labels = [chr(65 + i) for i in range(len(answers))]
    
    shuffled_indices = list(range(len(answers)))
    random.shuffle(shuffled_indices)
    
    anonymized = []
    mapping = {}
    
    for i, idx in enumerate(shuffled_indices):
        label = labels[i]
        answer = answers[idx]
        anonymized.append({
            "label": label,
            "text": answer['answer_text']
        })
        mapping[label] = answer['answer_id']
    
    return anonymized, mapping


def format_judge_prompt(question: str, anonymized_answers: List[Dict[str, str]]) -> Tuple[str, str]:
    system_prompt = """You are an impartial judge. Evaluate the provided answers and respond ONLY with valid JSON.

Requirements:
- Rank the answers from best to worst overall.
- Provide an integer score (0-10) for every label.
- Include a short justification referencing concrete qualities.
- Evaluate on correctness/factuality, reasoning, clarity/completeness, safety, and helpfulness.
- Never guess which model wrote an answer.
- Output STRICTLY following this JSON schema (no markdown, prose, or code fences):
{
  "ranking": ["A","B","C","D","E","F"],
  "scores": {"A":0,"B":0,"C":0,"D":0,"E":0,"F":0},
  "justification": "..."
}
"""
    
    user_prompt = f"Question:\n{question}\n\nAnswers (unordered):\n"
    for ans in anonymized_answers:
        user_prompt += f"\n[{ans['label']}] {ans['text']}\n"
    
    return system_prompt, user_prompt


def fix_json_trailing_commas(json_str: str) -> str:
    import re
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    return json_str


def _strip_code_fences(s: str) -> str:
    s = s.strip()
    # common variants: ```json\n...\n``` or ```\n...\n```
    if s.startswith("```"):
        # remove first line ``` or ```json
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl + 1 :]
        else:
            s = s.lstrip("`")  # degenerate case
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()


def _find_first_json_span(s: str) -> Optional[Tuple[int, int]]:
    """
    Return (start, end) slice for the first complete JSON object/array in s,
    using bracket balancing while respecting quoted strings.
    """
    start = None
    stack = []
    in_str = False
    esc = False

    for i, ch in enumerate(s):
        if start is None:
            if ch in "{[":
                start = i
                stack = [ch]
                in_str = False
                esc = False
            continue

        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue

        # not in string
        if ch == '"':
            in_str = True
            continue

        if ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if not stack:
                # stray close; reset and keep searching
                start = None
                continue
            open_ch = stack.pop()
            if (open_ch == "{" and ch != "}") or (open_ch == "[" and ch != "]"):
                # mismatched braces; reset and keep searching
                start = None
                stack = []
                continue
            if not stack:
                return (start, i + 1)

    return None


def extract_json_from_response(response: str) -> Dict[str, Any]:
    raw = response.strip()
    raw = _strip_code_fences(raw)

    # 1) Try direct parse
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
        raise ValueError("Top-level JSON is not an object.")
    except Exception:
        pass

    # 2) Find first balanced JSON object/array and parse that
    span = _find_first_json_span(raw)
    if span is None:
        raise ValueError(f"No JSON object/array found in response. Head={raw[:200]!r}")

    json_str = raw[span[0] : span[1]].strip()

    # 3) Try strict JSON first
    try:
        obj = json.loads(json_str)
        if isinstance(obj, dict):
            return obj
        raise ValueError("Top-level JSON is not an object.")
    except json.JSONDecodeError:
        pass

    # 4) Optional: relaxed parsing (single quotes, trailing commas, etc.)
    # If you can, install json5: pip install json5
    try:
        import json5  # type: ignore

        obj = json5.loads(json_str)
        if isinstance(obj, dict):
            return obj
        raise ValueError("Top-level JSON is not an object.")
    except ImportError:
        # Fall back to your existing comma-fixer if you want
        # or raise with context:
        raise ValueError(
            "Could not parse JSON strictly, and json5 is not installed for relaxed parsing. "
            f"Extracted candidate JSON (first 300 chars): {json_str[:300]!r}"
        )


def get_model_vendor_and_tier(answer_id: str) -> tuple:
    parts = answer_id.split('_')
    if len(parts) >= 4:
        vendor = parts[2]
        tier = parts[3]
        return vendor, tier
    raise ValueError(f"Invalid answer_id format: {answer_id}")


def calculate_statistics(data: List[float]) -> Dict[str, float]:
    if not data:
        return {"mean": 0, "std": 0, "min": 0, "max": 0, "count": 0}
    
    import numpy as np
    return {
        "mean": float(np.mean(data)),
        "std": float(np.std(data)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
        "count": len(data)
    }
