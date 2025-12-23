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


### 2. Ranking by Metric

**Ranked by Average Self-Bias (Lower = Better)**

| Rank | Group | Avg Self-Bias | What this means |
|---:|---|---:|---|
| 1 | Group 1 (Self-only hint) | 41.25% | Minimizes self-preference the most |
| 2 | Group 4 (No hints / Blind) | 42.50% | Clean baseline; slightly higher self-bias |
| 3 | Group 2 (Competitors-only) | 43.33% | Worsens self-bias overall |
| 4 | Group 3 (Full hints) | 43.96% | Highest self-bias (worst by this metric) |


**Ranked by Stability & Balance (Lower balance score + lower winner drift = Better)**

| Rank | Group | Key Strength | Why |
|---:|---|---|---|
| 1 | Group 3 (Full hints) | Most stable  | Lowest winner drift; most even selection profile |
| 2 | Group 4 (No hints / Blind) | Best scientific control | No identity leakage; stable baseline |
| 3 | Group 1 (Self-only hint) | Bias mitigation | Reduces self-bias but causes larger winner swings |
| 4 | Group 2 (Competitors-only) | — | Most disruptive; amplifies bias in some judges |


**Note**: Rankings differ by metric. See "Recommendations" section for goal-based guidance.

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

### Domain-wise Breakdown: Which Group Performs Best Per Category?

#### Overall Self-Bias by Category (Average Across All Vendors)

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

**Key observations (from self-bias only):**
- **Group 1 (Self-only hint)** has the lowest self-bias in **5/8 categories**: Extraction, Humanities, Math, Reasoning, Writing.
- **Group 4 (Blind)** is best for **Coding** and **Roleplay**, suggesting identity-free judging reduces bias in more subjective/creative tasks.
- **Group 2 (Competitors-only)** is best only in **STEM**, and is otherwise not consistently bias-reducing.
- **Group 3 (Full hints)** does **not** minimize self-bias in any category in this run.

---

## Hypotheses Evaluation

| Hypothesis | Result | Evidence |
|------------|--------|----------|
| Self-hint increases self-bias | ❌ **Rejected** | Group 1 shows -1.25pp from baseline (decrease) |
| Competitor-hint reduces self-bias | ⚠️ **Partially supported** | Group 2 shows +0.83pp (minimal change) |
| Full transparency reduces bias | ❌ **Rejected** | Group 3 shows +1.46pp (increase) |
| Hinting significantly affects bias | ❌ **Rejected** | All changes <2pp (minimal impact) |

**Key Finding**: None of the hinting modes significantly reduce self-bias. The effect of revealing model identities is minimal (<2pp change), suggesting that **judge bias is robust to hinting interventions**.

### Summary

1. **Group 1 (Self)**: Best for bias minimization
   - Lowest average self-bias (41.25%)
   - Claude shows self-awareness (25.6% self-bias)
   - Trade-off: Worse balance and consistency

2. **Group 2 (Competitors)**: Worst overall performance
   - Highest average self-bias (43.33%)
   - GPT self-bias peaks here (65.6%)
   - Avoid unless studying bias amplification

3. **Group 3 (Full)**: Best for balance and consistency
   - Best balance score (13.10) and consistency (14.00)
   - Most balanced vendor distribution
   - Trade-off: Highest average self-bias (43.96%) and least blind

4. **Group 4 (Blind)**: Best for benchmark validity
   - Most defensible protocol (minimizes identity effects)
   - Baseline control (42.50% self-bias)
   - Recommended for published results

---

### Practical Bottom Line

#### For Leaderboard Claims
- **Primary setting**: Use **Group 4 (Blind)** as the clean protocol
- **Diagnostics**: Report Group 1 and Group 3 as supplementary analyses
- **Rationale**: Blind evaluation is the most defensible for benchmark validity

#### For Explicitly Reducing Judge Self-Bias in Production
- **Best choice**: **Group 1 (Self)** - strongest bias reduction from the data
- **Rationale**: Lowest average self-bias (41.25%) and Claude shows self-awareness

#### For Maximum Balance and Consistency
- **Best choice**: **Group 3 (Full)** - most balanced vendor distribution
- **Trade-off**: Accepts slightly higher self-bias (43.96%) for better overall fairness
- **Caveat**: Least blind setting - most exposed to brand/identity effects

#### Avoid Group 2 Unless...
- Only use Group 2 if your purpose is to study bias amplification
- Group 2 shows highest bias amplification and worst performance metrics

### Vendor-Specific Strategies

- **Claude**: Self-hint helps (25.6% vs 30.0% baseline) - shows self-awareness
- **GPT**: No hinting mode significantly reduces bias (62-66% across all groups) - persistent high bias
- **Gemini**: Competitors hint may help (28.1% vs 33.1% baseline) - responsive to hinting

*Note: “33.33%” is a naive uniform baseline (3 vendors). Real-world “unbiased” rates can differ due to answer quality, prompt mix, and judge preference for style.*

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
