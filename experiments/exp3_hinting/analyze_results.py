#!/usr/bin/env python3
"""
Analyze Experiment 3 results and generate summary tables
"""
import sys
sys.path.insert(0, '../../src')

import json
import pandas as pd
import numpy as np
from pathlib import Path

def load_and_merge_data(answers_path: str, judgments_path: str, hint_group: str):
    """Load and merge answers with judgments"""
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
                'hint_group': hint_group,
                'rank': rank_idx + 1,
                'score': score,
                'is_top_ranked': rank_idx == 0
            })
    
    return pd.DataFrame(rows)

def calculate_self_bias(df, hint_group, vendor):
    """Calculate self-bias for a vendor in a hint group"""
    group_df = df[df['hint_group'] == hint_group]
    vendor_judges = [j for j in group_df['judge'].unique() if j.startswith(vendor)]
    
    results = []
    for judge in vendor_judges:
        judge_df = group_df[group_df['judge'] == judge]
        top1 = judge_df[judge_df['is_top_ranked'] == True]
        vendor_top1 = len(top1[top1['model_vendor'] == vendor])
        total = len(top1)
        rate = vendor_top1 / total if total > 0 else 0
        results.append(rate)
    
    return np.mean(results) * 100 if results else 0

def calculate_cross_judge_preferences(df, hint_group):
    """Calculate top-1 preferences for each judge"""
    group_df = df[df['hint_group'] == hint_group]
    judges = sorted(group_df['judge'].unique())
    
    results = []
    for judge in judges:
        judge_df = group_df[group_df['judge'] == judge]
        top1 = judge_df[judge_df['is_top_ranked'] == True]
        total = len(top1)
        
        claude_pct = (len(top1[top1['model_vendor'] == 'claude']) / total * 100) if total > 0 else 0
        gemini_pct = (len(top1[top1['model_vendor'] == 'gemini']) / total * 100) if total > 0 else 0
        gpt_pct = (len(top1[top1['model_vendor'] == 'gpt']) / total * 100) if total > 0 else 0
        
        results.append({
            'judge': judge,
            'claude': claude_pct,
            'gemini': gemini_pct,
            'gpt': gpt_pct
        })
    
    return pd.DataFrame(results)

def main():
    base_dir = Path(__file__).parent
    answers_path = base_dir / 'data/answers/answers.json'
    judgments_dir = base_dir / 'data/judgments'
    
    # Find judgment files
    group2_file = judgments_dir / 'judgments_group2.json'
    group4_file = judgments_dir / 'judgments_group4.json'
    
    # Fallback to other naming patterns
    if not group2_file.exists():
        for f in judgments_dir.glob('*.json'):
            if 'group2' in f.name.lower() or 'competitors' in f.name.lower():
                group2_file = f
                break
    
    if not group4_file.exists():
        for f in judgments_dir.glob('*.json'):
            if 'group4' in f.name.lower() or 'blind' in f.name.lower():
                if f.is_symlink() or 'judgments' in f.name.lower():
                    group4_file = f
                    break
    
    if not group2_file:
        print("Error: Could not find Group 2 (Competitors) judgment file")
        return
    
    print("Loading data...")
    df_group2 = load_and_merge_data(str(answers_path), str(group2_file), 'group2_competitors')
    print(f"✓ Group 2: {len(df_group2)} records")
    
    if group4_file:
        df_group4 = load_and_merge_data(str(answers_path), str(group4_file), 'group4_blind')
        print(f"✓ Group 4: {len(df_group4)} records")
        df_all = pd.concat([df_group2, df_group4], ignore_index=True)
    else:
        df_all = df_group2
        print("⚠ Group 4 (Blind) not found, analyzing Group 2 only")
    
    print("\n" + "="*70)
    print("EXPERIMENT 3: HINTING EFFECT ANALYSIS")
    print("="*70)
    
    # 1. Self-Bias Comparison
    print("\n### 1. Self-Bias Detection Summary")
    print("\n| Vendor | Group 2 (Competitors) | Group 4 (Blind) | Change (pp) | Verdict |")
    print("|--------|----------------------|-----------------|-------------|---------|")
    
    vendors = ['claude', 'gpt', 'gemini']
    for vendor in vendors:
        group2_rate = calculate_self_bias(df_all, 'group2_competitors', vendor)
        
        if group4_file:
            group4_rate = calculate_self_bias(df_all, 'group4_blind', vendor)
            change = group2_rate - group4_rate
            expected = 33.33
            
            # Determine verdict
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
    
    cross_judge = calculate_cross_judge_preferences(df_all, 'group2_competitors')
    for _, row in cross_judge.iterrows():
        # Find highest
        max_val = max(row['claude'], row['gemini'], row['gpt'])
        claude_str = f"**{row['claude']:.2f}**" if row['claude'] == max_val else f"{row['claude']:.2f}"
        gemini_str = f"**{row['gemini']:.2f}**" if row['gemini'] == max_val else f"{row['gemini']:.2f}"
        gpt_str = f"**{row['gpt']:.2f}**" if row['gpt'] == max_val else f"{row['gpt']:.2f}"
        
        print(f"| {row['judge']} | {claude_str} | {gemini_str} | {gpt_str} |")
    
    # 3. Comparison to baseline if available
    if group4_file:
        print("\n### 3. Self-Bias Change from Baseline")
        print("\n| Vendor | Group 2 Rate | Group 4 Rate | Change (pp) | Effect |")
        print("|--------|--------------|--------------|------------|-------|")
        
        for vendor in vendors:
            group2_rate = calculate_self_bias(df_all, 'group2_competitors', vendor)
            group4_rate = calculate_self_bias(df_all, 'group4_blind', vendor)
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

