# Experiment 1: Blind Judge Evaluation

## Research Question
> **Does a judge show self-preference when answers are anonymous?**

## Setup
- **Answers**: Anonymized (A, B, C, D, E, F)
- **Prompts**: 60 mixed prompts across 6 categories
- **Hinting**: None (blind evaluation)

## Models Tested

### Answer Generators
| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | Haiku 4.5 | Sonnet 4.5 |
| GPT | GPT-5-mini | GPT-4.1 |
| Gemini | 2.5 Flash | 3 Pro |

### Judges
- `gemini_thinking` (Gemini 3 Pro)
- `claude_thinking` (Claude Sonnet 4.5)
- `gpt_thinking` (GPT-4.1 via OpenRouter)

## Results

| Judge | Claude Wins | GPT Wins | Gemini Wins | Self-Bias? |
|-------|-------------|----------|-------------|------------|
| Gemini | 60% | 20% | 20% | ❌ No |
| Claude | 60% | 20% | 20% | ❌ No |
| GPT | 20% | **80%** | 0% | ⚠️ **YES** |

## Key Finding
**GPT shows strong self-preference bias (80%)** while Gemini and Claude do not show self-bias.

## Files
- `config.yaml` - Model configuration used
- `prompts.json` - 60 test prompts
- `analysis.ipynb` - Analysis notebook
- `data/answers/` - Generated model answers
- `data/judgments/` - Judge evaluations
- `data/results/` - Visualizations and CSVs

## How to Reproduce
```bash
cd /path/to/LLM_Eval

# Generate answers
python src/generate_answers.py --config experiments/exp1_blind_judge/config.yaml --prompts experiments/exp1_blind_judge/prompts.json

# Judge answers
python src/judge_answers.py --config experiments/exp1_blind_judge/config.yaml --answers experiments/exp1_blind_judge/data/answers/answers_*.json --judges gemini_thinking claude_thinking gpt_thinking

# Analyze
jupyter notebook experiments/exp1_blind_judge/analysis.ipynb
```

