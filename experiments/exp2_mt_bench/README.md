# Experiment 2: MT-Bench Blind Judge Evaluation

## Research Question
> **Does judge bias vary across different domains/task types?**

## Benchmark: MT-Bench (Official)
- **Source**: [LMSYS FastChat](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge/data/mt_bench)
- **Paper**: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (Zheng et al., 2023)
- **Prompts**: 80 official MT-Bench questions (first turn only)
- **Obtained Data**:
  * [Answers](https://huggingface.co/datasets/sayakpaul/llm-bias-mt-bench/blob/main/experiment-2/answers_new.json)
  * [Judgments](https://huggingface.co/datasets/sayakpaul/llm-bias-mt-bench/blob/main/experiment-2/judgments_new.json)

## Setup
- **Answers**: Anonymized (A, B, C, D, E, F)
- **Prompts**: 80 MT-Bench style prompts
- **Hinting**: None (blind evaluation)
- **Judgments**: 480 (80 prompts × 6 judges)

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

### Answer Generators
| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | Haiku 4.5 | Sonnet 4.5 |
| GPT | GPT-5-mini | GPT-5.2 |
| Gemini | 2.5 Flash | 3 Pro Preview |

### Judges
- `claude_fast`, `claude_thinking`
- `gpt_fast`, `gpt_thinking`
- `gemini_fast`, `gemini_thinking`

---

## Results

### 1. Self-Bias Detection Summary

How often each vendor's judges rank their own vendor's answers on top, compared to the expected baseline. Values are aggregated across fast and thinking tiers for each vendor family.

| Judge | Self-Preference | Expected | Bias (pp) | Verdict |
|-------|-----------------|----------|-----------|---------|
| **Claude** | 32.50% | 33.33% | +8.75 | **Least Biased** |
| **Gemini** | 31.25% | 33.33% | +11.50 | **Mild Biased** |
| **GPT** | 70.00% | 33.33% | +36.67 | **Most Biased** |

**Self-Preference**: Percentage of times the vendor's judges rank their own vendor as #1

**Bias (pp)**: Difference from expected in percentage points (pp = percentage points (arithmetic difference between percentages))

### 2. Cross-Judge Comparison (Top-1 Selection %)

Percentage of times each judge ranks each vendor's answers as #1. Each judge evaluates all 6 models (claude_fast, claude_thinking, gpt_fast, gpt_thinking, gemini_fast, gemini_thinking) and ranks them. The columns show vendor-level aggregation across fast and thinking tiers.

| Judge | Claude | Gemini | GPT |
|-------|--------|--------|-----|
| claude_fast | 27.50 | 17.50 | **55.00** |
| claude_thinking | 32.50 | 17.50 | **50.00** |
| gemini_fast | 22.50 | **35.00** | 42.50 |
| gemini_thinking | 26.25 | **31.25** | 42.50 |
| gpt_fast | 21.25 | 20.00 | **58.75** |
| gpt_thinking | 21.25 | 8.75 | **70.00** |

*Bold values indicate self-preference (judge ranking their own vendor).*

### 3. Average Scores by Vendor & Tier 

Average scores (0-10 scale) given by Gemini Thinking judge to each vendor's fast vs thinking tier models. 

| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | 7.30 ± 2.23 | 7.96 ± 1.84 |
| Gemini | 6.01 ± 3.41 | 7.55 ± 2.75 |
| GPT | 7.05 ± 3.26 | 8.47 ± 2.21 |

*mean ± standard deviation, where standard deviation shows score variability across 80 prompts (single run).*

### 4. Category-wise Preferences by Judge Family

Which vendor's answers are ranked #1 most often in each category, broken down by judge family.  

*Winner column shows the dominant vendor per category.*

#### 4a. Claude Judges

| Category | Claude | Gemini | GPT | Winner |
|----------|--------|--------|-----|--------|
| Coding | 35% | 5% | **60%** | GPT |
| Extraction | **40%** | 25% | 35% | Claude |
| Humanities | 20% | 5% | **75%** | GPT |
| Math | 35% | **40%** | 25% | Gemini |
| Reasoning | 40% | **45%** | 15% | Gemini |
| Roleplay | 30% | 10% | **60%** | GPT |
| STEM | 10% | 10% | **80%** | GPT |
| Writing | 30% | 0% | **70%** | GPT |

#### 4b. Gemini Thinking Judge

| Category | Claude | Gemini | GPT | Winner |
|----------|--------|--------|-----|--------|
| Coding | 30% | 10% | **60%** | GPT |
| Extraction | **60%** | 10% | 30% | Claude |
| Humanities | 20% | 20% | **60%** | GPT |
| Math | 20% | **80%** | 0% | Gemini |
| Reasoning | 20% | **70%** | 10% | Gemini |
| Roleplay | 0% | 40% | **60%** | GPT |
| STEM | 30% | 0% | **70%** | GPT |
| Writing | 30% | 20% | **50%** | GPT |

#### 4c. GPT Judges 

| Category | Claude | Gemini | GPT | Winner |
|----------|--------|--------|-----|--------|
| Coding | 15% | 10% | **75%** | GPT |
| Extraction | 40% | 5% | **55%** | GPT |
| Humanities | 20% | 10% | **70%** | GPT |
| Math | 25% | **40%** | 35% | Gemini |
| Reasoning | **45%** | 30% | 25% | Claude |
| Roleplay | 5% | 10% | **85%** | GPT |
| STEM | 10% | 10% | **80%** | GPT |
| Writing | 10% | 0% | **90%** | GPT |

### 5. Tier Preference (Thinking vs Fast)

The percentage of times thinking-tier vs fast-tier models are ranked #1 across all judges.

| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | 38.1% | **61.9%** |
| Gemini | 48.0% | **52.0%** |
| GPT | 26.5% | **73.5%** |

> [!NOTE]
> All vendors' Thinking tier models preferred over Fast tier

---

<details>
<summary><b>Unravel for additional commentaries</b></summary>

### Overall Self-Bias Patterns

GPT judges show the strongest self-preference bias, ranking their own answers #1 significantly more often than expected. Claude demonstrates the least bias, with self-preference rates close to the baseline and actually favoring GPT answers over its own. Gemini shows mild self-bias, particularly in its core strength domains. While GPT answers are selected most frequently even by non-GPT judges (suggesting genuine quality advantages), the substantial gap between GPT judge preferences and other judges' preferences indicates clear self-bias is present.

### Domain-wise Breakdown

#### Self-Bias by Category

Self-bias rates for each vendor broken down by category, aggregated across fast and thinking tiers. 
*Columns indicate percentage of times each vendor's judges (fast + thinking combined) rank their own vendor #1 in that category.*

| Category | GPT Self-Bias | Claude Self-Bias | Gemini Self-Bias |
|----------|---------------|------------------|------------------|
| Writing | **90.0%** | 30.0% | 15.0% |
| Roleplay | **85.0%** | 30.0% | 45.0% |
| STEM | **80.0%** | 10.0% | 20.0% |
| Coding | **75.0%** | 35.0% | 15.0% |
| Humanities | **70.0%** | 20.0% | 20.0% |
| Extraction | 55.0% | 40.0% | 10.0% |
| Math | 35.0% | 35.0% | **80.0%** |
| Reasoning | 25.0% | 40.0% | **60.0%** |

**Key observations:**
- GPT shows highest self-bias in Writing (90%) and Roleplay (85%), suggesting stronger bias in creative/subjective domains.
- Gemini shows strong self-bias in Math (80%) and Reasoning (60%), its core strengths.
- Claude maintains relatively low self-bias across all domains (10-40%).

#### Cross-Judge GPT Selection by Category

How often GPT answers are ranked #1 by different judges, broken down by category.

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
- In STEM, Claude judge actually selects GPT more than GPT judge itself (90% vs 70%), suggesting GPT's STEM answers are genuinely strong.
- In Math, GPT judge shows lower self-bias (20%), likely because Gemini dominates this domain.
- Cross-judge agreement varies by domain, with Writing showing highest GPT preference across all judges.

### Summary

**Judge choice matters**: Depending on the judge vendor, the "best model" changes dramatically across domains. GPT shows strong self-preference bias (70% vs 33% expected), but GPT answers are also frequently selected by non-GPT judges, suggesting genuine quality advantages in many domains.

**Self-bias varies by domain**: GPT's self-bias is strongest in creative/subjective domains (Writing: 90%, Roleplay: 85%), while Gemini shows strong self-bias in its core strengths (Math: 80%, Reasoning: 60%). Claude maintains relatively impartial judging across all domains.

**Cross-judge agreement indicates quality**: When multiple judges agree on a winner (e.g., GPT in Writing, Gemini in Math), it suggests genuine domain-specific strengths rather than just judge favoritism.

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
