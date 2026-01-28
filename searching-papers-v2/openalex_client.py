"""
OpenAlex API Client Wrapper

Handles all OpenAlex API complexity:
- Rate limiting and exponential backoff
- Pagination with per-page=200
- Two-step lookups for entities
- Error handling and retries
- Efficient field selection
- Filter builder for easy query specification
"""

import time
import requests
from typing import Dict, List, Optional, Any

# ============= Configuration =============
OPENALEX_API_BASE = "https://api.openalex.org"
OPENALEX_RATE_LIMIT = 100  # requests per second
OPENALEX_PER_PAGE = 200


class OpenAlexClient:
    """Simple wrapper for OpenAlex API with proper error handling"""

    def __init__(self, api_key: Optional[str] = None, rate_limit: int = 100):
        """
        Initialize OpenAlex client

        Args:
            api_key: OpenAlex API key (get free at openalex.org/settings/api)
            rate_limit: Max requests per second (default: 100)
        """
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.base_url = OPENALEX_API_BASE

    def _wait_for_rate_limit(self):
        """Wait to respect rate limit"""
        min_time_between_requests = 1.0 / self.rate_limit
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < min_time_between_requests:
            sleep_time = min_time_between_requests - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict:
        """
        Make API request with exponential backoff retry

        Args:
            endpoint: API endpoint (e.g., 'works' or 'works/W123')
            params: Query parameters

        Returns:
            JSON response
        """
        url = f"{self.base_url}/{endpoint}"

        if self.api_key:
            params['api_key'] = self.api_key

        # Add default per-page for list endpoints only (not single entities)
        if 'per-page' not in params and 'sample' not in params:
            # Single entity endpoints look like: works/W123, authors/A456 (contain a slash)
            # List endpoints look like: works, authors (no slash)
            if '/' not in endpoint:  # Only add per-page for list endpoints
                params['per-page'] = 200

        max_retries = 5
        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()

                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()

                return response.json()

            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    # Rate limited - wait with exponential backoff
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

    def search_entities(self, entity_type: str, search_query: str) -> List[Dict]:
        """
        Search for entities (authors, institutions, sources, etc.)

        Args:
            entity_type: Entity type ('authors', 'institutions', 'sources', 'topics')
            search_query: Search query string

        Returns:
            List of matching entities with IDs
        """
        params = {'search': search_query}

        response = self._make_request(entity_type, params)

        results = response.get('results', [])
        return results

    def get_works(
        self,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        select: Optional[List[str]] = None,
        max_results: int = 200,
        sort: Optional[str] = None
    ) -> List[Dict]:
        """
        Get works with filters and pagination

        Args:
            filters: Dict of filters (e.g., {'publication_year': '2020', 'is_oa': True})
            search: Search query string
            select: List of fields to return (e.g., ['id', 'title', 'abstract'])
            max_results: Maximum number of results to retrieve
            sort: Sort string (e.g., 'cited_by_count:desc')

        Returns:
            List of work objects
        """
        params = {}

        # Build filter string from dict
        if filters:
            filter_parts = []
            for key, value in filters.items():
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                elif isinstance(value, list):
                    # OR operation: join with |
                    value = '|'.join(str(v) for v in value)
                filter_parts.append(f"{key}:{value}")
            params['filter'] = ','.join(filter_parts)

        # Add search query
        if search:
            params['search'] = search

        # Select specific fields
        if select:
            params['select'] = ','.join(select)

        # Add sort
        if sort:
            params['sort'] = sort

        # Set per-page
        params['per-page'] = 200

        # Paginate to get all results
        all_results = []
        page = 1

        while len(all_results) < max_results:
            params['page'] = page

            response = self._make_request('works', params)

            results = response.get('results', [])
            if not results:
                break

            all_results.extend(results)

            # Check if we've got all results
            meta_count = response.get('meta', {}).get('count', 0)
            if len(all_results) >= meta_count or len(all_results) >= max_results:
                break

            page += 1

        return all_results[:max_results]


def reconstruct_abstract(inverted_index: Optional[Dict]) -> str:
    """
    Reconstruct abstract from OpenAlex inverted index format

    Args:
        inverted_index: Dict mapping words to positions

    Returns:
        Reconstructed abstract string
    """
    if not inverted_index:
        return ""

    # Create list of (position, word) pairs
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))

    # Sort by position
    word_positions.sort(key=lambda x: x[0])

    # Reconstruct text
    words = [wp[1] for wp in word_positions]
    return ' '.join(words)


# ============= Filter Builder =============

