"""
Citation Expansion (Backward Citation Search)

Find papers that CITE the seed papers (cited-by search).
This expands the collection by finding papers that build on the seed papers.

This is Stage 5 of the workflow - takes seed papers and finds their citations.

Usage:
    python scripts/citation_expand.py --input artifacts/deduplicated.json \
                                      --max-total 100 \
                                      --openalex-key KEY \
                                      --ss-key KEY \
                                      --output artifacts/expanded.json

Strategy:
    - For each seed paper, find papers that cite it
    - Deduplicate results
    - Limit to max_total papers total
    - Gather full metadata
"""

import sys
import os
import json
import argparse
from typing import List, Dict, Set

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from openalex_client import OpenAlexClient
from semantic_scholar_client import SemanticScholarClient


def get_cited_by_openalex(paper_ids: List[str], api_key: str = None, limit_per_paper: int = 20) -> List[Dict]:
    """
    Get papers that cite the given papers using OpenAlex

    Args:
        paper_ids: List of OpenAlex paper IDs
        api_key: OpenAlex API key
        limit_per_paper: Max citing papers to retrieve per seed paper

    Returns:
        List of citing papers
    """
    client = OpenAlexClient(api_key=api_key, rate_limit=100)

    all_citing_papers = []
    seen_ids = set()

    for paper_id in paper_ids[:20]:  # Limit to 20 seed papers to avoid API explosion
        try:
            # Extract just the ID part if it's a URL
            if '/' in paper_id:
                paper_id = paper_id.split('/')[-1]

            # Build filter for papers that cite this paper
            citing_works = client.get_works(
                filters={'cited_by': paper_id},
                max_results=limit_per_paper
            )

            for work in citing_works:
                work_id = work.get('id')
                if work_id and work_id not in seen_ids:
                    seen_ids.add(work_id)

                    # Normalize paper
                    from openalex_client import reconstruct_abstract
                    abstract_inv = work.get('abstract_inverted_index')
                    abstract = reconstruct_abstract(abstract_inv) if abstract_inv else ""

                    open_access = work.get('open_access') or {}
                    primary_location = work.get('primary_location') or {}
                    source = primary_location.get('source') or {}

                    citing_paper = {
                        'id': work_id,
                        'title': work.get('title', ''),
                        'abstract': abstract,
                        'year': work.get('publication_year'),
                        'type': work.get('type'),
                        'citations': work.get('cited_by_count', 0),
                        'is_oa': open_access.get('is_oa', False),
                        'oa_status': open_access.get('oa_status', ''),
                        'doi': work.get('doi', ''),
                        'concepts': [c.get('display_name') for c in (work.get('concepts') or [])[:5]],
                        'authors': [a.get('author', {}).get('display_name') for a in (work.get('authorships') or [])[:10] if a.get('author')],
                        'venue': source.get('display_name', ''),
                        'venue_id': source.get('id', ''),
                        '_seed_source': 'openalex'
                    }
                    all_citing_papers.append(citing_paper)

        except Exception as e:
            print(f"  Warning: Could not get citations for {paper_id}: {e}")
            continue

    return all_citing_papers


def get_cited_by_semantic_scholar(paper_ids: List[str], api_key: str = None, limit_per_paper: int = 20) -> List[Dict]:
    """
    Get papers that cite the given papers using Semantic Scholar

    Args:
        paper_ids: List of Semantic Scholar paper IDs
        api_key: Semantic Scholar API key
        limit_per_paper: Max citing papers to retrieve per seed paper

    Returns:
        List of citing papers
    """
    client = SemanticScholarClient(api_key=api_key, rate_limit=1)

    all_citing_papers = []
    seen_ids = set()

    from semantic_scholar_client import build_fields_from_requirements
    fields = build_fields_from_requirements(
        require_abstract=True,
        require_authors=True,
        require_citations=True,
        require_venue=True
    )

    for paper_id in paper_ids[:20]:  # Limit to 20 seed papers
        try:
            # Get citations (papers that cite this paper)
            response = client._make_request(
                f'paper/{paper_id}/citations',
                params={'limit': limit_per_paper, 'fields': ','.join(fields)},
                base_url=client.graph_api_base
            )

            citations = response.get('data', [])

            for citation_data in citations:
                citing_paper = citation_data.get('citingPaper', {})
                paper_id_new = citing_paper.get('paperId')

                if not paper_id_new or paper_id_new in seen_ids:
                    continue

                seen_ids.add(paper_id_new)

                # Normalize
                from semantic_scholar_client import normalize_paper
                normalized = normalize_paper(citing_paper)
                normalized['_seed_source'] = 'semantic_scholar'

                all_citing_papers.append(normalized)

        except Exception as e:
            print(f"  Warning: Could not get citations for {paper_id}: {e}")
            continue

    return all_citing_papers


