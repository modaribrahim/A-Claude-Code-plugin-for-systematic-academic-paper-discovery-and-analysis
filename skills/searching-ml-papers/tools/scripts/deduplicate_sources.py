"""
Deduplicate Papers Across Sources

Remove duplicate papers found in multiple sources using DOI, title, and fuzzy matching.
This is a pure utility - no AI logic.

Usage:
    python scripts/deduplicate_sources.py --input artifacts/ranked_by_embeddings.json \
                                          --output artifacts/deduplicated.json

Strategy:
    1. DOI matching (exact) - most reliable
    2. Title + Year + First Author (normalized)
    3. Fuzzy title matching (optional, with --aggressive)
"""

import sys
import os
import json
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.deduplication import PaperDeduplicator


def main():
    parser = argparse.ArgumentParser(description='Deduplicate papers across sources')
    parser.add_argument('--input', required=True, help='Input JSON file from rank_embeddings.py')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--aggressive', action='store_true',
                       help='Use fuzzy title matching (slower but more thorough)')

    args = parser.parse_args()

    # Load ranked papers
    with open(args.input, 'r') as f:
        papers_by_source = json.load(f)

    print("Deduplicating papers across sources...")

    # Initialize deduplicator
    dedup = PaperDeduplicator()

    # Extract papers from each source
    openalex_papers = papers_by_source.get('openalex', [])
    semantic_scholar_papers = papers_by_source.get('semantic_scholar', [])
    arxiv_papers = papers_by_source.get('arxiv', [])

    print(f"\nPapers before deduplication:")
    print(f"  OpenAlex: {len(openalex_papers)}")
    print(f"  Semantic Scholar: {len(semantic_scholar_papers)}")
    print(f"  arXiv: {len(arxiv_papers)}")
    print(f"  Total: {len(openalex_papers) + len(semantic_scholar_papers) + len(arxiv_papers)}")

    # Deduplicate
    unique_papers, source_counts = dedup.deduplicate_cross_source(
        openalex_papers=openalex_papers,
        semantic_scholar_papers=semantic_scholar_papers,
        arxiv_papers=arxiv_papers,
        aggressive=args.aggressive
    )

    # Show results
    print(f"\nPapers after deduplication:")
    for source, count in source_counts.items():
        print(f"  {source}: {count}")
    print(f"  Total unique: {len(unique_papers)}")

    # Get deduplication stats
    stats = dedup.get_deduplication_stats()
    print(f"\nDeduplication statistics:")
    print(f"  Unique DOIs found: {stats['unique_dois']}")
    print(f"  Unique composite keys: {stats['unique_composite_keys']}")
    print(f"  Duplicates removed: {stats['duplicates_found']}")

    # Save results
    with open(args.output, 'w') as f:
        json.dump(unique_papers, f, indent=2)

    print(f"\n✓ Deduplicated papers saved to {args.output}")


if __name__ == "__main__":
    main()
