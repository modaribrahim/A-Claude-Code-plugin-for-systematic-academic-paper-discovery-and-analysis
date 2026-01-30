#!/usr/bin/env python3
"""
Extract structured data from paper collection

Generic utility script - extracts all metadata without filtering or keyword matching.
Output is meant for LLM to analyze and discover patterns.
"""

import json
import argparse
from typing import List, Dict, Any


def extract_paper_data(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract structured data from papers

    Returns all available metadata - no filtering, no keyword matching.
    LLM will discover patterns from this data.
    """
    extracted = []

    for p in papers:
        data = {
            'id': p.get('id') or p.get('doi') or p.get('title', ''),
            'title': p.get('title', ''),
            'abstract': p.get('abstract', ''),
            'year': p.get('year'),
            'authors': p.get('authors', []),
            'venue': p.get('venue') or p.get('journal_ref') or p.get('_source', ''),
            'citations': p.get('citations') or p.get('citationCount') or p.get('citation_count', 0),
            'url': p.get('url') or p.get('arxiv_id', ''),
            'categories': p.get('categories') or p.get('primary_category', ''),
            'doi': p.get('doi', ''),
            'published_date': p.get('published_date', ''),
            'source': p.get('_source', ''),
        }

        # Add any other fields present
        for key, value in p.items():
            if key not in data:
                data[key] = value

        extracted.append(data)

    return extracted


def main():
    parser = argparse.ArgumentParser(description='Extract structured data from papers')
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

    print(f"Extracting data from {len(papers)} papers...")

    # Extract structured data
    extracted = extract_paper_data(papers)

    # Save results
    with open(args.output, 'w') as f:
        json.dump(extracted, f, indent=2)

    print(f"✓ Extracted {len(extracted)} papers to {args.output}")
    print(f"  Fields available: title, abstract, year, authors, venue, citations, url, categories")


if __name__ == "__main__":
    main()
