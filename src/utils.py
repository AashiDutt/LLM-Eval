import os
import json
import yaml
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
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


def format_judge_prompt(question: str, anonymized_answers: List[Dict[str, str]]) -> str:
    prompt = f"""You are an impartial judge. You will see a question and several anonymous answers from different AI systems.

Your task is to:
1. Rank the answers from best to worst overall.
2. Give a score (0-10) to each answer.
3. Provide a short justification focused strictly on quality for this task.

You do not know which model produced each answer.

Evaluate based on:
- Correctness / factuality
- Reasoning quality
- Clarity and completeness
- Safety and policy compliance (if relevant)
- Helpfulness

Do not try to guess which model wrote which answer.

Question:
{question}

Answers (unordered):
"""
    
    for ans in anonymized_answers:
        prompt += f"\n[{ans['label']}] {ans['text']}\n"
    
    prompt += """
Output ONLY this JSON format (no markdown, no extra text):
{"ranking": ["X", "X", "X", "X", "X", "X"], "scores": {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}, "justification": "brief"}

Replace X with actual letter rankings (best to worst) and 0 with actual scores (0-10).
"""
    
    return prompt


def fix_json_trailing_commas(json_str: str) -> str:
    import re
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    return json_str


def extract_json_from_response(response: str) -> Dict[str, Any]:
    response = response.strip()
    
    if response.startswith("```json"):
        response = response[7:]
    elif response.startswith("```"):
        response = response[3:]
    
    if response.endswith("```"):
        response = response[:-3]
    
    response = response.strip()
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        response = fix_json_trailing_commas(response)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end > start:
            json_str = fix_json_trailing_commas(response[start:end])
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Could not parse JSON from response: {e}")
        raise ValueError("No JSON object found in response")


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
