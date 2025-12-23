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

## Available Data 

| Asset | Source | Description|
|-------|--------|--------|
| Answers | `experiments/exp3_hinting/data/answers/answers_mt_bench.json` | Answers from all models |
| Group 1 Judgments | `experiments/exp3_hinting/data/judgments/judgments_group1.json` | Judgments with self-hints |
| Group 2 Judgments | `experiments/exp3_hinting/data/judgments/judgments_group2.json` | Judgments with competitor-hints | 
| Group 3 Judgments | `experiments/exp3_hinting/data/judgments/judgments_group3.json` | Judgments with full hints | 
| Group 4 Judgments | `experiments/exp3_hinting/data/judgments/judgments_group4.json` | Baseline blind judgments | 
| All groups analysis |  `experiments/exp3_hinting/analysis.ipynb`| Cross-group comparison |

## Hypotheses

1. **Self-hint increases self-bias**: Judges favor own model more when they know which answer is theirs
2. **Competitor-hint reduces self-bias**: Knowing competitors but not self leads to fairer evaluation
3. **Full transparency**: May increase or decrease bias depending on model


## Results

### 1. Comprehensive Comparison: All 4 Hinting Groups

#### Main Metrics Comparison

| Metric | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) | Best |
|--------|----------------|----------------------|----------------|-----------------|------|
| **Average Self-Bias** | 41.25% | 43.33% | 43.96% | 42.50% | Group 1 |
| **Deviation from Expected** | 13.06pp | 13.47pp | 10.63pp | 11.53pp | Group 3 |
| **Balance Score** | 15.50 | 14.96 | 13.10 | 14.07 | Group 3 |
| **Consistency** | 15.57 | 16.11 | 14.00 | 15.52 | Group 3 |

*Note: Lower values are better for all metrics. Expected self-bias = 33.33% (3 vendors, unbiased)*

#### Vendor-Specific Self-Bias Rates

| Vendor | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) |
|--------|----------------|----------------------|----------------|-----------------|
| **Claude** | 25.6% | 36.2% | 34.4% | 30.0% |
| **GPT** | 62.5% | 65.6% | 63.7% | 64.4% |
| **Gemini** | 35.6% | 28.1% | 33.8% | 33.1% |

*Self-bias rate = percentage of times a judge ranks their own vendor #1*

#### Top-Vendor Distribution

| Vendor | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) |
|--------|----------------|----------------------|----------------|-----------------|
| **Claude** | 23.5% | 27.1% | 26.5% | 25.2% |
| **GPT** | 55.2% | 54.0% | 51.7% | 53.1% |
| **Gemini** | 21.2% | 19.0% | 21.9% | 21.7% |

*Percentage of times each vendor's answers are ranked #1 overall*


### 2. Overall Ranking

| Rank | Group | Key Strength |
|------|-------|--------------|
| 1 | Group 1 (Self) | Lowest average self-bias (41.25%) |
| 2 | Group 4 (Blind) | Baseline control |
| 3 | Group 2 (Competitors) | Moderate performance |
| 4 | Group 3 (Full) | Best balance & consistency |

---

## Key Findings 🔎

### Overall Hinting Effect

1. **Hinting has minimal impact on self-bias**
   - All hinting modes show minimal change from baseline (<2pp)
   - Group 1 (Self): -1.25pp from baseline
   - Group 2 (Competitors): +0.83pp from baseline
   - Group 3 (Full): +1.46pp from baseline
   - **Conclusion**: Revealing model identities does not significantly reduce or increase overall self-bias

2. **Group 1 (Self) performs best on average self-bias**
   - Lowest average self-bias: 41.25% (vs 42.50% baseline)
   - Claude shows lowest self-bias when their identity is revealed (25.6%)
   - GPT remains highly biased (62.5%) even when only their identity is revealed
   - **Insight**: Self-awareness may help Claude be more impartial, but GPT's bias persists

3. **Group 3 (Full) has best balance and consistency**
   - Best balance score: 13.10 (most balanced vendor distribution)
   - Best consistency: 14.00 (most consistent across judges)
   - Lowest deviation from expected: 10.63pp
   - **Insight**: Full transparency produces the most balanced and consistent judgments, despite slightly higher average self-bias

### Vendor-Specific Patterns

#### Claude: Self-Awareness Effect

- **Group 1 (Self)**: 25.6% self-bias (lowest across all groups)
- **Group 4 (Blind)**: 30.0% self-bias
- **Change**: -4.4pp when Claude knows their own identity
- **Interpretation**: Claude shows **self-awareness** - when they know which answer is theirs, they become more impartial, potentially avoiding self-favoritism

#### GPT: Persistent High Bias

- **Self-bias range**: 62.5% - 65.6% across all groups
- **Group 1 (Self)**: 62.5% (lowest, but still very high)
- **Group 2 (Competitors)**: 65.6% (highest)
- **Change from baseline**: Minimal (<2pp)
- **Interpretation**: GPT shows **systematic high self-bias** regardless of hinting condition. No hinting mode significantly reduces GPT's strong self-preference.

#### Gemini: Moderate and Variable

