"""
Cross-Platform Paper Deduplication Utility

Handles deduplication of papers from multiple sources (OpenAlex, Semantic Scholar, arXiv)
using a multi-stage strategy based on bibliographic best practices.

Strategy (based on systematic review methodologies):
1. Primary: DOI matching (most reliable unique identifier)
2. Secondary: Normalized title + year + first author
3. Tertiary: Fuzzy title matching for variations

References:
- BibDedupe: An Open-Source Python Library for Bibliographic Deduplication
- Rule-based deduplication of article records from bibliographic databases
- Entity deduplication in big data graphs for scholarly graphs
"""

import re
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from difflib import SequenceMatcher


class PaperDeduplicator:
    """
    Deduplicate papers across multiple academic sources

    Uses a hierarchical strategy:
    1. DOI matching (exact)
    2. Title + Year + First Author (normalized)
    3. Fuzzy title matching (for typos/variations)
    """

    def __init__(self, fuzzy_threshold: float = 0.85):
        """
        Initialize deduplicator

        Args:
            fuzzy_threshold: Minimum similarity for fuzzy matching (0.0-1.0)
                            0.85 is recommended for bibliographic matching
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.seen_dois: Set[str] = set()
        self.seen_composite_keys: Set[str] = set()
        self.duplicate_map: Dict[str, str] = {}  # duplicate_id -> canonical_id

    def normalize_title(self, title: str) -> str:
        """
        Normalize title for comparison

        Steps:
        1. Convert to lowercase
        2. Remove punctuation
        3. Remove extra whitespace
        4. Remove special characters

        Args:
            title: Raw title string

        Returns:
            Normalized title
        """
        if not title:
            return ""

        # Convert to lowercase
        title = title.lower()

        # Remove punctuation (except hyphens in compound words)
        title = re.sub(r'[^\w\s-]', ' ', title)

        # Remove extra whitespace
        title = ' '.join(title.split())

        return title.strip()

    def extract_doi(self, paper: Dict) -> str:
        """
        Extract DOI from paper, handling various formats

        Handles:
        - Direct DOI field
        - DOI in URL format
        - arXiv IDs (not DOI, but similar role)

        Args:
            paper: Paper dictionary

        Returns:
            Clean DOI or empty string
        """
        doi = paper.get('doi', '')

        if not doi:
            return ''

        # Remove URL prefix if present
        doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)
        doi = doi.strip().lower()

        return doi

    def get_first_author(self, paper: Dict) -> str:
        """
        Get first author name for deduplication

        Args:
            paper: Paper dictionary

        Returns:
            First author name or empty string
        """
        authors = paper.get('authors', [])

        if not authors or len(authors) == 0:
            return ''

        first_author = authors[0]

        # If it's a dict with 'name' field
        if isinstance(first_author, dict):
            return first_author.get('name', '').lower().strip()

        # If it's a string
        return str(first_author).lower().strip()

    def build_composite_key(self, paper: Dict) -> str:
        """
        Build composite key from title + year + first author

        This is used when DOI is not available.

        Format: "normalized_title|year|first_author"

        Args:
            paper: Paper dictionary

        Returns:
            Composite key string
        """
        title = self.normalize_title(paper.get('title', ''))
        year = str(paper.get('year', ''))
        first_author = self.get_first_author(paper)

        return f"{title}|{year}|{first_author}"

    def fuzzy_title_match(self, title1: str, title2: str) -> float:
        """
        Calculate fuzzy similarity between two titles

        Uses SequenceMatcher (difflib) which is based on
        Ratcliff/Obershelp pattern matching algorithm.

        Args:
            title1: First title
            title2: Second title

        Returns:
            Similarity score (0.0 to 1.0)
        """
        norm1 = self.normalize_title(title1)
        norm2 = self.normalize_title(title2)

        if not norm1 or not norm2:
            return 0.0

        return SequenceMatcher(None, norm1, norm2).ratio()

    def is_duplicate_by_doi(self, paper: Dict) -> bool:
        """
        Check if paper is duplicate using DOI

        Args:
            paper: Paper to check

        Returns:
            True if duplicate found
        """
        doi = self.extract_doi(paper)

        if not doi:
            return False

        if doi in self.seen_dois:
            return True

        self.seen_dois.add(doi)
        return False

    def is_duplicate_by_composite(self, paper: Dict) -> bool:
        """
        Check if paper is duplicate using composite key

        Args:
            paper: Paper to check

        Returns:
            True if duplicate found
        """
        composite_key = self.build_composite_key(paper)

        if not composite_key or composite_key.endswith('|'):
            return False

        if composite_key in self.seen_composite_keys:
            return True

        self.seen_composite_keys.add(composite_key)
        return False

    def find_duplicate_by_fuzzy(self, paper: Dict, existing_papers: List[Dict]) -> Dict:
        """
        Find duplicate using fuzzy title matching

        Args:
            paper: Paper to check
            existing_papers: List of papers to compare against

        Returns:
            Duplicate paper if found, None otherwise
        """
        title = paper.get('title', '')

        if not title:
            return None

        for existing in existing_papers:
            existing_title = existing.get('title', '')

            if not existing_title:
                continue

            similarity = self.fuzzy_title_match(title, existing_title)

            if similarity >= self.fuzzy_threshold:
                # Additional check: year should match
                if paper.get('year') == existing.get('year'):
                    return existing

        return None

    def deduplicate_papers(self, papers: List[Dict], aggressive: bool = False) -> List[Dict]:
        """
        Deduplicate a list of papers from multiple sources

        Args:
            papers: List of paper dictionaries
            aggressive: If True, use fuzzy matching (slower but more thorough)

        Returns:
            Deduplicated list of papers
        """
        unique_papers = []
        duplicates_found = 0

        for paper in papers:
            paper_id = paper.get('id', 'unknown')

            # Stage 1: DOI matching (fastest, most reliable)
            if self.is_duplicate_by_doi(paper):
                duplicates_found += 1
                self.duplicate_map[paper_id] = f"DOI:{self.extract_doi(paper)}"
                continue

            # Stage 2: Composite key matching
            if self.is_duplicate_by_composite(paper):
                duplicates_found += 1
                self.duplicate_map[paper_id] = f"Composite:{self.build_composite_key(paper)}"
                continue

            # Stage 3: Fuzzy matching (only if aggressive mode)
            if aggressive:
                duplicate = self.find_duplicate_by_fuzzy(paper, unique_papers)
                if duplicate:
                    duplicates_found += 1
                    dup_id = duplicate.get('id', 'unknown')
                    self.duplicate_map[paper_id] = f"Fuzzy:{dup_id}"
                    continue

            unique_papers.append(paper)

        print(f"  Deduplication: Found {duplicates_found} duplicates ({len(unique_papers)} unique)")
        return unique_papers

    def deduplicate_cross_source(
        self,
        openalex_papers: List[Dict],
        semantic_scholar_papers: List[Dict],
        arxiv_papers: List[Dict],
        aggressive: bool = False
    ) -> Tuple[List[Dict], Dict[str, int]]:
        """
        Deduplicate papers across multiple sources

        Args:
            openalex_papers: Papers from OpenAlex
            semantic_scholar_papers: Papers from Semantic Scholar
            arxiv_papers: Papers from arXiv
            aggressive: Use fuzzy matching

        Returns:
            Tuple of (deduplicated_papers, source_counts)
        """
        all_papers = []

        # Tag papers with source
        for p in openalex_papers:
            p['_source'] = 'openalex'
            all_papers.append(p)

        for p in semantic_scholar_papers:
            p['_source'] = 'semantic_scholar'
            all_papers.append(p)

        for p in arxiv_papers:
            p['_source'] = 'arxiv'
            all_papers.append(p)

        # Deduplicate
        unique = self.deduplicate_papers(all_papers, aggressive=aggressive)

        # Count by source
        source_counts = defaultdict(int)
        for p in unique:
            source = p.get('_source', 'unknown')
            source_counts[source] += 1

        return unique, dict(source_counts)

    def get_deduplication_stats(self) -> Dict:
        """
        Get statistics about deduplication process

        Returns:
            Dictionary with stats
        """
        return {
            'unique_dois': len(self.seen_dois),
            'unique_composite_keys': len(self.seen_composite_keys),
            'duplicates_found': len(self.duplicate_map)
        }


def merge_papers_by_source(
    openalex_papers: List[Dict],
    semantic_scholar_papers: List[Dict],
    arxiv_papers: List[Dict]
) -> Dict[str, List[Dict]]:
    """
    Merge papers from all sources into a structured dict

    Args:
        openalex_papers: Papers from OpenAlex
        semantic_scholar_papers: Papers from Semantic Scholar
        arxiv_papers: Papers from arXiv

    Returns:
        Dict with source as key, list of papers as value
    """
    return {
        'openalex': openalex_papers,
        'semantic_scholar': semantic_scholar_papers,
        'arxiv': arxiv_papers
    }


if __name__ == "__main__":
    # Test deduplication
    dedup = PaperDeduplicator()

    test_papers = [
        {
            'id': '1',
            'title': 'Deep Learning for Change Detection',
            'year': 2024,
            'doi': '10.1109/test.2024.1234567',
            'authors': ['John Smith', 'Jane Doe']
        },
        {
            'id': '2',
            'title': 'Deep Learning for Change Detection',  # Duplicate by title/year/author
            'year': 2024,
            'doi': '',
            'authors': ['John Smith', 'Jane Doe']
        },
        {
            'id': '3',
            'title': 'Deep Learning for Change  Detection',  # Fuzzy duplicate (extra space)
            'year': 2024,
            'doi': '',
            'authors': ['John Smith', 'Jane Doe']
        },
        {
            'id': '4',
            'title': 'Different Paper Title',
            'year': 2023,
            'doi': '10.1234/different.5678',
            'authors': ['Alice Johnson']
        }
    ]

    unique = dedup.deduplicate_papers(test_papers, aggressive=True)
    print(f"Original: {len(test_papers)}, After dedup: {len(unique)}")
    print(f"Stats: {dedup.get_deduplication_stats()}")
