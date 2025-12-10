import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from scipy import stats


def load_and_merge_data(answers_path: str, judgments_path: str) -> pd.DataFrame:
    import json
    
    with open(answers_path, 'r') as f:
        answers = json.load(f)
    
    with open(judgments_path, 'r') as f:
        judgments = json.load(f)
    
    rows = []
    for judgment in judgments:
        if 'error' in judgment:
            continue
        
        prompt_id = judgment['prompt_id']
        judge = judgment['judge_model']
        ranking = judgment['ranking']
        scores = judgment['scores']
        mapping = judgment['mapping']
        
        for rank_idx, label in enumerate(ranking):
            answer_id = mapping[label]
            score = scores[label]
            
            answer = next((a for a in answers if a['answer_id'] == answer_id), None)
            if answer is None:
                continue
            
            rows.append({
                'prompt_id': prompt_id,
                'category': answer['category'],
                'answer_id': answer_id,
                'model_vendor': answer['model_vendor'],
                'model_tier': answer['model_tier'],
                'judge': judge,
                'rank': rank_idx + 1,
                'score': score,
                'is_top_ranked': rank_idx == 0
            })
    
    df = pd.DataFrame(rows)
    return df


def calculate_top1_preference(df: pd.DataFrame, judge: str = None) -> pd.DataFrame:
    if judge:
        df = df[df['judge'] == judge]
    
    top1 = df[df['is_top_ranked'] == True]
    vendor_counts = top1.groupby('model_vendor').size()
    total = len(top1)
    
    results = []
    for vendor in ['claude', 'gpt', 'gemini']:
        count = vendor_counts.get(vendor, 0)
        percentage = (count / total * 100) if total > 0 else 0
        results.append({
            'vendor': vendor,
            'top1_count': count,
            'top1_percentage': percentage,
            'total_judgments': total
        })
    
    return pd.DataFrame(results)


def calculate_average_scores(df: pd.DataFrame, judge: str = None) -> pd.DataFrame:
    if judge:
        df = df[df['judge'] == judge]
    
    grouped = df.groupby(['model_vendor', 'model_tier'])['score'].agg(['mean', 'std', 'count'])
    grouped = grouped.reset_index()
    grouped.columns = ['vendor', 'tier', 'mean_score', 'std_score', 'count']
    
    return grouped


def calculate_category_preference(df: pd.DataFrame, judge: str = None) -> pd.DataFrame:
    if judge:
        df = df[df['judge'] == judge]
    
    top1 = df[df['is_top_ranked'] == True]
    
    category_vendor = top1.groupby(['category', 'model_vendor']).size().reset_index(name='count')
    
    category_totals = top1.groupby('category').size()
    category_vendor['total'] = category_vendor['category'].map(category_totals)
    category_vendor['percentage'] = (category_vendor['count'] / category_vendor['total'] * 100)
    
    return category_vendor


def calculate_tier_preference(df: pd.DataFrame, judge: str = None) -> pd.DataFrame:
    if judge:
        df = df[df['judge'] == judge]
    
    top1 = df[df['is_top_ranked'] == True]
    
    vendor_tier = top1.groupby(['model_vendor', 'model_tier']).size().reset_index(name='count')
    
    vendor_totals = top1.groupby('model_vendor').size()
    vendor_tier['vendor_total'] = vendor_tier['model_vendor'].map(vendor_totals)
    vendor_tier['percentage'] = (vendor_tier['count'] / vendor_tier['vendor_total'] * 100)
    
    return vendor_tier


def detect_self_bias(df: pd.DataFrame, target_vendor: str = 'gemini') -> Dict[str, Any]:
    results = {}
    
    judges = df['judge'].unique()
    
    for judge in judges:
        judge_df = df[df['judge'] == judge]
        top1 = judge_df[judge_df['is_top_ranked'] == True]
        
        target_count = len(top1[top1['model_vendor'] == target_vendor])
        total_count = len(top1)
        
        results[judge] = {
            'target_vendor_top1_count': target_count,
            'total_judgments': total_count,
            'target_vendor_top1_rate': target_count / total_count if total_count > 0 else 0
        }
    
    target_judge_key = f"{target_vendor}_thinking"
    
    if target_judge_key in results:
        target_judge_rate = results[target_judge_key]['target_vendor_top1_rate']
        
        other_rates = [
            results[j]['target_vendor_top1_rate'] 
            for j in results 
            if j != target_judge_key
        ]
        
        if other_rates:
            avg_other_rate = np.mean(other_rates)
            bias_difference = target_judge_rate - avg_other_rate
            
            results['bias_analysis'] = {
                'target_vendor': target_vendor,
                'target_judge': target_judge_key,
                'target_judge_rate': target_judge_rate,
                'other_judges_avg_rate': avg_other_rate,
                'bias_difference': bias_difference,
                'bias_percentage_points': bias_difference * 100
            }
    
    return results


