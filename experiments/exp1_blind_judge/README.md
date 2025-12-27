# Experiment 1: Blind Judge Evaluation

## Research Question
> **Does a judge show self-preference when answers are anonymous?**

## Setup
- **Answers**: Anonymized (A, B, C, D, E, F)
- **Prompts**: 10 mixed prompts across 6 categories
- **Hinting**: None (blind evaluation)

*Note: This experiment is a baby experiment that helped us gain intuition and decide the next steps of the project.*

## Models Tested

| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | Haiku 4.5 | Sonnet 4.5 |
| GPT | GPT-5-mini | GPT-5.2 |
| Gemini | 2.5 Flash | 3 Pro Preview |

### Judges
- `gemini_fast`, `gemini_thinking`
- `claude_fast`, `claude_thinking`
- `gpt_fast`, `gpt_thinking` 

## Results

We calculated the percentage of times each judge ranks each vendor's answers as Top-1 in blind evaluations where model identities are hidden. Each row represents a different judge model (using thinking-tier models only), and each column shows the win rate for that vendor's answers when evaluated by that judge. 

| Judge | Claude Wins | GPT Wins | Gemini Wins | Self-Bias? |
|-------|-------------|----------|-------------|------------|
| Gemini | 60% | 20% | 20% | No (20% for own) |
| Claude | 60% | 20% | 20% | No  |
| GPT | 20% | 80% | 0% | 60% |

- **Claude Wins / GPT Wins / Gemini Wins**: These represent the percentage of prompts where that vendor's answers were ranked #1 by the judge

- **Self-Bias**: This indicates whether the judge shows preference for its own vendor. It is calculated as the difference between the judge's self-preference rate and the average rate from other judges. 

## Key Findings

1. GPT shows strong self-preference bias (80% vs 20% from other judges i.e. +60% difference)
2. Claude answers are more preferred, however both Gemini and Claude judges ranked Claude #1 at 60%.
3. Gemini is impartial as it only ranked itself #1 at 20% (below expected 33% which we refer as our baseline for 3 model vendors)

<details>
<summary><b>Quick Start</b></summary>

```bash
cd /path/to/LLM_Eval

# Generate answers
python src/generate_answers.py --config experiments/exp1_blind_judge/config.yaml --prompts experiments/exp1_blind_judge/prompts.json

# Judge answers
python src/judge_answers.py --config experiments/exp1_blind_judge/config.yaml --answers experiments/exp1_blind_judge/data/answers/answers_*.json --judges gemini_thinking claude_thinking gpt_thinking

# Analyze
jupyter notebook experiments/exp1_blind_judge/analysis.ipynb
```
</details>

