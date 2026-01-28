"""
Multi-Source Paper Search

Execute searches across OpenAlex, Semantic Scholar, and arXiv simultaneously.
This is a pure utility script - no AI logic, just executes queries and returns results.

Usage:
    python scripts/multi_search.py --query "deep learning change detection" \
                                    --year-from 2020 \
                                    --output artifacts/search_results.json

Output:
    JSON file with structure:
    {
        "openalex": [...],
        "semantic_scholar": [...],
        "arxiv": [...]
    }
"""

import sys
import os
import json
import argparse
from typing import Dict, List

# Add parent directory to path to import clients
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from openalex_client import OpenAlexClient
from semantic_scholar_client import SemanticScholarClient
from arxiv_client import ArxivClient


def search_openalex(
    query: str,
    year_from: int = None,
    year_to: int = None,
    min_citations: int = None,
    max_results: int = 500,
    api_key: str = None
) -> List[Dict]:
    """
    Search OpenAlex for papers

    Args:
        query: Search query string
        year_from: Earliest publication year
        year_to: Latest publication year
        min_citations: Minimum citation count
        max_results: Maximum results to return
        api_key: OpenAlex API key (optional)

    Returns:
        List of paper dictionaries
    """
    client = OpenAlexClient(api_key=api_key, rate_limit=100)

    # Build filters (use correct OpenAlex filter names)
    filters = {}
    if year_from:
        filters['from-publication-year'] = year_from
    if year_to:
        filters['to-publication-year'] = year_to
    # Note: min_citations is handled via sort parameter instead

    # Build query spec
    query_spec = {'query': query, 'filters': filters}

    # Execute search
    select_fields = [
        'id', 'title', 'publication_year', 'type', 'cited_by_count',
        'primary_location', 'authorships', 'concepts', 'open_access',
        'doi', 'abstract_inverted_index'
    ]

    works = client.get_works(
        filters=filters if filters else None,
        search=query if query else None,
        select=select_fields,
        max_results=max_results,
        sort='cited_by_count:desc'
    )

    # Normalize papers
    from openalex_client import reconstruct_abstract
    papers = []
    for work in works:
        if not work:
            continue

        abstract_inv = work.get('abstract_inverted_index')
        abstract = reconstruct_abstract(abstract_inv) if abstract_inv else ""

        open_access = work.get('open_access') or {}
        primary_location = work.get('primary_location') or {}
        source = primary_location.get('source') or {}

        paper = {
            'id': work.get('id'),
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
            'venue_id': source.get('id', '')
        }
        papers.append(paper)

    return papers


def search_semantic_scholar(
    query: str,
    year_from: int = None,
    year_to: int = None,
    min_citations: int = None,
    fields_of_study: List[str] = None,
    venue: str = None,
    max_results: int = 500,
    api_key: str = None
) -> List[Dict]:
    """
    Search Semantic Scholar for papers

    Args:
        query: Search query string
        year_from: Earliest publication year
        year_to: Latest publication year
        min_citations: Minimum citation count
        fields_of_study: Field of study filters
        venue: Venue name filter
        max_results: Maximum results to return
        api_key: Semantic Scholar API key (optional)

    Returns:
        List of paper dictionaries
    """
    client = SemanticScholarClient(api_key=api_key, rate_limit=1)

    # Build year range
    year = None
    if year_from and year_to:
        year = f"{year_from}-{year_to}"
    elif year_from:
        year = f"{year_from}-"
    elif year_to:
        year = f"-{year_to}"

    # Build fields to request
    from semantic_scholar_client import build_fields_from_requirements
    fields = build_fields_from_requirements(
        require_abstract=True,
        require_authors=True,
        require_citations=True,
        require_venue=True
    )

    # Execute search (get up to 100 per request, paginate if needed)
    papers = []
    offset = 0
    limit = 100  # Semantic Scholar max per request

    while len(papers) < max_results:
        response = client.search_papers(
            query=query,
            fields=fields,
            year=year,
            venue=venue,
            fields_of_study=','.join(fields_of_study) if fields_of_study else None,
            min_citation_count=min_citations,
            limit=min(limit, max_results - len(papers)),
            offset=offset
        )

        raw_papers = response.get('data', [])
        if not raw_papers:
            break

        from semantic_scholar_client import normalize_paper
        for raw_paper in raw_papers:
            normalized = normalize_paper(raw_paper)
            papers.append(normalized)

        offset += limit

        # Check if we've got all results
        total = response.get('total', 0)
        if len(papers) >= total or len(papers) >= max_results:
            break

    return papers[:max_results]


