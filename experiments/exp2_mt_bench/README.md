# Experiment 2: MT-Bench Blind Judge Evaluation

## Research Question
> **Does judge bias vary across different domains/task types?**

## Results

### 1. Self-Bias Detection 

We calculated how often each vendor's judges rank their own vendor's answers on top, then compared it to the expected baseline(33.33%). 

Note that the values in the table below are aggregated across fast and thinking tiers for each vendor family.

| Judge | Self-Preference | Baseline | Bias (pp) | Self Preference Level |
|-------|-----------------|----------|-----------|---------|
| **Claude** | 32.50% | 33.33% | -0.83 | Near neutral |
| **Gemini** | 31.25% | 33.33% | -2.08 | Near neutral |
| **GPT** | 70.00% | 33.33% | +36.67 | Strong self-preference |

**Self-Preference**: Percentage of times the vendor's judges rank their own vendor as #1

**Baseline**: The baseline of 33.33% represents the expected self-preference rate if judges were completely unbiased across 3 vendors (each vendor would receive 1/3 of top rankings).

**Bias (pp)**: Difference from expected in percentage points (pp = percentage points (arithmetic difference between percentages))

### 2. Cross-Judge Comparison 

The table below depicts the percentage of times each judge ranks each vendor's answers as #1. Each judge evaluates all 6 models (claude_fast, claude_thinking, gpt_fast, gpt_thinking, gemini_fast, gemini_thinking) and ranks them. The columns show vendor-level aggregation across fast and thinking tiers.

| Judge | Claude | Gemini | GPT |
|-------|--------|--------|-----|
| claude_fast | 27.50 | 17.50 | **55.00** |
| claude_thinking | 32.50 | 17.50 | **50.00** |
| gemini_fast | 22.50 | **35.00** | 42.50 |
| gemini_thinking | 26.25 | **31.25** | 42.50 |
| gpt_fast | 21.25 | 20.00 | **58.75** |
| gpt_thinking | 21.25 | 8.75 | **70.00** |

*Bold values indicate self-preference (judge ranking their own vendor).*

### 3. Tier effects via score distributions 

To check whether “thinking” tiers systematically score higher, we compare mean ± std scores (0–10) assigned by a single judge (Gemini Thinking) to each vendor’s fast vs thinking models across 80 prompts.

| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | 7.30 ± 2.23 | 7.96 ± 1.84 |
| Gemini | 6.01 ± 3.41 | 7.55 ± 2.75 |
| GPT | 7.05 ± 3.26 | 8.47 ± 2.21 |

Thinking tiers score higher for all vendors (≈ +0.7 to +1.5 points here), but variance remains non-trivial across prompts.

### 4. Category-wise Preferences by Judge Family

Here are category-wise preferences for "which vendor's answers are ranked #1 most often in each category" (broken down by judge family).  

**Winner column shows the dominant vendor per category.*

#### 4a. Claude Judges

We calculated the percentage of times Claude judges (aggregated across `claude_fast` and `claude_thinking`) rank each vendor's answers within each category. Each row represents a different category, and each column shows the win rate for that vendor when evaluated by Claude judges. Values are aggregated across fast and thinking tier judges.

| Category | Claude | Gemini | GPT | Winner |
|----------|--------|--------|-----|--------|
| Coding | 35% | 5% | 60% | GPT |
| Extraction | 40% | 25% | 35% | Claude |
| Humanities | 20% | 5% | 75% | GPT |
| Math | 35% | 40% | 25% | Gemini |
| Reasoning | 40% | 45% | 15% | Gemini |
| Roleplay | 30% | 10% | 60% | GPT |
| STEM | 10% | 10% | 80% | GPT |
| Writing | 30% | 0% | 70% | GPT |

#### 4b. Gemini Judges

