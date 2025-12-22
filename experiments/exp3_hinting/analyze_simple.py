#!/usr/bin/env python3
"""
Simple analysis script that doesn't require pandas
"""
import json
from pathlib import Path
from collections import defaultdict

def analyze_judgments(judgments_file, answers_file, hint_group_name):
    """Analyze judgments and return statistics"""
    with open(answers_file, 'r') as f:
        answers = json.load(f)
    
    with open(judgments_file, 'r') as f:
        judgments = json.load(f)
    
    # Create answer lookup
    answer_lookup = {a['answer_id']: a for a in answers}
    
    # Statistics
    judge_stats = defaultdict(lambda: {
        'total': 0,
        'claude_top1': 0,
        'gemini_top1': 0,
        'gpt_top1': 0,
        'self_top1': 0
    })
    
    for judgment in judgments:
        if 'error' in judgment:
            continue
        
        judge = judgment['judge_model']
        ranking = judgment['ranking']
        mapping = judgment['mapping']
        
        # Get top-ranked answer
        top_label = ranking[0]
        top_answer_id = mapping[top_label]
        top_answer = answer_lookup.get(top_answer_id)
        
        if not top_answer:
            continue
        
        judge_stats[judge]['total'] += 1
        vendor = top_answer['model_vendor']
        
        if vendor == 'claude':
            judge_stats[judge]['claude_top1'] += 1
        elif vendor == 'gemini':
            judge_stats[judge]['gemini_top1'] += 1
        elif vendor == 'gpt':
            judge_stats[judge]['gpt_top1'] += 1
        
        # Check self-bias
        judge_vendor = judge.split('_')[0]
        if vendor == judge_vendor:
            judge_stats[judge]['self_top1'] += 1
    
    return judge_stats

def calculate_vendor_self_bias(judge_stats, vendor):
    """Calculate average self-bias for a vendor"""
    vendor_judges = [j for j in judge_stats.keys() if j.startswith(vendor)]
    if not vendor_judges:
        return 0
    
    total_self = 0
    total_judgments = 0
    
    for judge in vendor_judges:
        stats = judge_stats[judge]
        total_self += stats['self_top1']
        total_judgments += stats['total']
    
    return (total_self / total_judgments * 100) if total_judgments > 0 else 0

def main():
    base_dir = Path(__file__).parent
    # Try multiple possible answer file names
    answers_file = base_dir / 'data/answers/answers.json'
    if not answers_file.exists():
        answers_file = base_dir / 'data/answers/answers_mt_bench.json'
    if not answers_file.exists():
        # Try symlink target
        answers_file = base_dir.parent / 'exp2_mt_bench/data/answers/answers_mt_bench.json'
    judgments_dir = base_dir / 'data/judgments'
    
    # Find files
    group2_file = judgments_dir / 'judgments_group2.json'
    group4_file = judgments_dir / 'judgments_group4.json'
    
    if not group2_file.exists():
        print(f"Error: {group2_file} not found")
        return
    
    print("="*70)
    print("EXPERIMENT 3: HINTING EFFECT ANALYSIS")
    print("="*70)
    
    # Analyze Group 2
    print("\nAnalyzing Group 2 (Competitors)...")
    group2_stats = analyze_judgments(group2_file, answers_file, "Group 2")
    
    group4_stats = None
    if group4_file.exists():
        print("Analyzing Group 4 (Blind)...")
        group4_stats = analyze_judgments(group4_file, answers_file, "Group 4")
    
    # 1. Self-Bias Summary
    print("\n### 1. Self-Bias Detection Summary")
    print("\n| Vendor | Group 2 (Competitors) | Group 4 (Blind) | Change (pp) | Verdict |")
    print("|--------|----------------------|-----------------|-------------|---------|")
    
    vendors = ['claude', 'gpt', 'gemini']
    for vendor in vendors:
        group2_rate = calculate_vendor_self_bias(group2_stats, vendor)
        
        if group4_stats:
            group4_rate = calculate_vendor_self_bias(group4_stats, vendor)
            change = group2_rate - group4_rate
            expected = 33.33
            
            if abs(group2_rate - expected) < 5:
                verdict = "✅ Least biased"
            elif group2_rate > expected + 15:
                verdict = "❌ Most biased"
            else:
                verdict = "⚠️ Mild bias"
            
            print(f"| **{vendor.upper()}** | {group2_rate:.2f}% | {group4_rate:.2f}% | {change:+.2f} | {verdict} |")
        else:
            expected = 33.33
            if abs(group2_rate - expected) < 5:
                verdict = "✅ Least biased"
            elif group2_rate > expected + 15:
                verdict = "❌ Most biased"
            else:
                verdict = "⚠️ Mild bias"
            print(f"| **{vendor.upper()}** | {group2_rate:.2f}% | N/A | N/A | {verdict} |")
    
    # 2. Cross-Judge Comparison
    print("\n### 2. Cross-Judge Comparison (Group 2 - Top-1 Selection %)")
    print("\n| Judge | Claude | Gemini | GPT |")
    print("|-------|--------|--------|-----|")
    
    for judge in sorted(group2_stats.keys()):
        stats = group2_stats[judge]
        total = stats['total']
        
        claude_pct = (stats['claude_top1'] / total * 100) if total > 0 else 0
        gemini_pct = (stats['gemini_top1'] / total * 100) if total > 0 else 0
        gpt_pct = (stats['gpt_top1'] / total * 100) if total > 0 else 0
        
        max_val = max(claude_pct, gemini_pct, gpt_pct)
        claude_str = f"**{claude_pct:.2f}**" if claude_pct == max_val else f"{claude_pct:.2f}"
        gemini_str = f"**{gemini_pct:.2f}**" if gemini_pct == max_val else f"{gemini_pct:.2f}"
        gpt_str = f"**{gpt_pct:.2f}**" if gpt_pct == max_val else f"{gpt_pct:.2f}"
        
        print(f"| {judge} | {claude_str} | {gemini_str} | {gpt_str} |")
    
    # 3. Comparison to baseline
    if group4_stats:
        print("\n### 3. Self-Bias Change from Baseline")
        print("\n| Vendor | Group 2 Rate | Group 4 Rate | Change (pp) | Effect |")
        print("|--------|--------------|--------------|------------|-------|")
        
        for vendor in vendors:
            group2_rate = calculate_vendor_self_bias(group2_stats, vendor)
            group4_rate = calculate_vendor_self_bias(group4_stats, vendor)
            change = group2_rate - group4_rate
            
            if change > 5:
                effect = "⚠️ Increased bias"
            elif change < -5:
                effect = "✅ Reduced bias"
            else:
                effect = "➡️ No change"
            
            print(f"| {vendor.upper()} | {group2_rate:.2f}% | {group4_rate:.2f}% | {change:+.2f} | {effect} |")
    
    print("\n" + "="*70)
    print("Analysis complete!")

if __name__ == '__main__':
    main()

