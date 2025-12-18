# Experiment 3: Hinting Effect

## Research Question
> **Does revealing model identities change judge behavior?**

## Design: Partial Hinting Control Groups

| Group | Hint Mode | What Judge Sees | Purpose |
|-------|-----------|-----------------|---------|
| **Group 1** | `self` | Only own model revealed | Self-knowledge effect |
| **Group 2** | `competitors` | Only competitor models revealed | Competitor awareness |
| **Group 3** | `full` | All models revealed | Full transparency |
| **Group 4** | `none` | No hints (blind) | Baseline control |

## Data Reuse

| Asset | Source | API Calls |
|-------|--------|-----------|
| Answers | `exp2_mt_bench/data/answers/answers_mt_bench.json` | 0 (reused) |
| Group 4 Judgments | `exp2_mt_bench/data/judgments/judgments_mt_bench.json` | 0 (reused) |
| Groups 1-3 Judgments | NEW | 1,440 (480 × 3) |

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

## How to Run

### Run All Groups (1-3)

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

## Hint Examples

### Group 1: Self-hint
```
[A] Answer text...
[B] Answer text...
...
**Note**: Answer(s) B, E are from GPT.
```

### Group 2: Competitors-hint
```
[A] Answer text...
[B] Answer text...
...
**Model hints**: [A] = CLAUDE, [B] = Not disclosed, [C] = GPT, [D] = GEMINI, [E] = CLAUDE, [F] = GPT
```
*Note: Judge's own model is marked as "Not disclosed" to prevent deduction by elimination*

### Group 3: Full-hint
```
[A] Answer text...
[B] Answer text...
...
**Model hints**: [A] = CLAUDE, [B] = GPT, [C] = GEMINI, [D] = CLAUDE, [E] = GPT, [F] = GEMINI
```

## Hypotheses

1. **Self-hint increases self-bias**: Judges favor own model more when they know which answer is theirs
2. **Competitor-hint reduces self-bias**: Knowing competitors but not self leads to fairer evaluation
3. **Full transparency**: May increase or decrease bias depending on model

## Expected Outputs

| Output | Description |
|--------|-------------|
| `group1_self.json` | Judgments with self-hints |
| `group2_competitors.json` | Judgments with competitor-hints |
| `group3_full.json` | Judgments with full hints |
| `group4_blind.json` | Baseline blind judgments (from exp2) |
| `analysis.ipynb` | Cross-group comparison |

## Cost Estimate

- **Groups 1-3**: ~$45 (480 × 3 judge calls)
- **Quick test**: ~$1

## Comparison Analysis

After running all groups, compare:

| Metric | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) |
|--------|----------------|----------------------|----------------|-----------------|
| GPT self-preference | ? | ? | ? | 70% (baseline) |
| Claude self-preference | ? | ? | ? | 32.5% |
| Gemini self-preference | ? | ? | ? | 31.25% |

