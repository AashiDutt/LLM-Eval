# LLM Judge Bias Evaluation Framework

A comprehensive framework to test whether AI judges show self-preference bias when evaluating answers from different LLMs.

## 🎯 Research Questions

1. **Self-Preference Bias**: Does a judge favor its own responses?
2. **Domain Effects**: Does bias vary by benchmark/task type?
3. **Hinting Effects**: Does revealing model names change judge behavior?
4. **Tier Preferences**: Do judges favor thinking-tier over fast-tier?
5. **Family Loyalty**: Does a judge favor its model family?

## 📁 Project Structure

```
LLM_Eval/
├── src/                          # Core framework code
│   ├── models.py                 # API wrappers (Claude, GPT via OpenRouter, Gemini)
│   ├── generate_answers.py       # Generate answers from all models
│   ├── judge_answers.py          # Blind judging system
│   ├── analysis.py               # Analysis functions
│   └── utils.py                  # Utilities
├── experiments/                  # Individual experiments
│   └── exp1_blind_judge/         # ✅ Completed
│       ├── README.md
│       ├── config.yaml
│       ├── prompts.json
│       ├── analysis.ipynb
│       └── data/
├── requirements.txt
└── README.md
```

## 🧪 Experiments

| # | Experiment | Question | Status |
|---|------------|----------|--------|
| 1 | [Blind Judge](experiments/exp1_blind_judge/) | Self-preference with anonymous answers? | ✅ Done |
| 2 | Benchmark Analysis | Does bias vary by domain? | ✅ Done |
| 3 | Hinting Effect | Does revealing model names matter? | ✅ Done|
| 4 | Fast vs Thinking | Tier preference patterns? | ✅ Done |
| 5 | Family Loyalty | Same-vendor preference? | ✅ Done |

## 🚀 Quick Start

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure API Keys
Create `.env` file:
```bash
ANTHROPIC_API_KEY=your_key
OPENROUTER_API_KEY=your_key
GOOGLE_API_KEY=your_key
```

### Run an Experiment
```bash
# Generate answers
python src/generate_answers.py \
  --config experiments/exp1_blind_judge/config.yaml \
  --prompts experiments/exp1_blind_judge/prompts.json \
  --output experiments/exp1_blind_judge/data/answers/answers.json

# Judge answers
python src/judge_answers.py \
  --config experiments/exp1_blind_judge/config.yaml \
  --answers experiments/exp1_blind_judge/data/answers/answers.json \
  --judges gemini_thinking claude_thinking gpt_thinking

# Analyze
jupyter notebook experiments/exp1_blind_judge/analysis.ipynb
```

## 🔑 Key Finding (Experiment 1)

| Judge | Picks Own Vendor | Others Pick Same | Self-Bias? |
|-------|------------------|------------------|------------|
| Gemini | 20% | 20% (Claude) | ❌ No |
| Claude | 60% | 60% (Gemini agrees) | ❌ No |
| **GPT** | **80%** | 20% | ⚠️ **+60% bias** |

**GPT shows strong self-preference bias** (+60% vs other judges).  
Claude's 60% win rate is due to quality, not bias (Gemini judge agrees).

## 📊 Models Supported

| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | Haiku 4.5 | Sonnet 4.5 |
| GPT | GPT-5-mini | GPT-5.2 |
| Gemini | 2.5 Flash | 3 Pro |

## 📄 License

MIT License
