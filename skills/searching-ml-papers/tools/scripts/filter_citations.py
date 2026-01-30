"""
Filter Papers by Citation Count

Keep only the top N most cited papers from each source.
This is a pure utility - no AI logic.

Usage:
    python scripts/filter_citations.py --input artifacts/search_results.json \
                                       --top-n 200 \
                                       --output artifacts/filtered_by_citations.json

Note: arXiv papers don't have citation counts - they will be sorted by recency instead.
"""

import json
import argparse
from typing import Dict, List


def filter_papers_by_citations(papers: List[Dict], top_n: int, source: str) -> List[Dict]:
    """
    Filter papers to keep top N by citation count

    Args:
        papers: List of paper dictionaries
        top_n: Number of top papers to keep
        source: Source name ('openalex', 'semantic_scholar', 'arxiv')

    Returns:
        Filtered list of papers
    """
    if source == 'arxiv':
        # arXiv doesn't have citations - sort by year (most recent first)
        filtered = sorted(
            papers,
            key=lambda p: p.get('year', 0),
            reverse=True
        )[:top_n]
    else:
        # OpenAlex and Semantic Scholar have citation counts
        filtered = sorted(
            papers,
            key=lambda p: p.get('citations', 0),
            reverse=True
        )[:top_n]

    return filtered


def main():
    parser = argparse.ArgumentParser(description='Filter papers by citation count')
    parser.add_argument('--input', required=True, help='Input JSON file from multi_search.py')
    parser.add_argument('--top-n', type=int, default=200, help='Number of top papers to keep per source')
    parser.add_argument('--output', required=True, help='Output JSON file path')

    args = parser.parse_args()

    # Load results
    with open(args.input, 'r') as f:
        data = json.load(f)

    print(f"Filtering to top {args.top_n} papers per source by citations...")

    filtered = {}
    for source, papers in data.items():
        print(f"\n{source}: {len(papers)} papers")

        if len(papers) == 0:
            filtered[source] = []
            continue

        # Filter
        filtered_papers = filter_papers_by_citations(papers, args.top_n, source)

        print(f"  → Kept top {len(filtered_papers)}")

        # Show citation stats
        if source != 'arxiv':
            citations = [p.get('citations', 0) for p in filtered_papers]
            if citations:
                print(f"  Citation range: {min(citations)} - {max(citations)}")

        filtered[source] = filtered_papers

    # Save results
    with open(args.output, 'w') as f:
        json.dump(filtered, f, indent=2)

    total_papers = sum(len(papers) for papers in filtered.values())
    print(f"\n✓ Filtered results saved to {args.output}")
    print(f"  Total papers after filtering: {total_papers}")


if __name__ == "__main__":
    main()
