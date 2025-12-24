# Experiment 3: Hinting Effect

## Research Question
> **Does revealing model identities change judge behavior?**

We use the same models from [`exp2_mt_bench`](../exp2_mt_bench/). Please check out the details
before proceeding with the rest of the sections.

## Design: Partial Hinting Control Groups

| Group | Hint Mode | What Judge Sees | Purpose |
|-------|-----------|-----------------|---------|
| **Group 1** | `self` | Only own model revealed | Self-knowledge effect |
| **Group 2** | `competitors` | Only competitor models revealed | Competitor awareness |
| **Group 3** | `full` | All models revealed | Full transparency |
| **Group 4** | `none` | No hints (blind) | Baseline control |

> [!NOTE] 
> Group 4 (`none`) is essentially **Experiment 2** - it uses the same blind judgment protocol with no model identity hints. The judgments are reused from Experiment 2's results.

## Main Metrics Comparison (clarified units + definitions)

We compared the four hinting groups across fairness/stability metrics. **Lower is better** for all metrics below, but note that **“more balanced” ≠ “unbiased”** (it only means Top-1 wins are more evenly spread).

| Metric | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) | Best |
|--------|----------------|----------------------|----------------|-----------------|------|
| **Average Self-Bias (%)** | 41.25% | 43.33% | 43.96% | 42.50% | Group 1 |
| **Deviation from Expected (pp)** | 13.06 pp | 13.47 pp | 10.63 pp | 11.53 pp | Group 3 |
| **Balance Score (pp, stdev)** | 15.50 | 14.96 | 13.10 | 14.07 | Group 3 |
| **Consistency (pp, stdev)** | 15.57 | 16.11 | 14.00 | 15.52 | Group 3 |

**Units**

- **pp** = *percentage points* (arithmetic difference between percentages).
- **stdev (pp)** = standard deviation computed on percentages, reported in percentage points.

**Metric definitions (consistent wording)**

- **Average Self-Bias (%)**: For each **vendor** \(v ∈ {Claude, GPT, Gemini}\), compute  
  `self_bias(v) = P(judges from v pick v as Top-1)`.  
  Then report the **mean** of `self_bias(v)` across the three vendors.

- **Deviation from Expected (pp)**: For each vendor \(v\), compute  
  `|self_bias(v) − 33.33%|` (naive baseline for 3 vendors), then average across vendors.

- **Balance Score (pp, stdev)**: Compute overall Top-1 win rate for each vendor across **all judges**, then take the **standard deviation** across the three vendors. Lower = more even Top-1 distribution.

- **Consistency (pp, stdev)**: Compute each **judge model’s** self-bias rate, then take the **standard deviation** across the 6 judges. Lower = judges behave more similarly.

> **Note:** A low **Balance Score** is about “evenness,” not necessarily “fairness.” It can improve simply because judges spread wins more evenly—even if they’re spreading them for the wrong reasons.

## Vendor-Specific Self-Bias Rates

Self-bias rates for each vendor across different hinting groups, aggregated across fast and thinking tiers. Values show the percentage of times each vendor's judges rank their own vendor's answers as #1.

| Vendor | Group 1 (Self) | Group 2 (Competitors) | Group 3 (Full) | Group 4 (Blind) |
|--------|----------------|----------------------|----------------|-----------------|
| **Claude** | 25.6% | 36.2% | 34.4% | 30.0% |
| **GPT** | 62.5% | 65.6% | 63.7% | 64.4% |
| **Gemini** | 35.6% | 28.1% | 33.8% | 33.1% |

*Self-bias rate = percentage of times a judge ranks their own vendor #1 (aggregated across fast and thinking tiers)*

## Domain-wise Best Group

Average self-bias rates by category for each hinting group, aggregated across all vendors and tiers. Best Group column indicates which hinting mode produces the lowest self-bias for that category.

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

*Best = lowest average self-bias across all vendors for that category (aggregated across fast and thinking tiers)*

## Goal-Based Recommendations

| Goal | Recommended Group | Rationale | Trade-offs |
|------|------------------|-----------|------------|
| **Benchmark Validity** | Group 4 (Blind) | Most defensible protocol; minimizes identity leakage | Baseline self-bias remains (42.50%) |
| **Bias Mitigation** | Group 1 (Self) | Lowest **Average Self-Bias** (41.25%) | Weaker balance/consistency than Group 3 |
| **Balanced Selection** | Group 3 (Full) | Best **Deviation**, **Balance**, and **Consistency**  | Highest Average Self-Bias (43.96%) |
| **Use only if studying disruption** | Group 2 (Competitors) | Worst **Consistency** (16.11) and tends to increase instability across judges/vendors | Can amplify bias patterns in some judges |

> [!NOTE]
> "33.33%" is a naive uniform baseline (3 vendors). Real-world "unbiased" rates can differ due to answer quality, prompt mix, and judge preference for style.*


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
