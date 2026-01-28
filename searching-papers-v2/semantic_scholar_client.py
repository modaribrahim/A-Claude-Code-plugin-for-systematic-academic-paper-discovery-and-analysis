"""
Semantic Scholar API Client Wrapper

Handles both Graph API and Recommendations API:
- Graph API: Primary search for papers using keyword/semantic search
- Recommendations API: Deep search based on positive/negative paper examples

API Documentation:
- Graph API: https://api.semanticscholar.org/graph/v1/swagger.json
- Recommendations API: https://api.semanticscholar.org/recommendations/v1/swagger.json
"""

import time
import requests
from typing import Dict, List, Optional, Any, Union

# ============= Configuration =============
SEMANTIC_SCHOLAR_GRAPH_API_BASE = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_RECOMMENDATIONS_API_BASE = "https://api.semanticscholar.org/recommendations/v1"
SEMANTIC_SCHOLAR_RATE_LIMIT = 100  # requests per second (1 per second for free tier)


class SemanticScholarClient:
    """Client for Semantic Scholar APIs with proper error handling and rate limiting"""

    def __init__(self, api_key: Optional[str] = None, rate_limit: int = 1):
        """
        Initialize Semantic Scholar client

        Args:
            api_key: Semantic Scholar API key (optional but recommended)
            rate_limit: Max requests per second (default: 1 for free tier)
        """
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.graph_api_base = SEMANTIC_SCHOLAR_GRAPH_API_BASE
        self.recommendations_api_base = SEMANTIC_SCHOLAR_RECOMMENDATIONS_API_BASE

    def _wait_for_rate_limit(self):
        """Wait to respect rate limit"""
        min_time_between_requests = 1.0 / self.rate_limit
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < min_time_between_requests:
            sleep_time = min_time_between_requests - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Dict[str, Any],
                     base_url: str, method: str = "GET",
                     body: Optional[Dict] = None) -> Dict:
        """
        Make API request with exponential backoff retry

        Args:
            endpoint: API endpoint
            params: Query parameters
            base_url: Base URL for the API
            method: HTTP method (GET or POST)
            body: Request body for POST requests

        Returns:
            JSON response
        """
        url = f"{base_url}/{endpoint}"

        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key

        max_retries = 5
        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()

                if method == "GET":
                    response = requests.get(url, params=params, headers=headers, timeout=30)
                elif method == "POST":
                    response = requests.post(url, params=params, json=body, headers=headers, timeout=30)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    print(f"  Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif response.status_code >= 500:
                    # Server error - retry with backoff
                    wait_time = 2 ** attempt
                    print(f"  Server error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Other error - don't retry
                    raise

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"  Timeout, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

        raise Exception(f"Failed after {max_retries} retries")

    # ============= Graph API: Paper Search =============

    def search_papers(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        year: Optional[str] = None,
        venue: Optional[str] = None,
        fields_of_study: Optional[str] = None,
        min_citation_count: Optional[int] = None,
        open_access_pdf: Optional[bool] = None,
        publication_types: Optional[str] = None,
        publication_date_or_year: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        Search for papers using the Graph API (relevance search)

        This is the PRIMARY search method for finding papers by keywords/topics.
        Uses relevance ranking and supports up to 100 results per request.

        Args:
            query: Plain-text search query string
            fields: List of fields to return (see API docs for available fields)
            year: Publication year range (e.g., "2019", "2016-2020", "2010-", "-2015")
            venue: Venue filter (e.g., "Nature", "ICSE")
            fields_of_study: Field of study filter (e.g., "Computer Science,Physics")
            min_citation_count: Minimum number of citations
            open_access_pdf: Only return papers with open access PDFs
            publication_types: Publication type filter (e.g., "JournalArticle,Review")
            publication_date_or_year: Date range (e.g., "2019-03-05:2020-06-06")
            limit: Number of results to return (max 100)
            offset: Starting position for pagination

        Returns:
            Dictionary with 'data', 'total', 'offset', 'next' keys
        """
        params = {
            'query': query,
            'limit': min(limit, 100),
            'offset': offset
        }

        # Add optional parameters
        if fields:
            params['fields'] = ','.join(fields)
        if year:
            params['year'] = year
        if venue:
            params['venue'] = venue
        if fields_of_study:
            params['fieldsOfStudy'] = fields_of_study
        if min_citation_count is not None:
            params['minCitationCount'] = min_citation_count
        if open_access_pdf:
            params['openAccessPdf'] = ''
        if publication_types:
            params['publicationTypes'] = publication_types
        if publication_date_or_year:
            params['publicationDateOrYear'] = publication_date_or_year

        return self._make_request('paper/search', params, self.graph_api_base, method="GET")

    def search_papers_bulk(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        year: Optional[str] = None,
        venue: Optional[str] = None,
        fields_of_study: Optional[str] = None,
        min_citation_count: Optional[int] = None,
        open_access_pdf: Optional[bool] = None,
        publication_types: Optional[str] = None,
        publication_date_or_year: Optional[str] = None,
        limit: int = 1000,
        token: Optional[str] = None,
        sort: Optional[str] = None
    ) -> Dict:
        """
        Search for papers using bulk search (for >1000 results)

        Similar to search_papers but supports:
        - Up to 1000 results per request
        - Pagination via token
        - Custom sorting

        Args:
            query: Plain-text search query (can use boolean logic)
            fields: List of fields to return
            year: Publication year range
            venue: Venue filter
            fields_of_study: Field of study filter
            min_citation_count: Minimum number of citations
            open_access_pdf: Only return papers with open access PDFs
            publication_types: Publication type filter
            publication_date_or_year: Date range
            limit: Number of results to return (max 1000)
            token: Continuation token from previous request
            sort: Sort order (e.g., "citationCount:desc", "publicationDate:asc")

        Returns:
            Dictionary with 'data', 'total', 'token' keys
        """
        params = {
            'query': query,
            'limit': min(limit, 1000)
        }

        # Add optional parameters
        if fields:
            params['fields'] = ','.join(fields)
        if year:
            params['year'] = year
        if venue:
            params['venue'] = venue
        if fields_of_study:
            params['fieldsOfStudy'] = fields_of_study
        if min_citation_count is not None:
            params['minCitationCount'] = min_citation_count
        if open_access_pdf:
            params['openAccessPdf'] = ''
        if publication_types:
            params['publicationTypes'] = publication_types
        if publication_date_or_year:
            params['publicationDateOrYear'] = publication_date_or_year
        if token:
            params['token'] = token
        if sort:
            params['sort'] = sort

        return self._make_request('paper/search/bulk', params, self.graph_api_base, method="GET")

    def get_paper(self, paper_id: str, fields: Optional[List[str]] = None) -> Dict:
        """
        Get details for a single paper

        Args:
            paper_id: Paper ID (supports multiple ID formats: S2 ID, DOI, ARXIV, etc.)
            fields: List of fields to return

        Returns:
            Paper object
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)

        return self._make_request(f'paper/{paper_id}', params, self.graph_api_base, method="GET")

    def get_papers_batch(self, paper_ids: List[str], fields: Optional[List[str]] = None) -> List[Dict]:
        """
        Get details for multiple papers at once

        Args:
            paper_ids: List of paper IDs (max 500)
            fields: List of fields to return

        Returns:
            List of paper objects
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)

        body = {'ids': paper_ids}

        response = self._make_request('paper/batch', params, self.graph_api_base, method="POST", body=body)
        return response

    # ============= Recommendations API =============

    def get_recommendations(
        self,
        positive_paper_ids: List[str],
        negative_paper_ids: Optional[List[str]] = None,
        limit: int = 100,
        fields: Optional[List[str]] = None
    ) -> Dict:
        """
        Get paper recommendations based on positive/negative examples

        This is the SECONDARY search method for deep research.
        Use this when you have seed papers and want to find related work.

        Args:
            positive_paper_ids: List of paper IDs to use as positive examples
            negative_paper_ids: List of paper IDs to use as negative examples (optional)
            limit: Number of recommendations to return (max 500)
            fields: List of fields to return

        Returns:
            Dictionary with 'recommendedPapers' key containing list of papers
        """
        params = {
            'limit': min(limit, 500)
        }

        if fields:
            params['fields'] = ','.join(fields)

        body = {
            'positivePaperIds': positive_paper_ids
        }

        if negative_paper_ids:
            body['negativePaperIds'] = negative_paper_ids

        return self._make_request('papers/', params, self.recommendations_api_base,
                                 method="POST", body=body)

    def get_recommendations_for_paper(
        self,
        paper_id: str,
        from_pool: str = "recent",
        limit: int = 100,
        fields: Optional[List[str]] = None
    ) -> Dict:
        """
        Get recommendations for a single paper

        Simplified version of get_recommendations for a single seed paper.

        Args:
            paper_id: Paper ID to get recommendations for
            from_pool: Pool to recommend from ("recent" or "all-cs")
            limit: Number of recommendations to return (max 500)
            fields: List of fields to return

        Returns:
            Dictionary with 'recommendedPapers' key containing list of papers
        """
        params = {
            'from': from_pool,
            'limit': min(limit, 500)
        }

        if fields:
            params['fields'] = ','.join(fields)

        return self._make_request(f'papers/forpaper/{paper_id}', params,
                                 self.recommendations_api_base, method="GET")


# ============= Helper Functions =============

def normalize_paper(paper: Dict) -> Dict:
    """
    Normalize Semantic Scholar paper format to match OpenAlex format

    Args:
        paper: Raw paper from Semantic Scholar API

    Returns:
        Normalized paper dict with consistent field names
    """
    # Extract venue
    venue = ""
    if paper.get('venue'):
        venue = paper['venue']
    elif paper.get('publicationVenue'):
        publication_venue = paper['publicationVenue']
        if publication_venue and isinstance(publication_venue, dict):
            venue = publication_venue.get('name', '')

    # Extract authors
    authors = []
    if paper.get('authors'):
        authors = [a.get('name', '') for a in paper['authors'] if a.get('name')]

    # Extract external IDs
    external_ids = paper.get('externalIds', {})

    # Extract concepts (fields of study)
    concepts = []
    for fos in (paper.get('s2FieldsOfStudy') or [])[:5]:
        category = fos.get('category')
        if category:
            concepts.append(category)

    # Build normalized paper
    normalized = {
        'id': paper.get('paperId', ''),
        'title': paper.get('title', ''),
        'abstract': paper.get('abstract', ''),
        'year': paper.get('year'),
        'type': paper.get('publicationTypes', ['Unknown'])[0] if paper.get('publicationTypes') else 'Unknown',
        'citations': paper.get('citationCount', 0),
        'influentialCitationCount': paper.get('influentialCitationCount', 0),
        'is_oa': paper.get('isOpenAccess', False),
        'oa_status': 'open' if paper.get('isOpenAccess') else 'closed',
        'doi': external_ids.get('DOI', ''),
        'concepts': concepts,
        'authors': authors,
        'venue': venue,
        'venue_id': (paper.get('publicationVenue') or {}).get('id', ''),
        'url': paper.get('url', ''),
        'openAccessPdf': paper.get('openAccessPdf', {}).get('url', ''),
        'publicationDate': paper.get('publicationDate', ''),
        'referenceCount': paper.get('referenceCount', 0),
        'externalIds': external_ids
    }

    return normalized


def build_fields_from_requirements(require_abstract: bool = True,
                                   require_authors: bool = True,
                                   require_citations: bool = True,
                                   require_venue: bool = True) -> List[str]:
    """
    Build Semantic Scholar fields list based on requirements

    Args:
        require_abstract: Include abstract field
        require_authors: Include authors field
        require_citations: Include citation counts
        require_venue: Include venue information

    Returns:
        List of field names for Semantic Scholar API
    """
    fields = ['paperId', 'title', 'year', 'url', 'externalIds', 'isOpenAccess',
              'openAccessPdf', 's2FieldsOfStudy', 'publicationTypes', 'publicationDate']

    if require_abstract:
        fields.append('abstract')

    if require_authors:
        fields.append('authors')

    if require_citations:
        fields.extend(['citationCount', 'influentialCitationCount', 'referenceCount'])

    if require_venue:
        fields.extend(['venue', 'publicationVenue'])

    return fields
