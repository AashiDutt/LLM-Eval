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

| Asset | Source | API Calls | Status |
|-------|--------|-----------|--------|
| Answers | `experiments/exp3_hinting/data/answers/answers_mt_bench.json` | 0 (reused) | ✅ Available |
| Group 2 Judgments | `experiments/exp3_hinting/data/judgments/judgments_group2.json` | 480 | ✅ Available |
| Group 4 Judgments | `experiments/exp3_hinting/data/judgments/judgments_group4.json` | 0 (reused) | ✅ Available |
| Group 1 Judgments | NEW | 480 | ⏳ Pending |
| Group 3 Judgments | NEW | 480 | ⏳ Pending |

## Models

### Answer Generators (from Exp 2)
| Vendor | Fast Tier | Thinking Tier |
|--------|-----------|---------------|
| Claude | Haiku 4.5 | Sonnet 4.5 |
| GPT | GPT-5-mini | o4-mini |
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

## Available Data

| Output | Description | Status |
|--------|-------------|--------|
| `judgments_group2.json` | Judgments with competitor-hints | ✅ Available |
| `judgments_group4.json` | Baseline blind judgments (from exp2) | ✅ Available |
| `group1_self.json` | Judgments with self-hints | ⏳ Pending |
| `group3_full.json` | Judgments with full hints | ⏳ Pending |
| `analysis.ipynb` | Cross-group comparison | ✅ Available |

## Cost Estimate

- **Groups 1-3**: ~$45 (480 × 3 judge calls)
- **Quick test**: ~$1

## Results (Available Groups Only)

**Note**: This analysis includes only Group 2 (Competitors) and Group 4 (Blind) as these are the currently available judgment files.

### 1. Self-Bias Detection Summary (Group 2 vs Group 4)

| Vendor | Group 2 (Competitors) | Group 4 (Blind) | Change (pp) | Verdict |
|--------|----------------------|-----------------|-------------|---------|
| **Claude** | 36.25% | 30.00% | +6.25 | ✅ **LEAST BIASED** |
| **Gemini** | 28.12% | 33.12% | -5.00 | ⚠️ Mild bias |
| **GPT** | 65.62% | 64.38% | +1.25 | ❌ **MOST BIASED** |

*pp = percentage points (arithmetic difference between percentages)*

### 2. Cross-Judge Comparison (Group 2 - Top-1 Selection %)

| Judge | Claude | Gemini | GPT |
|-------|--------|--------|-----|
| claude_fast | 32.50 | 13.75 | **53.75** |
| claude_thinking | 40.00 | 18.75 | **41.25** |
| gemini_fast | 25.00 | 30.00 | **45.00** |
| gemini_thinking | 21.25 | 26.25 | **52.50** |
| gpt_fast | 23.75 | 17.50 | **58.75** |
| gpt_thinking | 20.00 | 7.50 | **72.50** |

### 3. Self-Bias Change from Baseline

| Vendor | Group 2 Rate | Group 4 Rate | Change (pp) | Effect |
|--------|--------------|--------------|------------|-------|
| Claude | 36.25% | 30.00% | +6.25 | ⚠️ Slight increase |
| GPT | 65.62% | 64.38% | +1.25 | ➡️ Minimal change |
| Gemini | 28.12% | 33.12% | -5.00 | ✅ Slight decrease |

---

## Key Findings 🔎

1. **Competitors hint has minimal effect on GPT self-bias**
   - GPT self-preference: 65.62% (Group 2) vs 64.38% (Group 4)
   - Change: +1.25 percentage points (minimal change)
   - GPT remains highly biased even when competitors are revealed
   - The +1.25pp change is negligible, indicating competitors hint does not reduce GPT's strong self-preference

2. **Claude shows slight increase in self-bias**
   - Claude self-preference: 36.25% (Group 2) vs 30.00% (Group 4)
   - Change: +6.25 percentage points (slight increase)
   - Still remains the least biased judge overall (closest to expected 33.33%)
   - The increase is modest and Claude maintains relative impartiality

3. **Gemini shows slight decrease in self-bias**
   - Gemini self-preference: 28.12% (Group 2) vs 33.12% (Group 4)
   - Change: -5.00 percentage points (slight decrease)
   - Revealing competitors may help Gemini be more impartial
   - This is the only vendor showing reduced self-bias with competitors hint

4. **Overall pattern**: Revealing competitor identities (while hiding own) does not significantly reduce self-bias for highly biased models like GPT. The effect is minimal across all vendors, suggesting that competitor awareness alone is insufficient to mitigate strong self-preference bias.

---

## Pending Analysis

The following groups are not yet available and will be analyzed when data becomes available:

- **Group 1 (Self)**: Judges see only their own model revealed
- **Group 3 (Full)**: All models revealed

Once these groups are available, the analysis will be updated to include all four groups for comprehensive comparison.

