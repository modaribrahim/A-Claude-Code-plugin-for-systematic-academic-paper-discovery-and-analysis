"""
Example: Complete Workflow Demonstration

This script demonstrates the complete 6-stage workflow for searching academic papers.
Use this as a reference for understanding how the system works.

NOTE: This is a demonstration. The actual agent (Claude Code) will run these stages
interactively based on user input.
"""

import os
import json


def print_stage(title):
    """Print stage header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def example_workflow():
    """Run complete example workflow"""

    # Example user query (after refinement)
    query = "deep learning change detection remote sensing"
    year_from = 2020
    min_citations = 10
    categories = ["cs.CV", "cs.LG"]

    print_stage("ACADEMIC PAPER SEARCH - EXAMPLE WORKFLOW")
    print(f"\nResearch Query: {query}")
    print(f"Year Range: {year_from}-present")
    print(f"Min Citations: {min_citations}")
    print(f"arXiv Categories: {', '.join(categories)}")

    # Stage 2: Multi-Source Search
    print_stage("STAGE 2: Multi-Source Broad Search")

    cmd_2 = f"""python scripts/multi_search.py \\
  --query "{query}" \\
  --year-from {year_from} \\
  --min-citations {min_citations} \\
  --categories {' '.join(categories)} \\
  --max-results 100 \\
  --output artifacts/search_results.json"""

    print("\nCommand to run:")
    print(cmd_2)

    print("\nExpected output:")
    print("  - OpenAlex: ~100 papers")
    print("  - Semantic Scholar: ~100 papers")
    print("  - arXiv: ~100 papers")
    print("  Total: ~300 papers")

    # Stage 3a: Filter by Citations
    print_stage("STAGE 3a: Filter by Citation Count")

    cmd_3a = """python scripts/filter_citations.py \\
  --input artifacts/search_results.json \\
  --top-n 50 \\
  --output artifacts/filtered_by_citations.json"""

    print("\nCommand to run:")
    print(cmd_3a)

    print("\nExpected output:")
    print("  Top 50 papers per source by citation count")
    print("  Total: ~150 papers")

    # Stage 3b: Rank by Embeddings
    print_stage("STAGE 3b: Rank by Semantic Similarity")

    cmd_3b = f"""python scripts/rank_embeddings.py \\
  --input artifacts/filtered_by_citations.json \\
  --query "{query}" \\
  --top-n 20 \\
  --output artifacts/ranked_by_embeddings.json"""

    print("\nCommand to run:")
    print(cmd_3b)

    print("\nExpected output:")
    print("  Top 20 papers per source by semantic similarity")
    print("  Total: ~60 papers")

    # Stage 4: Deduplicate
    print_stage("STAGE 4: Cross-Source Deduplication")

    cmd_4 = """python scripts/deduplicate_sources.py \\
  --input artifacts/ranked_by_embeddings.json \\
  --aggressive \\
  --output artifacts/deduplicated.json"""

    print("\nCommand to run:")
    print(cmd_4)

    print("\nExpected output:")
    print("  30-40 unique seed papers (after removing duplicates)")

    # Stage 5: Citation Expansion
    print_stage("STAGE 5: Citation Expansion")

    cmd_5 = """python scripts/citation_expand.py \\
  --input artifacts/deduplicated.json \\
  --max-total 100 \\
  --per-paper-limit 20 \\
  --output artifacts/expanded.json"""

    print("\nCommand to run:")
    print(cmd_5)

    print("\nExpected output:")
    print("  ~100 total papers (seed + cited-by papers)")

    # Stage 6: Summarize
    print_stage("STAGE 6: Generate Summary")

    cmd_6 = """python scripts/summarize_results.py \\
  --input artifacts/expanded.json \\
  --output artifacts/summary.json"""

    print("\nCommand to run:")
    print(cmd_6)

    print("\nExpected output:")
    print("  Summary statistics:")
    print("    - Total papers")
    print("    - Year distribution")
    print("    - Top venues")
    print("    - Top authors")
    print("    - Top concepts")
    print("    - Citation statistics")

    # Summary
    print_stage("WORKFLOW COMPLETE")

    print("\n📁 Output Files:")
    print("  artifacts/search_results.json       - Raw search results")
    print("  artifacts/filtered_by_citations.json - Top papers by citations")
    print("  artifacts/ranked_by_embeddings.json  - Top papers by relevance")
    print("  artifacts/deduplicated.json          - Unique seed papers")
    print("  artifacts/expanded.json              - Final collection")
    print("  artifacts/summary.json               - Statistics summary")

    print("\n⏱️  Estimated Time: 10-20 minutes")

    print("\n✨ Next Steps:")
    print("  1. Review artifacts/summary.json")
    print("  2. Examine artifacts/expanded.json for paper details")
    print("  3. Provide feedback to refine the search")

    print("\n💡 Tip: In production, Claude Code will run this")
    print("         workflow interactively and ask for your")
    print("         feedback at each stage!")


def print_quick_reference():
    """Print quick reference guide"""

    print_stage("QUICK REFERENCE GUIDE")

    print("\n📚 All Scripts:\n")

    scripts = [
        ("multi_search.py", "Search OpenAlex + Semantic Scholar + arXiv"),
        ("filter_citations.py", "Keep top N papers by citation count"),
        ("rank_embeddings.py", "Rank papers by semantic similarity"),
        ("deduplicate_sources.py", "Remove duplicate papers"),
        ("citation_expand.py", "Find papers that cite seed papers"),
        ("summarize_results.py", "Generate collection statistics"),
    ]

    for script, description in scripts:
        print(f"  {script:30} → {description}")

    print("\n🔧 All Utils:\n")

    utils = [
        ("embeddings.py", "Semantic ranking with sentence-transformers"),
        ("deduplication.py", "Cross-platform deduplication logic"),
        ("query_builder.py", "Build API-specific queries"),
    ]

    for util, description in utils:
        print(f"  {util:30} → {description}")

    print("\n📖 Workflow:\n")
    print("  Query → Search → Filter → Rank → Dedup → Expand → Summarize")

    print("\n🎯 Key Features:\n")
    print("  ✓ 3 academic sources (OpenAlex, Semantic Scholar, arXiv)")
    print("  ✓ Two-stage filtering (citations + embeddings)")
    print("  ✓ Robust deduplication (DOI + fuzzy matching)")
    print("  ✓ Citation expansion (find related work)")
    print("  ✓ Interactive refinement")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  ACADEMIC PAPER SEARCH AGENT v2")
    print("  Example Workflow Demonstration")
    print("="*70)

    # Run example
    example_workflow()

    print("\n\n")

    # Quick reference
    print_quick_reference()

    print("\n" + "="*70)
    print("  For more information, see README.md")
    print("  To use the agent, just ask Claude Code!")
    print("="*70 + "\n")