We calculated the percentage of times Gemini judges (aggregated across `gemini_fast` and `gemini_thinking`) rank each vendor's answers within each category. Each column shows the win rate for that vendor when evaluated by Gemini judges. Values are aggregated across fast and thinking tier judges.

| Category | Claude | Gemini | GPT | Winner |
|----------|--------|--------|-----|--------|
| Coding | 40% | 15% | 45% | GPT |
| Extraction | 35% | 10% | 55% | GPT |
| Humanities | 20% | 20% | 60% | GPT |
| Math | 20% | 80% | 0% | Gemini |
| Reasoning | 30% | 60% | 10% | Gemini |
| Roleplay | 0% | 45% | 55% | GPT |
| STEM | 15% | 20% | 65% | GPT |
| Writing | 35% | 15% | 50% | GPT |

#### 4c. GPT Judges 

The following table shows the percentage of times GPT judges (aggregated across `gpt_fast` and `gpt_thinking`) rank each vendor's answers as #1 within each category. Each row represents a different category, and each column shows the win rate for that vendor when evaluated by GPT judges. Values are aggregated across fast and thinking tier judges.

| Category | Claude | Gemini | GPT | Winner |
|----------|--------|--------|-----|--------|
| Coding | 15% | 10% | 75% | GPT |
| Extraction | 40% | 5% | 55% | GPT |
| Humanities | 20% | 10% | 70% | GPT |
| Math | 25% | 40% | 35% | Gemini |
| Reasoning | 45% | 30% | 25% | Claude |
| Roleplay | 5% | 10% | 85% | GPT |
| STEM | 10% | 10% | 80% | GPT |
| Writing | 10% | 0% | 90% | GPT |

Across all three judge families, GPT answers are ranked #1 most frequently, winning 6 out of 8 categories. While Gemini consistently dominates Math and performs strongly in Reasoning across all judges. Claude also shows the most balanced distribution, winning only 2 categories per judge family. There is strong cross-judge agreement that GPT excels in creative domains (Writing, Roleplay, STEM, Humanities) and that Gemini excels in quantitative domains (Math, Reasoning).

### 5. Tier Preference (Thinking vs Fast)

We tested preference for each tier for all models. For each vendor, we calculated the percentage of times their fast-tier vs thinking-tier models are ranked #1 across all judges. Specifically, we identified all judgments where a vendor's model was ranked #1, then determined whether it was the fast-tier or thinking-tier model for that vendor, and calculated the percentage distribution.

| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | 38.1% | 61.9% |
| Gemini | 48.0% | 52.0% |
| GPT | 26.5% | 73.5% |

> [!NOTE]
> All vendors' Thinking tier models preferred over Fast tier

---

<details>
<summary><b>Unravel for additional commentaries</b></summary>

### Overall Self-Bias Patterns

GPT judges show the strongest self-preference bias, ranking their own answers #1 significantly more often than expected (+36.67 pp above baseline). Claude demonstrates the least bias, with self-preference rates slightly below the baseline (-0.83 pp) and actually favoring GPT answers over its own. Gemini also shows less self-bias than expected overall (-2.08 pp), but demonstrates strong domain-specific self-bias in its core strength domains (Math: 80%, Reasoning: 60%). While GPT answers are selected most frequently even by non-GPT judges (suggesting genuine quality advantages), the substantial gap between GPT judge preferences and other judges' preferences indicates clear self-bias is present.

### Domain-wise Breakdown

#### Self-Bias by Category

Self-bias rates for each vendor broken down by category, aggregated across fast and thinking tiers. The columns indicate percentage of times each vendor's judges (aggregated) rank their own vendor #1 in that category.

| Category | GPT Self-Bias | Claude Self-Bias | Gemini Self-Bias |
|----------|---------------|------------------|------------------|
| Writing | 90.0% | 30.0% | 15.0% |
| Roleplay | 85.0% | 30.0% | 45.0% |
| STEM | 80.0% | 10.0% | 20.0% |
| Coding | 75.0% | 35.0% | 15.0% |
| Humanities | 70.0% | 20.0% | 20.0% |
| Extraction | 55.0% | 40.0% | 10.0% |
| Math | 35.0% | 35.0% | 80.0% |
| Reasoning | 25.0% | 40.0% | 60.0% |

