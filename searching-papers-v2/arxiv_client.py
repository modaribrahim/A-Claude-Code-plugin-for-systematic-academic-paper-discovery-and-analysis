"""
arXiv API Client Wrapper

Handles all arXiv API complexity:
- Rate limiting and query management
- Field extraction and normalization
- Error handling and retries
- Consistent interface matching OpenAlex and Semantic Scholar clients

arXiv API Documentation: http://export.arxiv.org/api_help/docs/torchard.html
arXiv.py Library: https://github.com/lukasschwab/arxiv.py
"""

import time
import arxiv
from typing import Dict, List, Optional, Any

# ============= Configuration =============
ARXIV_RATE_LIMIT = 3  # requests per second (arXiv asks for 1, but allows up to 3)
ARXIV_MAX_RESULTS = 1000  # arXiv API returns max 1000 per query


class ArxivClient:
    """Simple wrapper for arXiv API with proper error handling and normalization"""

    def __init__(self, rate_limit: int = 3):
        """
        Initialize arXiv client

        Args:
            rate_limit: Max requests per second (default: 3, though arXiv requests 1)
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0

    def _wait_for_rate_limit(self):
        """Wait to respect rate limit"""
        min_time_between_requests = 1.0 / self.rate_limit
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < min_time_between_requests:
            sleep_time = min_time_between_requests - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def search_papers(
        self,
        query: str,
        max_results: int = 100,
        sort_by: str = "relevance",
        categories: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """
        Search arXiv for papers

        Args:
            query: Search query string (supports arXiv query syntax)
            max_results: Maximum number of results to retrieve (default: 100)
            sort_by: Sort order - options:
                - "relevance": Relevance ranking (default)
                - "lastUpdatedDate": Most recently updated
                - "submittedDate": Most recently submitted
            categories: List of arXiv categories to filter (e.g., ['cs.CV', 'cs.LG'])
            filters: Optional filters including:
                - year_from: Earliest publication year
                - year_to: Latest publication year

        Returns:
            List of paper dicts with normalized metadata

        Example query:
            "deep learning AND change detection"

        Example categories:
            ['cs.CV', 'cs.LG']  # Computer Vision + Learning
        """
        # Build sort criterion
        sort_criterion_map = {
            "relevance": arxiv.SortCriterion.Relevance,
            "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
            "submittedDate": arxiv.SortCriterion.SubmittedDate
        }
        sort_criterion = sort_criterion_map.get(sort_by, arxiv.SortCriterion.Relevance)

        # Build query with category filters
        search_query = query

        # Add category filters if provided
        if categories:
            cat_filter = " OR ".join([f"cat:{cat}" for cat in categories])
            search_query = f"({query}) AND ({cat_filter})"

        # Add year filters if provided
        if filters:
            year_from = filters.get('year_from')
            year_to = filters.get('year_to')

            if year_from or year_to:
                year_filter = ""
                if year_from and year_to:
                    year_filter = f"submittedDate:[{year_from}0101 TO {year_to}1231]"
                elif year_from:
                    year_filter = f"submittedDate:[{year_from}0101 TO *]"
                elif year_to:
                    year_filter = f"submittedDate:[* TO {year_to}1231]"

                search_query = f"({search_query}) AND {year_filter}"

        # Create search client
        search = arxiv.Search(
            query=search_query,
            max_results=min(max_results, ARXIV_MAX_RESULTS),
            sort_by=sort_criterion,
            sort_order=arxiv.SortOrder.Descending
        )

        # Execute search with rate limiting
        self._wait_for_rate_limit()

        papers = []
        try:
            for result in search.results():
                paper = self._normalize_paper(result)
                papers.append(paper)

        except Exception as e:
            print(f"  ✗ Error searching arXiv: {e}")

        return papers

    def get_papers_by_ids(self, paper_ids: List[str]) -> List[Dict]:
        """
        Get papers by their arXiv IDs

        Args:
            paper_ids: List of arXiv IDs (e.g., ['2301.12345', 'cs.AI/1234567'])

        Returns:
            List of paper dicts with normalized metadata
        """
        papers = []

        for paper_id in paper_ids:
            self._wait_for_rate_limit()

            try:
                # Search by ID (arXiv uses title search with ID for exact match)
                search = arxiv.Search(id_list=[paper_id], max_results=1)

                for result in search.results():
                    paper = self._normalize_paper(result)
                    papers.append(paper)

            except Exception as e:
                print(f"  ✗ Error fetching paper {paper_id}: {e}")

        return papers

    def _normalize_paper(self, result: arxiv.Result) -> Dict:
        """
        Normalize arXiv paper format to match OpenAlex/Semantic Scholar format

        Args:
            result: arXiv Result object

        Returns:
            Normalized paper dict with consistent field names
        """
        # Extract authors
        authors = [author.name for author in result.authors]

        # Extract primary category
        primary_category = result.primary_category
        category = primary_category.split('.')[0] if primary_category else ""

        # Build concepts from categories and keywords
        concepts = []
        if primary_category:
            concepts.append(primary_category)

        # Map common arXiv categories to readable names
        category_map = {
            'cs.CV': 'Computer Vision',
            'cs.LG': 'Machine Learning',
            'cs.AI': 'Artificial Intelligence',
            'cs.CR': 'Cryptography',
            'cs.CL': 'Computation and Language',
            'cs.NE': 'Neural and Evolutionary Computing',
            'stat.ML': 'Machine Learning (Statistics)',
            'math.OC': 'Optimization and Control'
        }

        if primary_category in category_map:
            concepts.append(category_map[primary_category])

        # Determine if open access (arXiv is always open access)
        is_oa = True
        oa_status = 'green'  # arXiv is green open access

        # Build normalized paper
        normalized = {
            'id': result.entry_id.split('/')[-1],  # Extract ID from URL
            'title': result.title,
            'abstract': result.summary.replace('\n', ' '),  # Clean newlines
            'year': result.published.year if result.published else None,
            'type': 'article',  # arXiv papers are typically articles/preprints
            'citations': 0,  # arXiv doesn't provide citation counts
            'influentialCitationCount': 0,
            'is_oa': is_oa,
            'oa_status': oa_status,
            'doi': result.doi or '',
            'concepts': concepts[:5],  # Limit to 5 concepts
            'authors': authors[:10],  # Limit to 10 authors
            'venue': 'arXiv',
            'venue_id': '',
            'url': result.entry_id,
            'openAccessPdf': result.pdf_url,
            'published_date': result.published.strftime('%Y-%m-%d') if result.published else '',
            'updated_date': result.updated.strftime('%Y-%m-%d') if result.updated else '',
            'categories': result.categories,
            'primary_category': primary_category,
            'comment': result.comment if hasattr(result, 'comment') else '',
            'journal_ref': result.journal_ref if hasattr(result, 'journal_ref') else ''
        }

        return normalized


def build_query_from_keywords(keywords: List[str], operator: str = "AND") -> str:
    """
    Build arXiv query string from list of keywords

    Args:
        keywords: List of keywords
        operator: Logical operator to join keywords (AND/OR)

    Returns:
        Query string for arXiv API

    Example:
        keywords = ['change detection', 'remote sensing']
        operator = "AND"
        Returns: 'all:"change detection" AND all:"remote sensing"'
    """
    if operator.upper() == "AND":
        # Use AND operator for strict matching
        query_parts = [f'all:"{keyword}"' for keyword in keywords]
        return f" {operator} ".join(query_parts)
    else:
        # Use OR operator for broader matching
        query_parts = [f'all:"{keyword}"' for keyword in keywords]
        return f" {operator} ".join(query_parts)


def get_category_mapping() -> Dict[str, str]:
    """
    Get mapping of arXiv categories to readable names

    Returns:
        Dictionary mapping category codes to names

    Common categories:
        cs.AI - Artificial Intelligence
        cs.CL - Computation and Language
        cs.CV - Computer Vision and Pattern Recognition
        cs.LG - Machine Learning
        cs.NE - Neural and Evolutionary Computing
        stat.ML - Machine Learning (Statistics)
    """
    return {
        'cs.AI': 'Artificial Intelligence',
        'cs.CL': 'Computation and Language',
        'cs.CV': 'Computer Vision and Pattern Recognition',
        'cs.CC': 'Computational Complexity',
        'cs.CE': 'Computational Engineering',
        'cs.DS': 'Data Structures and Algorithms',
        'cs.DB': 'Databases',
        'cs.DL': 'Digital Libraries',
        'cs.DM': 'Discrete Mathematics',
        'cs.GL': 'General Literature',
        'cs.GR': 'Graphics',
        'cs.AR': 'Hardware Architecture',
        'cs.HC': 'Human-Computer Interaction',
        'cs.IR': 'Information Retrieval',
        'cs.IT': 'Information Theory',
        'cs.LG': 'Machine Learning',
        'cs.LO': 'Logic in Computer Science',
        'cs.MS': 'Mathematical Software',
        'cs.NA': 'Numerical Analysis',
        'cs.NE': 'Neural and Evolutionary Computing',
        'cs.NI': 'Networking and Internet Architecture',
        'cs.OH': 'Other Computer Science',
        'cs.OS': 'Operating Systems',
        'cs.PF': 'Performance',
        'cs.PL': 'Programming Languages',
        'cs.RO': 'Robotics',
        'cs.SC': 'Symbolic Computation',
        'cs.SD': 'Sound',
        'cs.SE': 'Software Engineering',
        'cs.SI': 'Social and Information Networks'
    }
