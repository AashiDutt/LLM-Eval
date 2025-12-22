#!/usr/bin/env python3
"""
Analyze domain-wise breakdown for Experiment 2
"""
import json
from pathlib import Path
from collections import defaultdict

def analyze_domain_breakdown(judgments_file, answers_file):
    """Analyze self-bias and preferences by domain"""
    with open(answers_file, 'r') as f:
        answers = json.load(f)
    
    with open(judgments_file, 'r') as f:
        judgments = json.load(f)
    
    # Create answer lookup
    answer_lookup = {a['answer_id']: a for a in answers}
    
    # Statistics by category and judge
    category_stats = defaultdict(lambda: defaultdict(lambda: {
        'total': 0,
        'claude_top1': 0,
        'gemini_top1': 0,
        'gpt_top1': 0,
        'self_top1': 0
    }))
    
    for judgment in judgments:
        if 'error' in judgment:
            continue
        
        judge = judgment['judge_model']
        ranking = judgment['ranking']
        mapping = judgment['mapping']
        prompt_id = judgment['prompt_id']
        
        # Get category from first answer
        top_label = ranking[0]
        top_answer_id = mapping[top_label]
        top_answer = answer_lookup.get(top_answer_id)
        
        if not top_answer:
            continue
        
        category = top_answer['category']
        judge_vendor = judge.split('_')[0]
        
        category_stats[category][judge]['total'] += 1
        
        vendor = top_answer['model_vendor']
        if vendor == 'claude':
            category_stats[category][judge]['claude_top1'] += 1
        elif vendor == 'gemini':
            category_stats[category][judge]['gemini_top1'] += 1
        elif vendor == 'gpt':
            category_stats[category][judge]['gpt_top1'] += 1
        
        if vendor == judge_vendor:
            category_stats[category][judge]['self_top1'] += 1
    
    return category_stats

def calculate_vendor_self_bias_by_category(category_stats, vendor):
    """Calculate self-bias for a vendor by category"""
    results = {}
    
    for category in sorted(category_stats.keys()):
        vendor_judges = [j for j in category_stats[category].keys() if j.startswith(vendor)]
        if not vendor_judges:
            continue
        
        total_self = 0
        total_judgments = 0
        
        for judge in vendor_judges:
            stats = category_stats[category][judge]
            total_self += stats['self_top1']
            total_judgments += stats['total']
        
        rate = (total_self / total_judgments * 100) if total_judgments > 0 else 0
        results[category] = {
            'self_rate': rate,
            'total': total_judgments
        }
    
    return results

def calculate_cross_judge_preferences_by_category(category_stats, category):
    """Calculate cross-judge preferences for a category"""
    if category not in category_stats:
        return None
    
    judges = sorted(category_stats[category].keys())
    results = []
    
    for judge in judges:
        stats = category_stats[category][judge]
        total = stats['total']
        
        claude_pct = (stats['claude_top1'] / total * 100) if total > 0 else 0
        gemini_pct = (stats['gemini_top1'] / total * 100) if total > 0 else 0
        gpt_pct = (stats['gpt_top1'] / total * 100) if total > 0 else 0
        
        results.append({
            'judge': judge,
            'claude': claude_pct,
            'gemini': gemini_pct,
            'gpt': gpt_pct
        })
    
    return results

def main():
    base_dir = Path(__file__).parent
    answers_file = base_dir / 'data/answers/answers_mt_bench.json'
    judgments_file = base_dir / 'data/judgments/judgments_mt_bench.json'
    
    print("Analyzing domain-wise breakdown...")
    category_stats = analyze_domain_breakdown(judgments_file, answers_file)
    
    print("\n### Domain-wise Self-Bias Breakdown")
    print("\n| Category | GPT Self-Bias | Claude Self-Bias | Gemini Self-Bias |")
    print("|----------|---------------|------------------|------------------|")
    
    vendors = ['gpt', 'claude', 'gemini']
    categories = sorted(category_stats.keys())
    
    for category in categories:
        row = [category.capitalize()]
        for vendor in vendors:
            bias_data = calculate_vendor_self_bias_by_category(category_stats, vendor)
            if category in bias_data:
                rate = bias_data[category]['self_rate']
                row.append(f"{rate:.1f}%")
            else:
                row.append("N/A")
        print("| " + " | ".join(row) + " |")
    
    print("\n### Domain-wise Cross-Judge Preferences (GPT Selection %)")
    print("\n| Category | GPT Judge | Claude Judge | Gemini Judge |")
    print("|----------|-----------|--------------|--------------|")
    
    for category in categories:
        prefs = calculate_cross_judge_preferences_by_category(category_stats, category)
        if prefs:
            gpt_judge_pct = next((p['gpt'] for p in prefs if p['judge'].startswith('gpt')), 0)
            claude_judge_pct = next((p['gpt'] for p in prefs if p['judge'].startswith('claude')), 0)
            gemini_judge_pct = next((p['gpt'] for p in prefs if p['judge'].startswith('gemini')), 0)
            
            print(f"| {category.capitalize()} | {gpt_judge_pct:.1f}% | {claude_judge_pct:.1f}% | {gemini_judge_pct:.1f}% |")

if __name__ == '__main__':
    main()