def main():
    parser = argparse.ArgumentParser(description='Expand papers by citation (cited-by search)')
    parser.add_argument('--input', required=True, help='Input JSON file with seed papers (deduplicated)')
    parser.add_argument('--max-total', type=int, default=100, help='Maximum total papers to retrieve')
    parser.add_argument('--per-paper-limit', type=int, default=20,
                       help='Max citing papers to retrieve per seed paper')
    parser.add_argument('--openalex-key', help='OpenAlex API key')
    parser.add_argument('--ss-key', help='Semantic Scholar API key')
    parser.add_argument('--sources', nargs='+', default=['openalex', 'semantic_scholar'],
                       help='Sources to use for citation search')
    parser.add_argument('--output', required=True, help='Output JSON file path')

    args = parser.parse_args()

    # Load seed papers
    with open(args.input, 'r') as f:
        seed_papers = json.load(f)

    print(f"Citation expansion: Finding papers that cite {len(seed_papers)} seed papers")
    print(f"Max total papers: {args.max_total}")
    print(f"Sources: {args.sources}\n")

    all_expanded = []
    papers_per_source = args.max_total // len(args.sources)

    # OpenAlex citation search
    if 'openalex' in args.sources:
        print("Searching OpenAlex for cited-by papers...")

        # Get OpenAlex paper IDs
        openalex_ids = [p['id'] for p in seed_papers if 'openalex.org' in p.get('id', '')]
        print(f"  Found {len(openalex_ids)} OpenAlex seed papers")

        if openalex_ids:
            citing_papers = get_cited_by_openalex(
                openalex_ids,
                api_key=args.openalex_key,
                limit_per_paper=args.per_paper_limit
            )
            print(f"  Found {len(citing_papers)} citing papers")

            # Limit
            citing_papers = citing_papers[:papers_per_source]
            all_expanded.extend(citing_papers)

    # Semantic Scholar citation search
    if 'semantic_scholar' in args.sources:
        print("\nSearching Semantic Scholar for cited-by papers...")

        # Get Semantic Scholar paper IDs
        ss_ids = [p['id'] for p in seed_papers if not p.get('id', '').startswith('http') and not 'arxiv' in p.get('id', '').lower()]
        print(f"  Found {len(ss_ids)} Semantic Scholar seed papers")

        if ss_ids:
            citing_papers = get_cited_by_semantic_scholar(
                ss_ids,
                api_key=args.ss_key,
                limit_per_paper=args.per_paper_limit
            )
            print(f"  Found {len(citing_papers)} citing papers")

            # Limit
            citing_papers = citing_papers[:papers_per_source]
            all_expanded.extend(citing_papers)

    # Deduplicate expanded papers
    print(f"\nDeduplicating {len(all_expanded)} expanded papers...")
    from utils.deduplication import PaperDeduplicator
    dedup = PaperDeduplicator()
    unique_expanded = dedup.deduplicate_papers(all_expanded, aggressive=False)

    print(f"  {len(unique_expanded)} unique expanded papers")

    # Combine seed + expanded
    final_papers = seed_papers + unique_expanded

    # Limit to max_total
    if len(final_papers) > args.max_total:
        print(f"\nLimiting to {args.max_total} total papers...")
        # Prioritize seed papers, then add expanded
        final_papers = final_papers[:args.max_total]

    # Save results
    with open(args.output, 'w') as f:
        json.dump(final_papers, f, indent=2)

    print(f"\n✓ Expanded results saved to {args.output}")
    print(f"  Seed papers: {len(seed_papers)}")
    print(f"  Expanded papers: {len(unique_expanded)}")
    print(f"  Total papers: {len(final_papers)}")


if __name__ == "__main__":
    main()