def search_arxiv(
    query: str,
    categories: List[str] = None,
    year_from: int = None,
    year_to: int = None,
    max_results: int = 500
) -> List[Dict]:
    """
    Search arXiv for papers

    Args:
        query: Search query string
        categories: arXiv categories (e.g., ['cs.CV', 'cs.LG'])
        year_from: Earliest publication year
        year_to: Latest publication year
        max_results: Maximum results to return

    Returns:
        List of paper dictionaries
    """
    client = ArxivClient(rate_limit=3)

    # Build filters
    filters = {}
    if year_from:
        filters['year_from'] = year_from
    if year_to:
        filters['year_to'] = year_to

    papers = client.search_papers(
        query=query,
        max_results=max_results,
        sort_by='relevance',
        categories=categories,
        filters=filters if filters else None
    )

    return papers


def main():
    parser = argparse.ArgumentParser(description='Search multiple academic sources for papers')
    parser.add_argument('--query', required=True, help='Search query string')
    parser.add_argument('--year-from', type=int, help='Earliest publication year')
    parser.add_argument('--year-to', type=int, help='Latest publication year')
    parser.add_argument('--min-citations', type=int, help='Minimum citation count (OpenAlex/Semantic Scholar)')
    parser.add_argument('--fields-of-study', nargs='+', help='Fields of study (Semantic Scholar)')
    parser.add_argument('--categories', nargs='+', help='arXiv categories (e.g., cs.CV cs.LG)')
    parser.add_argument('--venue', help='Venue name filter')
    parser.add_argument('--max-results', type=int, default=500, help='Maximum results per source')
    parser.add_argument('--openalex-key', help='OpenAlex API key')
    parser.add_argument('--ss-key', help='Semantic Scholar API key')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--sources', nargs='+', default=['openalex', 'semantic_scholar', 'arxiv'],
                       help='Sources to search (default: all three)')

    args = parser.parse_args()

    print(f"Searching for papers: {args.query}")
    print(f"Year range: {args.year_from}-{args.year_to}")
    print(f"Max results per source: {args.max_results}")
    print(f"Sources: {args.sources}\n")

    results = {}

    # Search OpenAlex
    if 'openalex' in args.sources:
        print("Searching OpenAlex...")
        try:
            results['openalex'] = search_openalex(
                query=args.query,
                year_from=args.year_from,
                year_to=args.year_to,
                min_citations=args.min_citations,
                max_results=args.max_results,
                api_key=args.openalex_key
            )
            print(f"  Found {len(results['openalex'])} papers\n")
        except Exception as e:
            print(f"  ✗ Error searching OpenAlex: {e}\n")
            results['openalex'] = []

    # Search Semantic Scholar
    if 'semantic_scholar' in args.sources:
        print("Searching Semantic Scholar...")
        try:
            results['semantic_scholar'] = search_semantic_scholar(
                query=args.query,
                year_from=args.year_from,
                year_to=args.year_to,
                min_citations=args.min_citations,
                fields_of_study=args.fields_of_study,
                venue=args.venue,
                max_results=args.max_results,
                api_key=args.ss_key
            )
            print(f"  Found {len(results['semantic_scholar'])} papers\n")
        except Exception as e:
            print(f"  ✗ Error searching Semantic Scholar: {e}\n")
            results['semantic_scholar'] = []

    # Search arXiv
    if 'arxiv' in args.sources:
        print("Searching arXiv...")
        try:
            results['arxiv'] = search_arxiv(
                query=args.query,
                categories=args.categories,
                year_from=args.year_from,
                year_to=args.year_to,
                max_results=args.max_results
            )
            print(f"  Found {len(results['arxiv'])} papers\n")
        except Exception as e:
            print(f"  ✗ Error searching arXiv: {e}\n")
            results['arxiv'] = []

    # Save results
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to {args.output}")

    # Print summary
    total_papers = sum(len(papers) for papers in results.values())
    print(f"\nSummary:")
    print(f"  Total papers found: {total_papers}")
    for source, papers in results.items():
        print(f"  {source}: {len(papers)}")


if __name__ == "__main__":
    main()
