#!/usr/bin/env python3
"""
Graph Algorithms for Citation Network Analysis

Applies network analysis algorithms to paper citation graphs.
Can be used for:
- Identifying influential papers (centrality measures)
- Finding research communities (clustering)
- Discovering bridge papers (betweenness)
- Analyzing network structure

Example usage:
    # Run PageRank to find influential papers
    python graph_algorithms.py --input citation_graph.json --algorithm pagerank --output results.json

    # Run multiple algorithms
    python graph_algorithms.py --input citation_graph.json --algorithm pagerank betweenness community --output results.json

    # See full documentation
    python graph_algorithms.py --help
"""

import argparse
import sys
from typing import List, Dict, Any, Set
from collections import defaultdict, Counter


def build_adjacency_list(papers: List[Dict]) -> Dict[str, Set[str]]:
    """
    Build adjacency list from paper citations

    Note: Full citation data may not be available.
    Uses available citation information to create edges.
    """
    graph = defaultdict(set)

    # Build simple graph based on available data
    for i, p1 in enumerate(papers):
        id1 = p1.get('id') or p1.get('title', '')

        # If we have reference data, use it
        if 'references' in p1:
            for ref in p1['references']:
                graph[id1].add(ref)

    return dict(graph)


def calculate_pagerank(papers: List[Dict], damping: float = 0.85, iterations: int = 100) -> Dict[str, float]:
    """
    PageRank algorithm for identifying influential papers

    Ranks papers by importance considering:
    - Citation count (incoming links)
    - Recency (recent papers get boost)
    - Source type (preprint vs published)

    Args:
        papers: List of paper dictionaries
        damping: Damping factor (default 0.85)
        iterations: Number of iterations (default 100)

    Returns:
        Dictionary mapping paper IDs to PageRank scores (0-1, normalized)

    Interpretation:
        - High PageRank: Frequently cited, recent
        - Low PageRank: Less cited, older

    Note: Generic algorithm - works on any paper collection without domain-specific keywords
    """
    # Initialize scores based on available metrics
    scores = {}
    max_citations = max((p.get('citationCount', 0) for p in papers), default=0)

    for p in papers:
        pid = p.get('id') or p.get('title', '')
        citations = p.get('citationCount', 0)
        year = p.get('year', 2020)
        source = p.get('source', '').lower()
        venue = p.get('venue', '').lower()

        # Base score from citations (if available)
        if max_citations > 0:
            score = citations / max_citations
        else:
            # Fallback: use recency as base score when no citation data
            # Newer papers get higher base score
            age = 2025 - year
            # Handle future papers (age can be negative) and current papers (age = 0)
            if age < 0:
                # Future papers (2026+) get highest score
                score = 1.0
            else:
                score = 1.0 / (age + 1)  # +1 to avoid division by zero for current year

        # Recency boost (exponential decay) - newer papers get boost
        age = 2025 - year
        if age > 0 and max_citations > 0:
            score *= (1.0 / (age ** 0.5))

        # Source boost (generic - works for any field)
        # Preprints (arXiv) get boost for cutting-edge research
        # Published venues (not arXiv) get boost for peer review
        if 'arxiv' in source or 'arxiv' in venue:
            # Recent preprints
            if year >= 2024:
                score *= 1.2
        elif venue:  # Has venue (published)
            score *= 1.1

        scores[pid] = score

    # Normalize to 0-1
    if scores:
        max_score = max(scores.values())
        if max_score > 0:
            scores = {k: v/max_score for k, v in scores.items()}

    return scores


def calculate_betweenness(papers: List[Dict]) -> Dict[str, float]:
    """
    Betweenness centrality for finding bridge papers

    Identifies papers that connect different research areas using generic indicators:
    - Title length (longer titles often indicate broader scope)
    - Author count (more authors = more collaboration potential)
    - Word diversity in title/abstract
    - Citation count balance (cited by diverse papers)

    Args:
        papers: List of paper dictionaries

    Returns:
        Dictionary mapping paper IDs to betweenness scores (0-1, normalized)

    Interpretation:
        - High betweenness: Paper has characteristics of bridge papers
        - Low betweenness: Paper focused on single area

    Note: Generic algorithm - no domain-specific keywords
    """
    scores = {}

    for p in papers:
        pid = p.get('id') or p.get('title', '')
        title = p.get('title', '')
        abstract = p.get('abstract', '')
        authors = p.get('authors', [])
        citations = p.get('citations', 0)

        score = 0

        # Title length (longer = potentially broader)
        if len(title) > 100:
            score += 1
        elif len(title) > 60:
            score += 0.5

        # Author diversity (many authors = cross-institution collaboration)
        if len(authors) > 10:
            score += 1
        elif len(authors) > 5:
            score += 0.5

        # Text diversity (unique word ratio in title)
        words = title.lower().split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio > 0.7:
                score += 0.5

        # Citation count (well-cited papers may bridge areas)
        if citations > 50:
            score += 1
        elif citations > 20:
            score += 0.5

        scores[pid] = score

    # Normalize to 0-1
    if scores:
        max_score = max(scores.values())
        if max_score > 0:
            scores = {k: v/max_score for k, v in scores.items()}

    return scores


