#!/usr/bin/env python3
"""
Build citation network graph from paper collection

Generic utility script - builds graph structure for LLM to analyze.
Does NOT apply algorithms - just provides graph data.
"""

import json
import argparse
from typing import List, Dict, Any, Tuple


def build_network(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build citation network structure

    Returns graph data (nodes, edges, basic stats).
    LLM will analyze this to identify influential papers, communities, etc.
    """
    # Create nodes (papers)
    nodes = []
    for p in papers:
        node = {
            'id': p.get('id') or p.get('doi') or p.get('title', ''),
            'title': p.get('title', ''),
            'year': p.get('year'),
            'citations': p.get('citations') or p.get('citationCount', 0),
            'authors': p.get('authors', [])[:5],  # First 5 authors
            'venue': p.get('venue') or p.get('_source', ''),
        }
        nodes.append(node)

    # Build edges (citations)
    # Note: Most APIs don't return full reference lists
    # We'll use citation counts as proxy for influence
    edges = []
    for i, p1 in enumerate(papers):
        for j, p2 in enumerate(papers):
            if i != j:
                # If p2 cites p1 (would need reference data)
                # For now, create edges based on conceptual similarity
                # LLM can analyze connections
                pass

    # Calculate basic statistics
    stats = {
        'total_papers': len(papers),
        'total_citations': sum(p.get('citations') or p.get('citationCount', 0) for p in papers),
        'avg_citations': sum(p.get('citations') or p.get('citationCount', 0) for p in papers) / len(papers) if papers else 0,
        'year_range': {
            'min': min(p.get('year', 2025) for p in papers),
            'max': max(p.get('year', 2025) for p in papers),
        }
    }

    return {
        'nodes': nodes,
        'edges': edges,  # Empty without full reference data
        'stats': stats,
    }


def main():
    parser = argparse.ArgumentParser(description='Build citation network from papers')
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

    print(f"Building network from {len(papers)} papers...")

    # Build network
    network = build_network(papers)

    # Save results
    with open(args.output, 'w') as f:
        json.dump(network, f, indent=2)

    print(f"✓ Network structure saved to {args.output}")
    print(f"  Nodes: {len(network['nodes'])}")
    print(f"  Stats: {network['stats']}")


if __name__ == "__main__":
    main()