**Key observations:**
- GPT shows highest self-bias in Writing (90%) and Roleplay (85%), suggesting stronger bias in creative and subjective domains.
- Gemini shows strong self-bias in Math (80%) and Reasoning (60%) which are its core strengths.
- Claude maintains relatively low self-bias across all domains (10-40%).

#### Cross-Judge GPT Selection by Category

Since, GPT showed the strongest overall self-bias(refer to previous table). We compared how often GPT judges select GPT answers versus how often other judges select GPT answers, helping distinguish between self-bias and genuine quality advantages. 

| Category | GPT Judge | Claude Judge | Gemini Judge | Gap |
|----------|-----------|--------------|--------------|-----|
| Writing | 90.0% | 70.0% | 50.0% | +40pp |
| Roleplay | 80.0% | 60.0% | 50.0% | +30pp |
| STEM | 70.0% | 90.0% | 60.0% | -20pp* |
| Humanities | 70.0% | 70.0% | 60.0% | +10pp |
| Coding | 60.0% | 50.0% | 30.0% | +30pp |
| Extraction | 50.0% | 30.0% | 80.0% | -30pp* |
| Reasoning | 30.0% | 30.0% | 10.0% | +20pp |
| Math | 20.0% | 40.0% | 0.0% | +20pp |

*Gap = difference between GPT judge and average of other judges. Positive gap indicates GPT judge favors GPT more.*

*Negative gap indicates GPT judge selects GPT less than other judges (e.g., Claude judge selects GPT more in STEM)*

**Domain insights:**
- GPT self-bias is strongest in Writing and Roleplay (creative tasks).
- In STEM, Claude judge actually selects GPT more than GPT judge itself. This suggests GPT's STEM answers are genuinely strong.
- In Math, GPT judge shows lower self-bias, likely because Gemini dominates this domain.
- Cross-judge agreement varies by domain, with Writing showing highest GPT preference across all judges.

### Summary

**Judge choice**: Depending on the judge vendor, the "best model" changes dramatically across domains. GPT shows strong self-preference bias (70% vs 33% expected), but GPT answers are also frequently selected by non-GPT judges. This shows genuine quality advantages of GPT.

**Self-bias varies by domain**: GPT's self-bias is strongest in creative domains (Writing: 90%, Roleplay: 85%), while Gemini shows strong self-bias in its core strengths (Math: 80%, Reasoning: 60%). Claude maintains relatively impartial judging across all domains.

**Cross-judge agreement**: When multiple judges agree on a winner (like GPT in Writing, Gemini in Math), it suggests genuine domain-specific strengths rather than just judge favoritism.

</details>

<details>
<summary><b>Run the scripts</b></summary>

```bash
cd /path/to/LLM_Eval

# Step 1: Generate answers (80 prompts × 6 models = 480 API calls)
python src/generate_answers.py \
  --config experiments/exp2_mt_bench/config.yaml \
  --prompts experiments/exp2_mt_bench/prompts.json \
  --output experiments/exp2_mt_bench/data/answers/answers.json

# Step 2: Judge answers (80 prompts × 6 judges = 480 API calls)
python src/judge_answers.py \
  --config experiments/exp2_mt_bench/config.yaml \
  --answers experiments/exp2_mt_bench/data/answers/answers.json \
  --output experiments/exp2_mt_bench/data/judgments/judgments.json

# Step 3: Analyze
jupyter notebook experiments/exp2_mt_bench/analysis.ipynb
```

`src/generate_answers.py` and `src/judge_answers.py` provide a bunch of useful CLI flags to ease debugging. Please run them with `-h` to see them.

</details>
