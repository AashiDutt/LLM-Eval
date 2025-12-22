# Quick Start Guide

Get your bias evaluation running in **5 minutes**!

## Prerequisites

- Python 3.9+
- API keys for Anthropic, OpenAI, and Google AI

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configure API Keys

Create `.env` file:
```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
```

**Get keys from:**
- Anthropic: https://console.anthropic.com/
- OpenAI: https://openai.com/api/pricing/
- Google AI: https://aistudio.google.com/app/apikey

## Run the Pipeline

```bash
# Step 1: Generate answers (5 prompts for quick test)
python src/generate_answers.py --limit 5

# Step 2: Judge answers (use exact filename from Step 1)
python src/judge_answers.py --answers data/answers/answers_YYYYMMDD_HHMMSS.json --judges gemini_thinking --limit 5

# Step 3: Analyze results
jupyter notebook analysis.ipynb
```

## Expected Output

### Step 1 Output:
```
Processing 5 prompts across 6 models
✓ Done! Answers saved to: data/answers/answers_20251208_103119.json
```

### Step 2 Output:
```
Judging 5 prompts with 1 judge(s)
✓ Done! Judgments saved to: data/judgments/judgments_20251208_103432.json
```

### Step 3 (Notebook):
- Top-1 preference rates by vendor
- Average scores by vendor/tier
- Statistical test results

## Cost Estimate

**Quick test (5 prompts):** ~$0.40
**Full experiment (60 prompts):** ~$7-10

## Troubleshooting

| Error | Solution |
|-------|----------|
| "API key not found" | Check `.env` file |
| "Module not found" | Run `pip install -r requirements.txt` |
| "unrecognized arguments" | Use exact filename, not wildcard `*` |

## Next Steps

- Run full experiment: `python src/generate_answers.py` (no --limit)
- See [README.md](README.md) for full documentation
