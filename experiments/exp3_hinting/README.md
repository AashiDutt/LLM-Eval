# Experiment 3: Hinting Effect

## Research Question
> **Does revealing model identities change judge behavior?**

We use the same models from [`exp2_mt_bench`](../exp2_mt_bench/). Please check out the details
before proceeding with the rest of the sections.

## Design: Partial Hinting Control Groups

We divided this experiment into groups of experiments each having a different purpose.

| Group | Hint Mode | What Judge Sees | Purpose |
|-------|-----------|-----------------|---------|
| **Group 1** | `self` | Only own model revealed | Self-knowledge effect |
| **Group 2** | `competitors` | Only competitor models revealed | Competitor awareness |
| **Group 3** | `full` | All models revealed | Full transparency |
| **Group 4** | `none` | No hints (blind) | Baseline control |

> [*Note:*] Group 4 (`none`) is essentially Experiment 2, as it uses the same blind judgment protocol with no model identity hints. The judgments are reused from Experiment 2's results.

## Main Metrics Comparison 

We compared the four hinting groups across key metrics. Lower values are better for all metrics. A low Balance Score is about “evenness,” not necessarily “fairness.” It can improve simply because judges spread wins more evenly.

| Metric | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) | Best |
|--------|----------------|----------------------|----------------|-----------------|------|
| **Average Self-Bias (%)** | 41.25% | 43.33% | 43.96% | 42.50% | Group 1 |
| **Deviation from Expected (pp)** | 13.06 pp | 13.47 pp | 10.63 pp | 11.53 pp | Group 3 |
| **Balance Score (pp, stdev)** | 15.50 | 14.96 | 13.10 | 14.07 | Group 3 |
| **Consistency (pp, stdev)** | 15.57 | 16.11 | 14.00 | 15.52 | Group 3 |

**Metrics used:**

- **pp**: *percentage points* — the simple arithmetic difference between two percentages (e.g., 80% - 20% = 60 percentage points).

- **stdev (pp)**: *standard deviation* — a measure of how spread out values are. Calculated on percentages and reported in percentage points. Lower values mean less variation (more consistent).

- **Average Self-Bias (%)**: For each vendor (Claude, GPT, Gemini), we calculate how often that vendor's judges rank their own vendor's answers as #1. Values are aggregated across fast and thinking tier judges. Then we average these three percentages together. This tells us the overall self-bias across all vendors.

- **Deviation from Expected (pp)**: For each vendor, we calculate how far their self-bias rate is from 33.33% (the expected rate if judges were perfectly unbiased across 3 vendors). Self-bias rates are aggregated across fast and thinking tiers for each vendor. We take the absolute difference, then average across all three vendors. This measures how close we are to the unbiased baseline.

- **Balance Score (pp, stdev)**: We calculate the overall Top-1 win rate for each vendor across all 6 judges combined (fast and thinking tiers for all vendors), giving us three percentages (one per vendor). Then we calculate the standard deviation of these three percentages. A lower score means the three vendors' win rates are more similar to each other (more evenly distributed), regardless of whether that distribution is fair or biased.

- **Consistency (pp, stdev)**: For each of the 6 individual judge models, we calculate their self-bias rate. Then we calculate the standard deviation of these 6 rates. A lower score means all judges behave more similarly to each other (less variation in self-bias across different judge models).

## Vendor-Specific Self-Bias Rates

Self-bias rates for each vendor across different hinting groups, aggregated across fast and thinking tiers. Values show the percentage of times each vendor's judges rank their own vendor's answers as #1(aggregated across fast and thinking tiers).

| Vendor (fast + thinking) | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) |
|--------|----------------|----------------------|----------------|-----------------|
| **Claude** | 25.6% | 36.2% | 34.4% | 30.0% |
| **GPT** | 62.5% | 65.6% | 63.7% | 64.4% |
| **Gemini** | 35.6% | 28.1% | 33.8% | 33.1% |

We found that GPT judges show consistently high self-bias across all hinting groups, while Claude judges exhibit the lowest self-bias, particularly in Group 1 (Self-hint) at 25.6%. While Gemini judges show moderate self-bias with Group 2 (Competitors-hint) producing the lowest rate at 28.1%. 

## Domain-wise Best Group

Average self-bias rates by category for each hinting group, aggregated across all vendors and tiers. Best Group column indicates which hinting mode produces the lowest self-bias for that category(aggregated across fast and thinking tiers).

| Category | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) | Best Group |
|----------|----------------|----------------------|----------------|-----------------|------------|
| Extraction | 31.7% | 38.3% | 33.3% | 35.0% | Group 1 |
| Humanities | 36.7% | 38.3% | 36.7% | 36.7% | Group 1 |
| Math | 46.7% | 51.7% | 51.7% | 50.0% | Group 1 |
| Reasoning | 41.7% | 43.3% | 41.7% | 41.7% | Group 1 |
| Writing | 38.3% | 43.3% | 38.3% | 45.0% | Group 1 |
| Coding | 43.3% | 43.3% | 45.0% | 41.7% | Group 4 |
| Roleplay | 55.0% | 55.0% | 61.7% | 53.3% | Group 4 |
| STEM | 36.7% | 33.3% | 43.3% | 36.7% | Group 2 |

Group 1 (Self-hint) minimizes self-bias in 5 of 8 categories, while Group 4 (Blind) performs best for Coding and Roleplay, and Group 2 (Competitors-hint) is optimal for STEM tasks. This suggests that hinting effects are both vendor-specific and domain-dependent.

## Goal-Based Recommendations

Here are some hinting group recommendations based on our evaluation:

| Goal | Recommended Group | Why | Trade-off |
|------|------------------|-----|----------|
| **Benchmark Validity** | Group 4 (Blind) | Judges don't know model identities and it matches standard evaluation practice | Self-bias remains at 42.50% (not the lowest) |
| **Bias Mitigation** | Group 1 (Self) | Self-bias drops to 41.25% (lowest across all groups) | Balance score and consistency are worse than Group 3 |
| **Balanced Selection** | Group 3 (Full) | Best balance, consistency, and deviation | Self-bias is highest at 43.96% |
| **Study Disruption** | Group 2 (Competitors) | Reveals how knowing competitors (but not self) changes judge behavior | Worst consistency and increases bias for some vendors |


<details>
<summary><b>Run the scripts</b></summary>

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

# Group 4: Baseline (reuse exp2 results data)
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

</details>
