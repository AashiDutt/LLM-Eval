# Experiment 2: MT-Bench Blind Judge Evaluation

## Research Question
> **Does judge bias vary across different domains/task types?**

## Benchmark: MT-Bench (Official)
- **Source**: [LMSYS FastChat](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge/data/mt_bench)
- **Paper**: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (Zheng et al., 2023)
- **Prompts**: 80 official MT-Bench questions (first turn only)

## Setup
- **Answers**: Anonymized (A, B, C, D, E, F)
- **Prompts**: 80 MT-Bench style prompts
- **Hinting**: None (blind evaluation)

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
| Gemini | 2.5 Flash | 3 Pro |

### Judges
- `gemini_fast` (primary)
- `claude_thinking`
- `gpt_thinking`

## Expected Outputs
- Judge-bias heatmap by category
- Domain-specific self-bias scores
- Comparison with Experiment 1 (mixed prompts)

## How to Run

```bash
cd /path/to/LLM_Eval

# Step 1: Generate answers (80 prompts × 6 models = 480 API calls)
python src/generate_answers.py \
  --config experiments/exp2_mt_bench/config.yaml \
  --prompts experiments/exp2_mt_bench/prompts.json \
  --output experiments/exp2_mt_bench/data/answers/answers.json

# Step 2: Judge answers (80 prompts × 3 judges = 240 API calls)
python src/judge_answers.py \
  --config experiments/exp2_mt_bench/config.yaml \
  --answers experiments/exp2_mt_bench/data/answers/answers.json \
  --output experiments/exp2_mt_bench/data/judgments/judgments.json \
  --judges gemini_thinking claude_thinking gpt_thinking

# Step 3: Analyze
jupyter notebook experiments/exp2_mt_bench/analysis.ipynb
```

## Quick Test (5 prompts)
```bash
python src/generate_answers.py \
  --config experiments/exp2_mt_bench/config.yaml \
  --prompts experiments/exp2_mt_bench/prompts.json \
  --output experiments/exp2_mt_bench/data/answers/answers_test.json \
  --limit 5

python src/judge_answers.py \
  --config experiments/exp2_mt_bench/config.yaml \
  --answers experiments/exp2_mt_bench/data/answers/answers_test.json \
  --judges gemini_thinking \
  --limit 5
```

## Cost Estimate
- **Full run**: ~$15-20 (480 answer + 240 judge calls)
- **Quick test**: ~$1

## Hypotheses
1. Bias may be stronger in **subjective** domains (writing, roleplay) vs **objective** (math, coding)
2. GPT's self-bias (seen in Exp 1) may vary by domain
3. Coding/technical tasks may show different patterns than creative tasks

