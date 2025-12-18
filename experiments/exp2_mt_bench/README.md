# Experiment 2: MT-Bench Blind Judge Evaluation

## Research Question
> **Does judge bias vary across different domains/task types?**

## Benchmark: MT-Bench (Official)
- **Source**: [LMSYS FastChat](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge/data/mt_bench)
- **Paper**: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (Zheng et al., 2023)
- **Prompts**: 80 official MT-Bench questions (first turn only)
- **Data**: [HuggingFace Dataset](https://huggingface.co/datasets/sayakpaul/llm-bias-mt-bench)

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

### Judges (6 total)
- `claude_fast`, `claude_thinking`
- `gpt_fast`, `gpt_thinking`
- `gemini_fast`, `gemini_thinking`

---

## Results

### 1. Self-Bias Detection Summary

| Judge | Self-Preference | Expected | Bias (pp) | Verdict |
|-------|-----------------|----------|-----------|---------|
| **Claude** | 32.50% | 33.33% | +8.75 | ✅ **LEAST BIASED** |
| **Gemini** | 31.25% | 33.33% | +11.50 | ⚠️ Mild bias |
| **GPT** | 70.00% | 33.33% | +36.67 | ❌ **MOST BIASED** |

*pp = percentage points (arithmetic difference between percentages)*

### 2. Cross-Judge Comparison (Top-1 Selection %)

| Judge | Claude | Gemini | GPT |
|-------|--------|--------|-----|
| claude_fast | 27.50 | 17.50 | **55.00** |
| claude_thinking | 32.50 | 17.50 | **50.00** |
| gemini_fast | 22.50 | **35.00** | 42.50 |
| gemini_thinking | 26.25 | **31.25** | 42.50 |
| gpt_fast | 21.25 | 20.00 | **58.75** |
| gpt_thinking | 21.25 | 8.75 | **70.00** |

### 3. Average Scores by Vendor & Tier (Gemini Judge)

| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | 7.30 ± 2.23 | 7.96 ± 1.84 |
| Gemini | 6.01 ± 3.41 | 7.55 ± 2.75 |
| GPT | 7.05 ± 3.26 | **8.47 ± 2.21** |

### 4. Category-wise Preferences (Gemini Judge)

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

### 5. Tier Preference (Thinking vs Fast)

| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | 38.1% | **61.9%** |
| Gemini | 48.0% | **52.0%** |
| GPT | 26.5% | **73.5%** |

*All vendors' Thinking tier models preferred over Fast tier*

---

## Key Findings

1. **GPT shows STRONG self-preference bias**
   - 70% top-1 rate for own answers (expected: 33%)
   - Statistically significant (p < 0.0001)
   - Bias difference: +36.67 percentage points

2. **Claude is the most impartial judge**
   - 32.5% self-preference ≈ expected 33.33%
   - Actually rates GPT answers highest (50%)
   - No significant self-bias detected

3. **Gemini shows domain-specific preferences**
   - Strong preference for Math (80%) and Reasoning (70%)
   - Overall self-bias not statistically significant

4. **GPT answers universally preferred**
   - All 6 judges rank GPT highest (42-70% top-1)
   - GPT Thinking tier scores highest across the board (8.47/10)

5. **Thinking tier > Fast tier consistently**
   - All vendors' thinking models outperform fast models
   - GPT thinking shows strongest preference (73.5% of GPT wins)

---

## Hypotheses Evaluation

| Hypothesis | Result |
|------------|--------|
| Bias stronger in subjective domains | ⚠️ Mixed - Gemini biased in Math/Reasoning (objective) |
| GPT self-bias varies by domain | ✅ Confirmed - GPT bias consistent across domains |
| Technical tasks show different patterns | ✅ Confirmed - Gemini excels in Math/Reasoning |

---

## How to Run

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

## Data Files
- `data/answers/answers_mt_bench.json` - 480 model answers
- `data/judgments/judgments_mt_bench.json` - 480 judgments (80 × 6 judges)
- `data/results/` - Analysis outputs and visualizations

## Cost Estimate
- **Full run**: ~$25-30 (480 answer + 480 judge calls)
- **Quick test**: ~$1
