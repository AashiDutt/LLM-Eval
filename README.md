# LLMs as Judges: Measuring Bias, Hinting Effects, and Tier Preferences

A comprehensive framework to test whether AI judges show self-preference bias when evaluating answers from different models. We take the MT-Bench benchmark to conduct our analyses but we believe it's extensible to
other frameworks.

## Research Questions

1. **Self-Preference Bias**: Does a judge favor its own responses?
2. **Domain Effects**: Does bias vary by benchmark/task type?
3. **Hinting Effects**: Does revealing model names change judge behavior?
4. **Tier Preferences**: Do judges favor thinking-tier over fast-tier?
5. **Family Loyalty**: Does a judge favor its model family?

## Models Supported

| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | Haiku 4.5 | Sonnet 4.5 |
| GPT | GPT-5-mini | GPT-5.2 |
| Gemini | 2.5 Flash | 3 Pro Preview |

## Project Structure

```
LLM_Eval/
├── src/                          # Core framework code
│   ├── models.py                 # API wrappers (Claude, GPT via OpenRouter, Gemini)
│   ├── generate_answers.py       # Generate answers from all models
│   ├── judge_answers.py          # Blind judging system
│   ├── analysis.py               # Analysis functions
│   └── utils.py                  # Utilities
├── experiments/                  # Individual experiments
│   ├── exp1_blind_judge/         # Experiment 1: Blind judge evaluation
│   ├── exp2_mt_bench/            # Experiment 2: MT-Bench domain analysis
│   └── exp3_hinting/             # Experiment 3: Hinting effect analysis
├── utils/
│   ├── regenerate_dubious_answers.py         # Regenerate answers that are dubious.
│   ├── regenerate_failed_judgments.py        # Regenerate judgments that led to errors.
├── requirements.txt
└── README.md
```

## Experiments

| # | Experiment | Question | Key Finding |
|---|------------|----------|--------|
| 1 | [Blind Judge](experiments/exp1_blind_judge/) | Self-preference with anonymous answers? | GPT shows +60% self-bias |
| 2 | [MT-Bench Analysis](experiments/exp2_mt_bench/) | Does bias vary by domain?  | GPT bias strongest in creative domains (90%) |
| 3 | [Hinting Effect](experiments/exp3_hinting/) | Does revealing model names matter? | Hinting has minimal impact (<2pp change) |
| 4 | Fast vs Thinking | Tier preference patterns?  | All vendors prefer thinking-tier |
| 5 | Family Loyalty | Same-vendor preference? | Cross-vendor patterns identified |

**Notes**:

* Experiment 1 is a baby experiment that helped us gain intuition and decide the next steps of the project.
* Experiment 3 was conducted with MT-Bench.
* We have used *33.33%* as a naive uniform baseline (3 vendors) for all experiments. Please note that real-world "unbiased" rates can differ due to answer quality, prompt mix, and judge preference.

<details>
<summary><b>Quick Start</b></summary>

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
OPENAI_API_KEY=your_key
GOOGLE_API_KEY=your_key
```

### Run Experiment 1

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

### Run Experiment 2

```bash
# Generate answers
python src/generate_answers.py \
  --config experiments/exp2_mt_bench/config.yaml \
  --prompts experiments/exp2_mt_bench/prompts.json \
  --output experiments/exp2_mt_bench/data/answers/answers.json

# Judge answers 
python src/judge_answers.py \
  --config experiments/exp2_mt_bench/config.yaml \
  --answers experiments/exp2_mt_bench/data/answers/answers.json \
  --output experiments/exp2_mt_bench/data/judgments/judgments.json

# Analyze
jupyter notebook experiments/exp2_mt_bench/analysis.ipynb
```

### Run Experiment 3: Hinting Effect

```bash
# Run all hinting groups
python src/judge_answers.py \
  --config experiments/exp3_hinting/config.yaml \
  --answers experiments/exp3_hinting/data/answers/answers.json \
  --output experiments/exp3_hinting/data/judgments/group1_self.json \
  --hint-mode self

# Analyze all groups
jupyter notebook experiments/exp3_hinting/analysis.ipynb
```
</details>

<details>
<summary><b>Experiment-wise Findings</b></summary>

### Experiment 1: Blind Judge

We compared how often each judge ranks its own vendor's answers as #1 versus how often other judges rank that same vendor as #1. The comparison helps distinguish between self-bias and genuine quality advantages. We used each vendor's thinking-tier as judge model only.

| Judge | Picks Own Vendor | Others Pick Same | Self-Bias? |
|-------|------------------|------------------|------------|
| Gemini | 20% | 10% (avg of Claude & GPT) | No |
| Claude | 60% | 40% (avg of Gemini & GPT) | No |
| GPT | 80% | 20% (avg of Claude & Gemini) | Yes, ~60% bias |

> NOTE:

GPT shows strong self-preference bias (+60% vs other judges).  
Claude's 60% win rate is due to quality, not bias (Gemini judge agrees).

### Experiment 2: MT-Bench Domain Analysis

We evaluated self-bias patterns across 8 domains using the MT-Bench benchmark (80 prompts). All 6 judges (fast and thinking tiers for each vendor) evaluated anonymized answers in blind conditions. Results are aggregated across fast and thinking tiers for each vendor family.

- **GPT self-bias**: 70% overall, strongest in Writing (90%) and Roleplay (85%)
- **Claude**: Least biased (~32.5%), maintains impartiality across domains
- **Gemini**: Shows bias in Math (80%) and Reasoning (60%) - its core strengths
- **Domain variation**: Bias patterns vary significantly by task type

### Experiment 3: Hinting Effect (with MT-Bench)

We tested whether revealing model identities to judges affects their bias by comparing 4 hinting groups: self-only, competitors-only, full transparency, and blind baseline. Using the same MT-Bench setup as Experiment 2, all 6 judges (aggregated across fast and thinking tiers) evaluated answers under different hinting conditions.

- **Overall finding**: Hinting has minimal impact (<2pp change from baseline)
- **Group 1 (Self)**: Lowest average self-bias (41.25%)
- **Group 3 (Full)**: Best balance and consistency (most fair overall)
- **GPT**: Persistent high bias (62-66%) regardless of hinting condition
- **Claude**: Shows self-awareness when identity revealed (25.6% self-bias)
- **Recommendation**: Use Group 3 (Full transparency) for best balance and fairness

</details>

## Acknowledgment

<div align="center">
  <img src="assets/google.png" alt="Google" height="60" style="margin-right: 20px;">
  <img src="assets/hf-logo.png" alt="Hugging Face" height="60">
</div>

Developed during Google's ML Developer Programs AI Sprint 2025 H2, this project benefited from generous GCP credits that facilitated its completion. We express our gratitude to the MLDP team for the support provided.
Sayak acknowledges the support he received from Hugging Face in terms of the API credits.

## 📄 License

MIT License
