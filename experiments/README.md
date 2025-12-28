Experiments 2 and 3 use the same MT-Bench benchmark and the same models and tiers. We detail that below here.

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

| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | Haiku 4.5 | Sonnet 4.5 |
| GPT | GPT-5-mini | GPT-5.2 |
| Gemini | 2.5 Flash | 3 Pro Preview |

### Judges

- `claude_fast`, `claude_thinking`
- `gpt_fast`, `gpt_thinking`
- `gemini_fast`, `gemini_thinking`

## Metrics used

Below metrics are shared between experiments 2 and 3.

- **pp**: *percentage points* — the simple arithmetic difference between two percentages (e.g., 80% - 20% = 60 percentage points).

- **stdev (pp)**: *standard deviation* — a measure of how spread out values are. Calculated on percentages and reported in percentage points. Lower values mean less variation (more consistent).

- **Average Self-Bias (%)**: For each vendor (Claude, GPT, Gemini), we calculate how often that vendor's judges rank their own vendor's answers as #1. Values are aggregated across fast and thinking tier judges. Then we average these three percentages together. This tells us the overall self-bias across all vendors.

- **Deviation from Expected (pp)**: For each vendor, we calculate how far their self-bias rate is from 33.33% (the expected rate if judges were perfectly unbiased across 3 vendors). Self-bias rates are aggregated across fast and thinking tiers for each vendor. We take the absolute difference, then average across all three vendors. This measures how close we are to the unbiased baseline.

- **Balance Score (pp, stdev)**: We calculate the overall Top-1 win rate for each vendor across all 6 judges combined (fast and thinking tiers for all vendors), giving us three percentages (one per vendor). Then we calculate the standard deviation of these three percentages. A lower score means the three vendors' win rates are more similar to each other (more evenly distributed), regardless of whether that distribution is fair or biased.

- **Consistency (pp, stdev)**: For each of the 6 individual judge models, we calculate their self-bias rate. Then we calculate the standard deviation of these 6 rates. A lower score means all judges behave more similarly to each other (less variation in self-bias across different judge models).