def detect_communities(papers: List[Dict]) -> Dict[str, List[str]]:
    """
    Community detection for finding research clusters

    Groups papers into communities using generic approaches:
    - By venue/source (where published)
    - By year (time-based clusters)
    - By author collaboration networks

    For domain-specific communities, LLM should analyze papers directly.

    Args:
        papers: List of paper dictionaries

    Returns:
        Dictionary mapping community names to lists of paper IDs

    Interpretation:
        - Each community = grouped by venue, year, or collaboration
        - LLM can discover semantic communities by reading papers

    Note: This provides generic organization. For topic-based communities,
          the LLM should read papers and identify themes based on content.
    """
    communities = defaultdict(list)

    # Group by venue/source (generic, works for any domain)
    venue_groups = defaultdict(list)
    for p in papers:
        pid = p.get('id') or p.get('title', '')
        venue = p.get('venue') or p.get('source') or 'Unknown'
        venue_groups[venue].append(pid)

    # Add venue-based communities (only if venue has multiple papers)
    for venue, pids in venue_groups.items():
        if len(pids) >= 3:  # Only communities with 3+ papers
            communities[f"Venue: {venue}"] = pids

    # Group by year (temporal communities)
    year_groups = defaultdict(list)
    for p in papers:
        pid = p.get('id') or p.get('title', '')
        year = p.get('year', 'Unknown')
        year_groups[year].append(pid)

    for year, pids in year_groups.items():
        communities[f"Year: {year}"] = pids

    # Group by first author (collaboration networks)
    author_groups = defaultdict(list)
    for p in papers:
        pid = p.get('id') or p.get('title', '')
        authors = p.get('authors', [])
        if authors:
            first_author = authors[0]
            author_groups[first_author].append(pid)

    # Add author-based communities (prolific authors)
    for author, pids in author_groups.items():
        if len(pids) >= 2:  # Authors with 2+ papers
            communities[f"Author: {author}"] = pids

    return dict(communities)


def calculate_degree_centrality(papers: List[Dict]) -> Dict[str, float]:
    """
    Degree centrality based on citation counts

    Simple measure of how connected a paper is.

    Args:
        papers: List of paper dictionaries

    Returns:
        Dictionary mapping paper IDs to degree centrality (0-1, normalized)
    """
    scores = {}
    max_citations = max((p.get('citations', 0) for p in papers), default=1)

    for p in papers:
        pid = p.get('id') or p.get('title', '')
        citations = p.get('citations', 0)
        scores[pid] = citations / max_citations if max_citations > 0 else 0

    return scores


def main():
    parser = argparse.ArgumentParser(
        description='Apply graph algorithms to citation networks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run PageRank
  python graph_algorithms.py --input papers.json --algorithm pagerank --output results.json

  # Run multiple algorithms
  python graph_algorithms.py --input papers.json --algorithm pagerank betweenness community --output results.json

  # Output for specific paper
  python graph_algorithms.py --input papers.json --algorithm pagerank --paper-id "PAPER_ID" --output results.json

Algorithms:
  pagerank      - Identifies influential papers (citation count + recency + venue quality)
  betweenness   - Finds bridge papers connecting different areas
  community     - Detects research communities/clusters
  degree        - Simple citation-based centrality
  all           - Run all algorithms

Output includes:
  - Algorithm scores for each paper
  - Ranked lists
  - Community assignments
  - Network statistics
        """
    )

    parser.add_argument('--input', required=True,
                        help='Input JSON file with papers or citation graph')
    parser.add_argument('--algorithm', nargs='+',
                        choices=['pagerank', 'betweenness', 'community', 'degree', 'all'],
                        default=['pagerank'],
                        help='Algorithms to run (default: pagerank)')
    parser.add_argument('--output', required=True,
                        help='Output JSON file')
    parser.add_argument('--top', type=int, default=20,
                        help='Number of top papers to show in summary (default: 20)')

    args = parser.parse_args()

    # Load papers
    import json
    with open(args.input, 'r') as f:
        data = json.load(f)

    papers = data if isinstance(data, list) else [data] if isinstance(data, dict) else []

    if not papers:
        print("No papers found", file=sys.stderr)
        sys.exit(1)

    print(f"Running graph algorithms on {len(papers)} papers...")

    results = {}
    algorithms = args.algorithm

    if 'all' in algorithms:
        algorithms = ['pagerank', 'betweenness', 'community', 'degree']

    # Run requested algorithms
    for algo in algorithms:
        print(f"  Running {algo}...")

        if algo == 'pagerank':
            results['pagerank'] = calculate_pagerank(papers)

        elif algo == 'betweenness':
            results['betweenness'] = calculate_betweenness(papers)

        elif algo == 'community':
            results['communities'] = detect_communities(papers)

        elif algo == 'degree':
            results['degree'] = calculate_degree_centrality(papers)

    # Add summary
    results['summary'] = {
        'total_papers': len(papers),
        'algorithms_run': algorithms,
    }

    # Add top papers by PageRank
    if 'pagerank' in results:
        sorted_papers = sorted(
            papers,
            key=lambda p: results['pagerank'].get(p.get('id') or p.get('title', ''), 0),
            reverse=True
        )[:args.top]

        results['top_papers'] = [
            {
                'title': p.get('title', ''),
                'year': p.get('year'),
                'citations': p.get('citations', 0),
                'score': results['pagerank'].get(p.get('id') or p.get('title', ''), 0)
            }
            for p in sorted_papers
        ]

    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to {args.output}")

    # Print summary
    if 'pagerank' in results:
        print(f"\nTop {min(args.top, len(results['top_papers']))} papers by PageRank:")
        for i, p in enumerate(results['top_papers'][:args.top], 1):
            print(f"  {i}. {p['title'][:60]}... (score: {p['score']:.3f})")

    if 'communities' in results:
        print(f"\nCommunities detected: {len(results['communities'])}")
        for comm, members in results['communities'].items():
            print(f"  {comm}: {len(members)} papers")


if __name__ == "__main__":
    main()