def run_statistical_tests(df: pd.DataFrame, target_vendor: str = 'gemini') -> Dict[str, Any]:
    results = {}
    
    target_judge = f"{target_vendor}_thinking"
    judge_df = df[df['judge'] == target_judge]
    top1 = judge_df[judge_df['is_top_ranked'] == True]
    
    vendor_counts = top1['model_vendor'].value_counts()
    
    expected_per_vendor = len(top1) / 3
    expected = [expected_per_vendor] * 3
    observed = [vendor_counts.get(v, 0) for v in ['claude', 'gpt', 'gemini']]
    
    chi2, p_value = stats.chisquare(observed, expected)
    
    results['chi_square_test'] = {
        'test': 'Chi-square goodness of fit',
        'null_hypothesis': 'Judge preferences are uniform across vendors',
        'chi2_statistic': float(chi2),
        'p_value': float(p_value),
        'significant_at_0.05': p_value < 0.05,
        'observed_counts': dict(zip(['claude', 'gpt', 'gemini'], observed)),
        'expected_counts': dict(zip(['claude', 'gpt', 'gemini'], expected))
    }
    
    target_count = vendor_counts.get(target_vendor, 0)
    total = len(top1)
    expected_prob = 1/3
    
    binom_result = stats.binomtest(target_count, total, expected_prob, alternative='greater')
    
    results['binomial_test'] = {
        'test': 'Binomial test',
        'null_hypothesis': f'{target_vendor} ranked #1 at expected rate (1/3)',
        'observed_rate': target_count / total if total > 0 else 0,
        'expected_rate': expected_prob,
        'p_value': float(binom_result.pvalue),
        'significant_at_0.05': binom_result.pvalue < 0.05
    }
    
    return results


def generate_summary_report(df: pd.DataFrame, target_vendor: str = 'gemini') -> str:
    report = []
    report.append("="*70)
    report.append("BIAS EVALUATION SUMMARY REPORT")
    report.append("="*70)
    
    target_judge = f"{target_vendor}_thinking"
    judge_df = df[df['judge'] == target_judge]
    
    report.append(f"\nTarget Vendor: {target_vendor.upper()}")
    report.append(f"Judge: {target_judge}")
    report.append(f"Total judgments analyzed: {len(judge_df) // 6}")
    
    report.append("\n" + "-"*70)
    report.append("TOP-1 PREFERENCE RATES")
    report.append("-"*70)
    
    top1_prefs = calculate_top1_preference(df, target_judge)
    for _, row in top1_prefs.iterrows():
        report.append(f"{row['vendor'].capitalize():10} {row['top1_percentage']:6.2f}% "
                     f"({row['top1_count']}/{row['total_judgments']})")
    
    report.append("\n" + "-"*70)
    report.append("AVERAGE SCORES BY VENDOR AND TIER")
    report.append("-"*70)
    
    avg_scores = calculate_average_scores(df, target_judge)
    for _, row in avg_scores.iterrows():
        report.append(f"{row['vendor'].capitalize():10} ({row['tier']:8}): "
                     f"{row['mean_score']:.2f} ± {row['std_score']:.2f}")
    
    report.append("\n" + "-"*70)
    report.append("SELF-BIAS DETECTION")
    report.append("-"*70)
    
    bias_results = detect_self_bias(df, target_vendor)
    if 'bias_analysis' in bias_results:
        ba = bias_results['bias_analysis']
        report.append(f"\n{target_vendor.upper()} judge ranks {target_vendor.upper()} #1: "
                     f"{ba['target_judge_rate']*100:.2f}% of the time")
        report.append(f"Other judges rank {target_vendor.upper()} #1: "
                     f"{ba['other_judges_avg_rate']*100:.2f}% (average)")
        report.append(f"\nBias difference: {ba['bias_percentage_points']:+.2f} percentage points")
        
        if ba['bias_difference'] > 0.1:
            report.append("⚠️  POTENTIAL SELF-BIAS DETECTED")
        elif ba['bias_difference'] < -0.1:
            report.append("⚠️  POTENTIAL SELF-PENALTY DETECTED")
        else:
            report.append("✓ No significant self-bias detected")
    
    report.append("\n" + "-"*70)
    report.append("STATISTICAL TESTS")
    report.append("-"*70)
    
    stat_tests = run_statistical_tests(df, target_vendor)
    
    chi2_test = stat_tests['chi_square_test']
    report.append(f"\nChi-square test: χ² = {chi2_test['chi2_statistic']:.3f}, "
                 f"p = {chi2_test['p_value']:.4f}")
    if chi2_test['significant_at_0.05']:
        report.append("✓ Significant at α=0.05 (preferences not uniform)")
    else:
        report.append("  Not significant at α=0.05")
    
    binom_test = stat_tests['binomial_test']
    report.append(f"\nBinomial test: p = {binom_test['p_value']:.4f}")
    report.append(f"Observed rate: {binom_test['observed_rate']*100:.2f}% vs "
                 f"Expected: {binom_test['expected_rate']*100:.2f}%")
    if binom_test['significant_at_0.05']:
        report.append("✓ Significant at α=0.05 (higher than expected)")
    else:
        report.append("  Not significant at α=0.05")
    
    report.append("\n" + "="*70)
    
    return "\n".join(report)