- **Self-bias range**: 28.1% - 35.6% across all groups
- **Group 2 (Competitors)**: 28.1% (lowest - competitors hint helps)
- **Group 1 (Self)**: 35.6% (highest)
- **Interpretation**: Gemini's bias is moderate and **responsive to hinting conditions**, showing the most variation across groups

### Cross-Judge Comparison

#### Group 1 (Self) - Judges see only their own model

| Judge | Claude | Gemini | GPT |
|-------|--------|--------|-----|
| claude_fast | **32.5%** | 13.8% | 53.8% |
| claude_thinking | **40.0%** | 18.8% | 41.3% |
| gemini_fast | 25.0% | **30.0%** | 45.0% |
| gemini_thinking | 21.3% | **26.3%** | 52.5% |
| gpt_fast | 23.8% | 17.5% | **58.8%** |
| gpt_thinking | 20.0% | 7.5% | **72.5%** |

**Key observation**: GPT thinking tier shows highest self-bias (72.5%) when they know their own identity.

#### Group 3 (Full) - All models revealed

| Judge | Claude | Gemini | GPT |
|-------|--------|--------|-----|
| claude_fast | **34.4%** | 15.0% | 50.6% |
| claude_thinking | **40.0%** | 20.0% | 40.0% |
| gemini_fast | 26.3% | **30.0%** | 43.8% |
| gemini_thinking | 21.3% | **26.3%** | 52.5% |
| gpt_fast | 23.8% | 17.5% | **58.8%** |
| gpt_thinking | 20.0% | 7.5% | **72.5%** |

**Key observation**: Full transparency produces more balanced selections, with GPT still dominating but less so than in other conditions.

### Top-Vendor Distribution Insights

1. **GPT dominates across all conditions**
   - GPT answers ranked #1: 51.7% - 55.2% across all groups
   - This dominance persists regardless of hinting
   - **Interpretation**: GPT answers may genuinely be higher quality, OR judges consistently favor GPT regardless of bias

2. **Claude and Gemini are under-selected**
   - Claude: 23.5% - 27.1% (below expected 33.3%)
   - Gemini: 19.0% - 21.9% (below expected 33.3%)
   - **Interpretation**: Either GPT answers are genuinely better, or there's systematic bias favoring GPT across all judges

3. **Group 3 (Full) shows most balanced distribution**
   - GPT: 51.7% (lowest across groups)
   - Claude: 26.5% (closer to expected)
   - Gemini: 21.9% (closer to expected)
   - **Interpretation**: Full transparency may reduce extreme preferences

---

## Hypotheses Evaluation

| Hypothesis | Result | Evidence |
|------------|--------|----------|
| Self-hint increases self-bias | ❌ **Rejected** | Group 1 shows -1.25pp from baseline (decrease) |
| Competitor-hint reduces self-bias | ⚠️ **Partially supported** | Group 2 shows +0.83pp (minimal change) |
| Full transparency reduces bias | ❌ **Rejected** | Group 3 shows +1.46pp (increase) |
| Hinting significantly affects bias | ❌ **Rejected** | All changes <2pp (minimal impact) |

**Key Finding**: None of the hinting modes significantly reduce self-bias. The effect of revealing model identities is minimal (<2pp change), suggesting that **judge bias is robust to hinting interventions**.

---

## Recommendations

1. **Use Group 3 (Full) - Full Transparency**
   - Best balance score (13.10) and consistency (14.00)
   - Most balanced vendor distribution
   - Transparent process (all models revealed)
   - Small trade-off in average self-bias is acceptable for better overall fairness

2. **Alternative: Use Group 1 (Self) if minimizing self-bias is priority**
   - Lowest average self-bias (41.25%)
   - Claude shows self-awareness effect (25.6% self-bias)
   - However, worse balance and consistency than Group 3

3. **Consider vendor-specific strategies**
   - Claude: Self-hint may help (25.6% vs 30.0% baseline)
   - GPT: No hinting mode significantly reduces bias (62-66% across all groups)
   - Gemini: Competitors hint may help (28.1% vs 33.1% baseline)


## How to Run All Groups (1-3)

```bash
cd /path/to/LLM_Eval

# Group 1: Self-hint (judges see only their own model revealed)
python src/judge_answers.py \
  --config experiments/exp3_hinting/config.yaml \
  --answers experiments/exp3_hinting/data/answers/answers.json \
  --output experiments/exp3_hinting/data/judgments/group1_self.json \
  --hint-mode self

# Group 2: Competitors-hint (judges see all except their own model)
python src/judge_answers.py \
  --config experiments/exp3_hinting/config.yaml \
  --answers experiments/exp3_hinting/data/answers/answers.json \
  --output experiments/exp3_hinting/data/judgments/group2_competitors.json \
  --hint-mode competitors

# Group 3: Full-hint (all models revealed)
python src/judge_answers.py \
  --config experiments/exp3_hinting/config.yaml \
  --answers experiments/exp3_hinting/data/answers/answers.json \
  --output experiments/exp3_hinting/data/judgments/group3_full.json \
  --hint-mode full

# Group 4: Baseline (already have from exp2)
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
