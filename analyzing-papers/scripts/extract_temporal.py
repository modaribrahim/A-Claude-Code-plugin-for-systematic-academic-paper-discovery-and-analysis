#!/usr/bin/env python3
"""
Extract temporal data from paper collection

Generic utility script - groups papers by time for LLM to analyze trends.
Does NOT analyze trends - just provides temporal data.
"""

import json
import argparse
from typing import List, Dict, Any
from collections import defaultdict


def extract_temporal_data(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract temporal organization of papers

    Returns papers grouped by year/month.
    LLM will analyze this to identify trends, evolution, etc.
    """
    # Group by year
    by_year = defaultdict(list)
    for p in papers:
        year = p.get('year', 2025)
        by_year[year].append({
            'title': p.get('title', ''),
            'abstract': p.get('abstract', '')[:500],  # First 500 chars
            'citations': p.get('citations') or p.get('citationCount', 0),
            'authors': p.get('authors', [])[:3],
            'url': p.get('url', ''),
        })

    # Calculate year-over-year growth
    years = sorted(by_year.keys())
    growth = {}
    for i in range(1, len(years)):
        prev_year = years[i-1]
        curr_year = years[i]
        prev_count = len(by_year[prev_year])
        curr_count = len(by_year[curr_year])

        if prev_count > 0:
            growth_rate = ((curr_count - prev_count) / prev_count) * 100
            growth[f"{prev_year}->{curr_year}"] = {
                'prev_count': prev_count,
                'curr_count': curr_count,
                'growth_rate': round(growth_rate, 1),
            }

    return {
        'by_year': dict(by_year),
        'years': years,
        'total_years': len(years),
        'year_range': f"{years[0]}-{years[-1]}" if years else "N/A",
        'growth': growth,
    }


def main():
    parser = argparse.ArgumentParser(description='Extract temporal data from papers')
    parser.add_argument('--input', required=True, help='Input JSON file with papers')
    parser.add_argument('--output', required=True, help='Output JSON file')

    args = parser.parse_args()

    # Load papers
    with open(args.input, 'r') as f:
        data = json.load(f)

    papers = data if isinstance(data, list) else [data] if isinstance(data, dict) else []

    if not papers:
        print("No papers found in input")
        return

    print(f"Extracting temporal data from {len(papers)} papers...")

    # Extract temporal data
    temporal = extract_temporal_data(papers)

    # Save results
    with open(args.output, 'w') as f:
        json.dump(temporal, f, indent=2)

    print(f"✓ Temporal data saved to {args.output}")
    print(f"  Year range: {temporal['year_range']}")
    print(f"  Years: {len(temporal['years'])}")
    for year in temporal['years']:
        print(f"    {year}: {len(temporal['by_year'][year])} papers")


if __name__ == "__main__":
    main()
