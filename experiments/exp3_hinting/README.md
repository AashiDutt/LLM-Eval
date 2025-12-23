# Experiment 3: Hinting Effect

## Research Question
> **Does revealing model identities change judge behavior?**

## Benchmark: MT-Bench (Official)
- **Source**: [LMSYS FastChat](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge/data/mt_bench)
- **Paper**: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (Zheng et al., 2023)
- **Prompts**: 80 official MT-Bench questions (first turn only)
- **Obtained Data**:
  * [Answers](https://huggingface.co/datasets/sayakpaul/llm-bias-mt-bench/blob/main/experiment-2/answers_new.json)
  * [Judgments](https://huggingface.co/datasets/sayakpaul/llm-bias-mt-bench/tree/main/experiment-3)

## Setup
- **Answers**: Anonymized (A, B, C, D, E, F) - 6 models (2 per vendor × 3 vendors)
- **Prompts**: 80 MT-Bench style prompts
- **Hinting**: 4 modes (self, competitors, full, none)
- **Judgments per group**: 480 (80 prompts × 6 judges)
- **Total judgments**: 1,920 (480 × 4 groups)

## Categories (10 prompts each)

| Category | Domain | Example Task |
|----------|--------|--------------|
| Writing | Creative | Persuasive emails, stories, poems |
| Roleplay | Character | Acting as different personas |
| Reasoning | Logic | Puzzles, brain teasers |
| Math | Quantitative | Calculations, proofs |
| Coding | Technical | Algorithms, data structures |
| Extraction | Information | Parsing text, NER |
| STEM | Science | Explanations, concepts |
| Humanities | Liberal Arts | Philosophy, history, ethics |

## Models

### Answer Generators (from Exp 2)
| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | Haiku 4.5 | Sonnet 4.5 |
| GPT | GPT-5-mini | GPT-5.2 |
| Gemini | 2.5 Flash | 3 Pro Preview |

### Judges
- `gemini_fast`, `gemini_thinking`
- `claude_fast`, `claude_thinking`
- `gpt_fast`, `gpt_thinking`

## Design: Partial Hinting Control Groups

| Group | Hint Mode | What Judge Sees | Purpose |
|-------|-----------|-----------------|---------|
| **Group 1** | `self` | Only own model revealed | Self-knowledge effect |
| **Group 2** | `competitors` | Only competitor models revealed | Competitor awareness |
| **Group 3** | `full` | All models revealed | Full transparency |
| **Group 4** | `none` | No hints (blind) | Baseline control |

## Main Metrics Comparison

| Metric | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) | Best |
|--------|----------------|----------------------|----------------|-----------------|------|
| **Average Self-Bias** | 41.25% | 43.33% | 43.96% | 42.50% | Group 1 |
| **Deviation from Expected** | 13.06pp | 13.47pp | 10.63pp | 11.53pp | Group 3 |
| **Balance Score** | 15.50 | 14.96 | 13.10 | 14.07 | Group 3 |
| **Consistency** | 15.57 | 16.11 | 14.00 | 15.52 | Group 3 |

*Note: Lower values are better for all metrics. Expected self-bias = 33.33% (3 vendors, unbiased)*

## Vendor-Specific Self-Bias Rates

| Vendor | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) |
|--------|----------------|----------------------|----------------|-----------------|
| **Claude** | 25.6% | 36.2% | 34.4% | 30.0% |
| **GPT** | 62.5% | 65.6% | 63.7% | 64.4% |
| **Gemini** | 35.6% | 28.1% | 33.8% | 33.1% |

*Self-bias rate = percentage of times a judge ranks their own vendor #1*

## Domain-wise Best Group

| Category | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) | Best Group |
|----------|----------------|----------------------|----------------|-----------------|------------|
| Extraction | **31.7%** | 38.3% | 33.3% | 35.0% | **Group 1** |
| Humanities | **36.7%** | 38.3% | 36.7% | 36.7% | **Group 1** |
| Math | **46.7%** | 51.7% | 51.7% | 50.0% | **Group 1** |
| Reasoning | **41.7%** | 43.3% | 41.7% | 41.7% | **Group 1** |
| Writing | **38.3%** | 43.3% | 38.3% | 45.0% | **Group 1** |
| Coding | 43.3% | 43.3% | 45.0% | **41.7%** | **Group 4** |
| Roleplay | 55.0% | 55.0% | 61.7% | **53.3%** | **Group 4** |
| STEM | 36.7% | **33.3%** | 43.3% | 36.7% | **Group 2** |

*Best = lowest average self-bias across all vendors for that category*

## Goal-Based Recommendations

| Goal | Recommended Group | Rationale | Trade-offs |
|------|------------------|-----------|------------|
| **Benchmark Validity** | Group 4 (Blind) | Most defensible protocol; minimizes identity effects | Baseline self-bias (42.50%) |
| **Bias Mitigation** | Group 1 (Self) | Lowest average self-bias (41.25%); Claude shows self-awareness (25.6%) | Worse balance and consistency |
| **Stable/Balanced Selection** | Group 3 (Full) | Best balance score (13.10) and consistency (14.00); most even vendor distribution | Highest average self-bias (43.96%); least blind |
| **Avoid** | Group 2 (Competitors) | Highest average self-bias (43.33%); GPT bias peaks (65.6%) | Only use if studying bias amplification |

*Note: "33.33%" is a naive uniform baseline (3 vendors). Real-world "unbiased" rates can differ due to answer quality, prompt mix, and judge preference for style.*

## How to Run

```bash
cd /path/to/LLM_Eval

# Group 1: Self-hint
python src/judge_answers.py \
  --config experiments/exp3_hinting/config.yaml \
  --answers experiments/exp3_hinting/data/answers/answers.json \
  --output experiments/exp3_hinting/data/judgments/group1_self.json \
  --hint-mode self

# Group 2: Competitors-hint
python src/judge_answers.py \
  --config experiments/exp3_hinting/config.yaml \
  --answers experiments/exp3_hinting/data/answers/answers.json \
  --output experiments/exp3_hinting/data/judgments/group2_competitors.json \
  --hint-mode competitors

# Group 3: Full-hint
python src/judge_answers.py \
  --config experiments/exp3_hinting/config.yaml \
  --answers experiments/exp3_hinting/data/answers/answers.json \
  --output experiments/exp3_hinting/data/judgments/group3_full.json \
  --hint-mode full

# Group 4: Baseline (symlink to exp2)
ln -s ../../exp2_mt_bench/data/judgments/judgments_mt_bench.json \
  experiments/exp3_hinting/data/judgments/group4_blind.json
```

### Quick Test (5 prompts, 1 judge)

```bash
python src/judge_answers.py \
  --config experiments/exp3_hinting/config.yaml \
  --answers experiments/exp3_hinting/data/answers/answers.json \
  --output experiments/exp3_hinting/data/judgments/test_self.json \
  --hint-mode self \
  --judges gemini_fast \
  --limit 5
```
## Analyze
```bash
jupyter notebook experiments/exp3_hinting/analysis.ipynb
```
