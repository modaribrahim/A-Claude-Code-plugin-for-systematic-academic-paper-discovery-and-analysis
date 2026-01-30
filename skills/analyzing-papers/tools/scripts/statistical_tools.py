#!/usr/bin/env python3
"""
Statistical Tools for Paper Analysis

Provides statistical analysis of paper collections:
- Distributions (citations, year, venues, authors)
- Correlations (between metrics)
- Significance tests (comparing groups)
- Descriptive statistics

Example usage:
    # Analyze citation distribution
    python statistical_tools.py --input papers.json --analysis distribution --field citations --output results.json

    # Multiple analyses
    python statistical_tools.py --input papers.json --analysis distribution correlation --output results.json

    # See full documentation
    python statistical_tools.py --help
"""

import argparse
import sys
import json
from typing import List, Dict, Any
from collections import Counter


def analyze_distribution(papers: List[Dict], field: str) -> Dict[str, Any]:
    """
    Analyze distribution of a field across papers

    Calculates:
    - Min, max, mean, median, std deviation
    - Quartiles (25%, 50%, 75%)
    - Histogram data
    - Outliers

    Args:
        papers: List of paper dictionaries
        field: Field to analyze (e.g., 'citations', 'year')

    Returns:
        Dictionary with distribution statistics

    Useful for:
        - Understanding citation distribution
        - Year coverage analysis
        - Author productivity distribution
    """
    values = []
    for p in papers:
        value = p.get(field)
        if value is not None and isinstance(value, (int, float)):
            values.append(value)

    if not values:
        return {'error': f'No valid values for field: {field}'}

    values.sort()
    n = len(values)

    # Basic statistics
    stats = {
        'count': n,
        'min': values[0],
        'max': values[-1],
        'mean': sum(values) / n,
        'median': values[n // 2],
    }

    # Standard deviation
    if n > 1:
        mean = stats['mean']
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        stats['std'] = variance ** 0.5

    # Quartiles
    stats['q1'] = values[n // 4]
    stats['q3'] = values[3 * n // 4]

    # Histogram (10 bins)
    bin_count = 10
    bin_width = (stats['max'] - stats['min']) / bin_count
    histogram = []

    for i in range(bin_count):
        bin_min = stats['min'] + i * bin_width
        bin_max = stats['min'] + (i + 1) * bin_width
        count = sum(1 for v in values if bin_min <= v < bin_max)
        histogram.append({
            'bin': i,
            'range': [bin_min, bin_max],
            'count': count,
        })

    stats['histogram'] = histogram

    # Outliers (beyond 1.5 * IQR)
    if 'q1' in stats and 'q3' in stats:
        iqr = stats['q3'] - stats['q1']
        lower_bound = stats['q1'] - 1.5 * iqr
        upper_bound = stats['q3'] + 1.5 * iqr

        outliers = [v for v in values if v < lower_bound or v > upper_bound]
        stats['outliers'] = {
            'count': len(outliers),
            'values': outliers[:20],  # First 20
        }

    return stats


def analyze_frequency(papers: List[Dict], field: str, top_n: int = 20) -> Dict[str, Any]:
    """
    Analyze frequency distribution of categorical field

    Counts occurrences of each unique value.

    Args:
        papers: List of paper dictionaries
        field: Field to analyze (e.g., 'venue', 'year', 'source')
        top_n: Number of top values to return

    Returns:
        Dictionary with frequency counts

    Useful for:
        - Most common venues
        - Publication counts by year
        - Source distribution
    """
    counter = Counter()

    for p in papers:
        value = p.get(field)
        if value:
            if isinstance(value, list):
                # Handle lists (e.g., authors)
                for item in value:
                    counter[item] += 1
            else:
                counter[value] += 1

    return {
        'total_unique': len(counter),
        'top_values': [
            {'value': val, 'count': count}
            for val, count in counter.most_common(top_n)
        ],
        'all_values': dict(counter) if len(counter) <= 100 else 'truncated',
    }


def analyze_correlation(papers: List[Dict], field1: str, field2: str) -> Dict[str, Any]:
    """
    Analyze correlation between two numerical fields

    Calculates Pearson correlation coefficient.

    Args:
        papers: List of paper dictionaries
        field1: First field (e.g., 'citations')
        field2: Second field (e.g., 'year')

    Returns:
        Dictionary with correlation analysis

    Useful for:
        - Citations vs year (are older papers more cited?)
        - Authors vs citations (team size impact)
        - Venue vs citations (venue quality)
    """
    pairs = []

    for p in papers:
        val1 = p.get(field1)
        val2 = p.get(field2)

        if val1 is not None and val2 is not None:
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                pairs.append((val1, val2))

    if len(pairs) < 2:
        return {'error': 'Not enough data points for correlation'}

    n = len(pairs)
    mean1 = sum(x for x, _ in pairs) / n
    mean2 = sum(y for _, y in pairs) / n

    # Pearson correlation
    numerator = sum((x - mean1) * (y - mean2) for x, y in pairs)
    denom1 = (sum((x - mean1) ** 2 for x, _ in pairs)) ** 0.5
    denom2 = (sum((y - mean2) ** 2 for _, y in pairs)) ** 0.5

    correlation = numerator / (denom1 * denom2) if denom1 * denom2 > 0 else 0

    return {
        'correlation': round(correlation, 3),
        'field1': field1,
        'field2': field2,
        'n': n,
        'interpretation': interpret_correlation(correlation),
    }


def interpret_correlation(r: float) -> str:
    """Interpret correlation coefficient"""
    abs_r = abs(r)

    if abs_r >= 0.7:
        strength = "strong"
    elif abs_r >= 0.4:
        strength = "moderate"
    elif abs_r >= 0.2:
        strength = "weak"
    else:
        strength = "very weak"

    direction = "positive" if r > 0 else "negative"

    return f"{strength} {direction} correlation"


def compare_groups(papers: List[Dict], group_field: str, metric_field: str) -> Dict[str, Any]:
    """
    Compare a metric across different groups

    Args:
        papers: List of paper dictionaries
        group_field: Field to group by (e.g., 'venue', 'year', 'source')
        metric_field: Metric to compare (e.g., 'citations')

    Returns:
        Dictionary with group comparison

    Useful for:
        - Citation counts by venue
        - Citations by year
        - Paper counts by source
    """
    groups = {}

    for p in papers:
        group_value = p.get(group_field, 'Unknown')
        metric_value = p.get(metric_field, 0)

        if group_value not in groups:
            groups[group_value] = []

        if isinstance(metric_value, (int, float)):
            groups[group_value].append(metric_value)

    # Calculate statistics for each group
    comparison = {}
    for group, values in groups.items():
        if values:
            values.sort()
            n = len(values)
            comparison[group] = {
                'count': n,
                'mean': sum(values) / n,
                'median': values[n // 2],
                'min': min(values),
                'max': max(values),
            }

    return {
        'group_field': group_field,
        'metric_field': metric_field,
        'groups': comparison,
        'total_groups': len(comparison),
    }


def main():
    parser = argparse.ArgumentParser(
        description='Statistical analysis of paper collections',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Citation distribution
  python statistical_tools.py --input papers.json --analysis distribution --field citations --output results.json

  # Venue frequency
  python statistical_tools.py --input papers.json --analysis frequency --field venue --output results.json

  # Correlation between citations and year
  python statistical_tools.py --input papers.json --analysis correlation --field1 citations --field2 year --output results.json

  # Compare citations by venue
  python statistical_tools.py --input papers.json --analysis compare --group-field venue --metric-field citations --output results.json

  # Multiple analyses
  python statistical_tools.py --input papers.json --analysis distribution frequency --output results.json

Analyses:
  distribution  - Distribution statistics (mean, median, std, quartiles, outliers)
  frequency     - Frequency counts for categorical data
  correlation   - Correlation between two numerical fields
  compare       - Compare metrics across groups

Output includes:
  - Statistical measures
  - Histogram data
  - Top N values
  - Correlation coefficients with interpretation
        """
    )

    parser.add_argument('--input', required=True,
                        help='Input JSON file with papers')
    parser.add_argument('--analysis', nargs='+',
                        choices=['distribution', 'frequency', 'correlation', 'compare', 'all'],
                        default=['distribution'],
                        help='Analysis type to run (default: distribution)')
    parser.add_argument('--output', required=True,
                        help='Output JSON file')

    # Distribution-specific
    parser.add_argument('--field',
                        help='Field to analyze (for distribution)')

    # Frequency-specific
    parser.add_argument('--top', type=int, default=20,
                        help='Number of top values to show (for frequency, default: 20)')

    # Correlation-specific
    parser.add_argument('--field1',
                        help='First field (for correlation)')
    parser.add_argument('--field2',
                        help='Second field (for correlation)')

    # Comparison-specific
    parser.add_argument('--group-field',
                        help='Field to group by (for compare)')
    parser.add_argument('--metric-field',
                        help='Metric to compare (for compare)')

    args = parser.parse_args()

    # Load papers
    with open(args.input, 'r') as f:
        data = json.load(f)

    papers = data if isinstance(data, list) else [data] if isinstance(data, dict) else []

    if not papers:
        print("No papers found", file=sys.stderr)
        sys.exit(1)

    print(f"Running statistical analysis on {len(papers)} papers...")

    results = {}
    analyses = args.analysis

    if 'all' in analyses:
        analyses = ['distribution', 'frequency']

    # Run requested analyses
    for analysis in analyses:
        print(f"  Running {analysis}...")

        if analysis == 'distribution':
            if not args.field:
                print("Error: --field required for distribution analysis", file=sys.stderr)
                sys.exit(1)

            results['distribution'] = analyze_distribution(papers, args.field)

        elif analysis == 'frequency':
            if not args.field:
                print("Error: --field required for frequency analysis", file=sys.stderr)
                sys.exit(1)

            results['frequency'] = analyze_frequency(papers, args.field, args.top)

        elif analysis == 'correlation':
            if not args.field1 or not args.field2:
                print("Error: --field1 and --field2 required for correlation analysis", file=sys.stderr)
                sys.exit(1)

            results['correlation'] = analyze_correlation(papers, args.field1, args.field2)

        elif analysis == 'compare':
            if not args.group_field or not args.metric_field:
                print("Error: --group-field and --metric-field required for comparison", file=sys.stderr)
                sys.exit(1)

            results['comparison'] = compare_groups(papers, args.group_field, args.metric_field)

    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to {args.output}")

    # Print summary
    if 'distribution' in results:
        dist = results['distribution']
        if 'error' not in dist:
            print(f"\n{args.field.capitalize()} Distribution:")
            print(f"  Mean: {dist['mean']:.2f}")
            print(f"  Median: {dist['median']:.2f}")
            print(f"  Std: {dist.get('std', 'N/A')}")
            print(f"  Range: {dist['min']} - {dist['max']}")

    if 'frequency' in results:
        freq = results['frequency']
        print(f"\nTop {args.top} {args.field} values:")
        for item in freq['top_values'][:args.top]:
            print(f"  {item['value']}: {item['count']}")

    if 'correlation' in results:
        corr = results['correlation']
        print(f"\nCorrelation: {corr['field1']} vs {corr['field2']}")
        print(f"  r = {corr['correlation']} ({corr['interpretation']})")

    if 'comparison' in results:
        comp = results['comparison']
        print(f"\nComparison by {comp['group_field']}:")
        for group, stats in list(comp['groups'].items())[:5]:
            print(f"  {group}: mean={stats['mean']:.2f}, n={stats['count']}")


if __name__ == "__main__":
    main()