class FilterBuilder:
    """Build OpenAlex filters from simple specifications"""

    def __init__(self):
        self.filters = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API"""
        return self.filters.copy()

    # ============= Publication Filters =============

    def add_year(self, year: Optional[int] = None, year_from: Optional[int] = None, year_to: Optional[int] = None):
        """Add publication year filter"""
        if year:
            self.filters['publication_year'] = year
        elif year_from and year_to:
            self.filters['publication_year'] = f"{year_from}-{year_to}"
        elif year_from:
            self.filters['publication_year'] = f">{year_from}"
        elif year_to:
            self.filters['publication_year'] = f"<{year_to}"
        return self

    def add_type(self, work_type: str):
        """Add work type filter (journal-article, conference-paper, dataset, etc.)"""
        self.filters['type'] = work_type
        return self

    def add_open_access(self, is_oa: bool = True):
        """Filter by open access status"""
        self.filters['is_oa'] = is_oa
        return self

    def add_has_doi(self, has_doi: bool = True):
        """Filter by DOI presence"""
        self.filters['has_doi'] = has_doi
        return self

    def add_citations(self, min_citations: Optional[int] = None, max_citations: Optional[int] = None):
        """Filter by citation count"""
        if min_citations:
            self.filters['cited_by_count'] = f">{min_citations}"
        if max_citations:
            self.filters['cited_by_count'] = f"<{max_citations}"
        return self

    # ============= Entity Filters (with lookup) =============

    def add_author_by_name(self, author_name: str, client: OpenAlexClient):
        """Add author filter by name (two-step lookup)"""
        results = client.search_entities('authors', author_name)
        if results:
            author_id = results[0]['id'].split('/')[-1]
            self.filters['authorships.author.id'] = author_id
            print(f"  ✓ Found author: {results[0]['display_name']}")
        else:
            print(f"  ✗ Author not found: {author_name}")
        return self

    def add_author_by_id(self, author_id: str):
        """Add author filter by ID"""
        if '/' in author_id:
            author_id = author_id.split('/')[-1]
        self.filters['authorships.author.id'] = author_id
        return self

    def add_institution_by_name(self, institution_name: str, client: OpenAlexClient):
        """Add institution filter by name (two-step lookup)"""
        results = client.search_entities('institutions', institution_name)
        if results:
            institution_id = results[0]['id'].split('/')[-1]
            self.filters['authorships.institutions.id'] = institution_id
            print(f"  ✓ Found institution: {results[0]['display_name']}")
        else:
            print(f"  ✗ Institution not found: {institution_name}")
        return self

    def add_institution_by_id(self, institution_id: str):
        """Add institution filter by ID"""
        if '/' in institution_id:
            institution_id = institution_id.split('/')[-1]
        self.filters['authorships.institutions.id'] = institution_id
        return self

    def add_venue_by_name(self, venue_name: str, client: OpenAlexClient):
        """Add venue/source filter by name (two-step lookup)"""
        results = client.search_entities('sources', venue_name)
        if results:
            venue_id = results[0]['id'].split('/')[-1]
            self.filters['primary_location.source.id'] = venue_id
            print(f"  ✓ Found venue: {results[0]['display_name']}")
        else:
            print(f"  ✗ Venue not found: {venue_name}")
        return self

    def add_venue_by_id(self, venue_id: str):
        """Add venue filter by ID"""
        if '/' in venue_id:
            venue_id = venue_id.split('/')[-1]
        self.filters['primary_location.source.id'] = venue_id
        return self

    def add_topic_by_name(self, topic_name: str, client: OpenAlexClient):
        """Add topic filter by name (two-step lookup)"""
        results = client.search_entities('topics', topic_name)
        if results:
            topic_id = results[0]['id'].split('/')[-1]
            self.filters['topics.id'] = topic_id
            print(f"  ✓ Found topic: {results[0]['display_name']}")
        else:
            print(f"  ✗ Topic not found: {topic_name}")
        return self

    def add_topic_by_id(self, topic_id: str):
        """Add topic filter by ID"""
        if '/' in topic_id:
            topic_id = topic_id.split('/')[-1]
        self.filters['topics.id'] = topic_id
        return self

    def add_country(self, country_code: str):
        """Add country filter for institutions (two-letter code)"""
        self.filters['institutions.country_code'] = country_code
        return self


def build_filter_from_dict(filter_spec: Dict[str, Any], client: OpenAlexClient) -> Dict[str, Any]:
    """
    Build filters from a dictionary specification

    This makes it easy for LLMs to specify filters as JSON.

    Args:
        filter_spec: Dictionary with filter specifications
        client: OpenAlex client for entity lookups

    Returns:
        Dictionary of filters for API

    Example filter_spec:
        {
            "year_from": 2020,
            "is_oa": True,
            "min_citations": 100,
            "venue_name": "Nature"
        }
    """
    fb = FilterBuilder()

    # Year filters
    if 'year' in filter_spec:
        fb.add_year(filter_spec['year'])
    if 'year_from' in filter_spec or 'year_to' in filter_spec:
        fb.add_year(
            year_from=filter_spec.get('year_from'),
            year_to=filter_spec.get('year_to')
        )

    # Type filters
    if 'type' in filter_spec:
        fb.add_type(filter_spec['type'])

    # Open access
    if 'is_oa' in filter_spec:
        fb.add_open_access(filter_spec['is_oa'])

    # DOI
    if 'has_doi' in filter_spec:
        fb.add_has_doi(filter_spec['has_doi'])

    # Citations
    if 'min_citations' in filter_spec or 'max_citations' in filter_spec:
        fb.add_citations(
            min_citations=filter_spec.get('min_citations'),
            max_citations=filter_spec.get('max_citations')
        )

    # Author
    if 'author_name' in filter_spec:
        fb.add_author_by_name(filter_spec['author_name'], client)
    elif 'author_id' in filter_spec:
        fb.add_author_by_id(filter_spec['author_id'])

    # Institution
    if 'institution_name' in filter_spec:
        fb.add_institution_by_name(filter_spec['institution_name'], client)
    elif 'institution_id' in filter_spec:
        fb.add_institution_by_id(filter_spec['institution_id'])

    # Country
    if 'country_code' in filter_spec:
        fb.add_country(filter_spec['country_code'])

    # Venue
    if 'venue_name' in filter_spec:
        fb.add_venue_by_name(filter_spec['venue_name'], client)
    elif 'venue_id' in filter_spec:
        fb.add_venue_by_id(filter_spec['venue_id'])

    # Topic
    if 'topic_name' in filter_spec:
        fb.add_topic_by_name(filter_spec['topic_name'], client)
    elif 'topic_id' in filter_spec:
        fb.add_topic_by_id(filter_spec['topic_id'])

    return fb.to_dict()
