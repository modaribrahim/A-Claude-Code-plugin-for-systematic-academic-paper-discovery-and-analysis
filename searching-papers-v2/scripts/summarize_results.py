"""
Summarize and Finalize Paper Collection

Generate a summary of the final paper collection for user review.
This is the last script that provides statistics and insights.

Usage:
    python scripts/summarize_results.py --input artifacts/expanded.json \
                                        --output artifacts/summary.json
"""

import json
import argparse
from typing import Dict, List
from collections import Counter


def generate_summary(papers: List[Dict]) -> Dict:
    """
    Generate comprehensive summary of paper collection

    Args:
        papers: List of paper dictionaries

    Returns:
        Summary dictionary
    """
    if not papers:
        return {
            'total_papers': 0,
            'message': 'No papers found'
        }

    # Basic stats
    total = len(papers)

    # Year distribution
    years = [p.get('year') for p in papers if p.get('year')]
    year_dist = Counter(years)

    # Venue distribution
    venues = [p.get('venue') for p in papers if p.get('venue')]
    venue_dist = Counter(venues).most_common(10)

    # Top authors
    all_authors = []
    for p in papers:
        authors = p.get('authors', [])
        if authors and len(authors) > 0:
            all_authors.append(authors[0])  # First author
    author_dist = Counter(all_authors).most_common(10)

    # Concepts/keywords
    all_concepts = []
    for p in papers:
        concepts = p.get('concepts', [])
        all_concepts.extend(concepts)
    concept_dist = Counter(all_concepts).most_common(15)

    # Citation stats (for non-arXiv papers)
    citations = [p.get('citations', 0) for p in papers if p.get('citations', 0) > 0]
    citation_stats = {}
    if citations:
        citation_stats = {
            'min': min(citations),
            'max': max(citations),
            'avg': sum(citations) // len(citations),
            'median': sorted(citations)[len(citations) // 2]
        }

    # Open access stats
    oa_count = sum(1 for p in papers if p.get('is_oa', False))
    oa_percentage = (oa_count / total * 100) if total > 0 else 0

    # Source distribution
    sources = [p.get('_source', p.get('_rank_source', 'unknown')) for p in papers]
    source_dist = Counter(sources)

    return {
        'total_papers': total,
        'year_distribution': dict(year_dist.most_common(10)),
        'top_venues': venue_dist,
        'top_authors': author_dist,
        'top_concepts': concept_dist,
        'citation_statistics': citation_stats,
        'open_access': {
            'count': oa_count,
            'percentage': round(oa_percentage, 1)
        },
        'source_distribution': dict(source_dist),
        'year_range': {
            'earliest': min(years) if years else None,
            'latest': max(years) if years else None
        }
    }


def main():
    parser = argparse.ArgumentParser(description='Summarize final paper collection')
    parser.add_argument('--input', required=True, help='Input JSON file with final papers')
    parser.add_argument('--output', required=True, help='Output JSON file for summary')

    args = parser.parse_args()

    # Load papers
    with open(args.input, 'r') as f:
        papers = json.load(f)

    print("Generating summary of paper collection...\n")

    # Generate summary
    summary = generate_summary(papers)

    # Print summary
    print(f"Total papers: {summary['total_papers']}\n")

    print("Year distribution:")
    for year, count in summary['year_distribution'].items():
        print(f"  {year}: {count}")

    print(f"\nYear range: {summary['year_range']['earliest']} - {summary['year_range']['latest']}")

    print("\nTop venues:")
    for venue, count in summary['top_venues']:
        print(f"  {venue}: {count}")

    print("\nTop concepts:")
    for concept, count in summary['top_concepts']:
        print(f"  {concept}: {count}")

    if summary['citation_statistics']:
        print("\nCitation statistics:")
        stats = summary['citation_statistics']
        print(f"  Range: {stats['min']} - {stats['max']}")
        print(f"  Average: {stats['avg']}")
        print(f"  Median: {stats['median']}")

    print(f"\nOpen access: {summary['open_access']['count']} ({summary['open_access']['percentage']}%)")

    print("\nSource distribution:")
    for source, count in summary['source_distribution'].items():
        print(f"  {source}: {count}")

    # Save summary
    with open(args.output, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Summary saved to {args.output}")


if __name__ == "__main__":
    main()
