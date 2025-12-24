import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils import load_config, load_prompts, load_json, format_judge_prompt, anonymize_and_shuffle
from src.models import ModelFactory
from src.judge_answers import JudgmentSchema


def select_prompt(prompts: list[dict], prompt_id: Optional[str], prompt_index: int) -> dict:
    if prompt_id:
        for prompt in prompts:
            if prompt.get("id") == prompt_id:
                return prompt
        raise ValueError(f"Prompt with id '{prompt_id}' not found in prompts file.")

    if not prompts:
        raise ValueError("Prompts file is empty.")

    if prompt_index < 0 or prompt_index >= len(prompts):
        raise IndexError(f"prompt_index {prompt_index} out of range (0-{len(prompts) - 1}).")

    return prompts[prompt_index]


def main():
    parser = argparse.ArgumentParser(description="Generate a single model response for a chosen prompt.")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file.")
    parser.add_argument("--prompts", type=str, required=True, help="Path to prompts JSON.")
    parser.add_argument("--prompt-id", type=str, default=None, help="Specific prompt id to run.")
    parser.add_argument("--prompt-index", type=int, default=0, help="Prompt index if id not provided.")
    parser.add_argument("--vendor", type=str, required=True, choices=["gpt", "gemini", "claude"], help="Model vendor.")
    parser.add_argument("--tier", type=str, required=True, choices=["fast", "thinking"], help="Model tier.")
    parser.add_argument(
        "--use-response-model", action="store_true", help="Request structured output using the JudgmentSchema."
    )

    args = parser.parse_args()

    config = load_config(args.config)
    system_prompt = None
    if "prompts" in args.prompts:
        prompts = load_prompts(args.prompts)
        prompt = select_prompt(prompts, args.prompt_id, args.prompt_index)
        prompt_text = prompt.get("text") or prompt.get("prompt") or ""
    elif "answers" in args.prompts:
        answers = load_json(args.prompts)
        answers_by_prompt = {}
        for answer in answers:
            prompt_id = answer["prompt_id"]
            if prompt_id not in answers_by_prompt:
                answers_by_prompt[prompt_id] = []
            answers_by_prompt[prompt_id].append(answer)
        for prompt_id, prompt_answers in answers_by_prompt.items():
            prompt_text = prompt_answers[0]["prompt_text"]
            answers = prompt_answers
            break

        anonymized, _ = anonymize_and_shuffle(answers, seed=32)
        system_prompt, prompt_text = format_judge_prompt(prompt_text, anonymized)
    else:
        raise

    if not prompt_text:
        raise ValueError("Selected prompt has no 'text' field.")

    model_factory = ModelFactory(config)
    model = model_factory.get_model(args.vendor, args.tier)

    response_model = JudgmentSchema if args.use_response_model else None

    response = model.generate(prompt_text, system_prompt=system_prompt, response_model=response_model)

    if isinstance(response, BaseModel):
        output = response.model_dump()
    elif isinstance(response, dict):
        output = response
    else:
        output = {"raw": str(response)}

    print(
        json.dumps(
            {
                "prompt_id": prompt.get("id") if system_prompt is None else prompt_id,
                "vendor": args.vendor,
                "tier": args.tier,
                "use_response_model": args.use_response_model,
                "output": output,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

# from pydantic import BaseModel
# import anthropic

# client = anthropic.Anthropic()

# class ContactInfo(BaseModel):
#     name: str
#     email: str
#     plan_interest: str
#     demo_requested: bool

# response = client.beta.messages.parse(
#     model="claude-sonnet-4-5",
#     max_tokens=2048,
#     # system="You are a seasoned data scientist at a Fortune 500 company.",
#     system="",
#     betas=["structured-outputs-2025-11-13"],
#     temperature=0.5,
#     messages=[
#         {
#             "role": "user",
#             "content": "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
#         }
#     ],
#     output_format=ContactInfo,
# )
# print(f"{response.parsed_output=}")


# import anthropic

# client = anthropic.Anthropic()

# response = client.messages.create(
#     model="claude-sonnet-4-5",
#     max_tokens=2048,
#     # system="You are a seasoned data scientist at a Fortune 500 company.", # <-- role prompt
#     system=None,
#     messages=[
#         {
#             "role": "user",
#             "content": "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
#         }
#     ],
#     temperature=0.5,
# )

# print(f"{response.content[0].text=}")
