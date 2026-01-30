"""
Multi-Source Query Builder

Generates optimized queries for each academic search API (OpenAlex, Semantic Scholar, arXiv)
based on a common user query specification.

Each API has different strengths and query syntax:
- OpenAlex: Powerful filtering, entity-based queries
- Semantic Scholar: Natural language, relevance ranking
- arXiv: Category-based, CS/Physics focused
"""

from typing import List, Dict, Optional


class QuerySpecification:
    """
    Standardized query specification that can be adapted to each API
    """

    def __init__(
        self,
        query_text: str,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        venues: Optional[List[str]] = None,
        min_citations: Optional[int] = None,
        fields_of_study: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,  # arXiv categories
        publication_type: Optional[str] = None
    ):
        """
        Initialize query specification

        Args:
            query_text: Main search query text
            year_from: Earliest publication year
            year_to: Latest publication year
            venues: Target venue names (journals/conferences)
            min_citations: Minimum citation count
            fields_of_study: Semantic Scholar fields (e.g., "Computer Science")
            categories: arXiv categories (e.g., ["cs.CV", "cs.LG"])
            publication_type: Article type (journal, conference, etc.)
        """
        self.query_text = query_text
        self.year_from = year_from
        self.year_to = year_to
        self.venues = venues or []
        self.min_citations = min_citations
        self.fields_of_study = fields_of_study or []
        self.categories = categories or []
        self.publication_type = publication_type

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'query': self.query_text,
            'year_from': self.year_from,
            'year_to': self.year_to,
            'venues': self.venues,
            'min_citations': self.min_citations,
            'fields_of_study': self.fields_of_study,
            'categories': self.categories,
            'publication_type': self.publication_type
        }


class MultiSourceQueryBuilder:
    """
    Build API-specific queries from a common specification
    """

    def __init__(self):
        """Initialize query builder"""
        pass

    def build_openalex_query(self, spec: QuerySpecification) -> Dict:
        """
        Build OpenAlex query specification

        OpenAlex strengths:
        - Powerful filter syntax
        - Entity lookups (venues, authors, institutions)
        - Works-level filtering
        - Citation counts

        Args:
            spec: Query specification

        Returns:
            OpenAlex-specific query dict
        """
        query = {
            'query': spec.query_text,
            'filters': {}
        }

        # Year filtering
        if spec.year_from and spec.year_to:
            query['filters']['year_from'] = spec.year_from
            query['filters']['year_to'] = spec.year_to
        elif spec.year_from:
            query['filters']['year_from'] = spec.year_from
        elif spec.year_to:
            query['filters']['year_to'] = spec.year_to

        # Venue filtering
        if spec.venues:
            # OpenAlex can filter by venue name
            query['filters']['venue_name'] = spec.venues[0]  # Primary venue

        # Citation filtering
        if spec.min_citations:
            query['filters']['min_citations'] = spec.min_citations

        # Type filtering
        if spec.publication_type:
            query['filters']['type'] = spec.publication_type

        return query

    def build_semantic_scholar_query(self, spec: QuerySpecification) -> Dict:
        """
        Build Semantic Scholar query specification

        Semantic Scholar strengths:
        - Natural language processing
        - Relevance ranking
        - Field of study filtering
        - Citation counts

        Args:
            spec: Query specification

        Returns:
            Semantic Scholar-specific query dict
        """
        query = {
            'query': spec.query_text
        }

        # Year filtering (string format)
        if spec.year_from and spec.year_to:
            query['year'] = f"{spec.year_from}-{spec.year_to}"
        elif spec.year_from:
            query['year'] = f"{spec.year_from}-"
        elif spec.year_to:
            query['year'] = f"-{spec.year_to}"

        # Venue filtering
        if spec.venues:
            query['venue'] = spec.venues[0]

        # Field of study
        if spec.fields_of_study:
            query['fields_of_study'] = ','.join(spec.fields_of_study)

        # Citation filtering
        if spec.min_citations:
            query['min_citation_count'] = spec.min_citations

        # Publication type
        if spec.publication_type:
            query['publication_types'] = spec.publication_type

        return query

    def build_arxiv_query(self, spec: QuerySpecification) -> Dict:
        """
        Build arXiv query specification

        arXiv strengths:
        - Category filtering (cs.CV, cs.LG, etc.)
        - Recent preprints
        - CS/Physics focus
        - Full text available

        Limitations:
        - No citation counts
        - Limited to CS/Physics/Math
        - Mostly preprints

        Args:
            spec: Query specification

        Returns:
            arXiv-specific query dict
        """
        query = {
            'query': spec.query_text,
            'sort_by': 'relevance'  # or 'lastUpdatedDate', 'submittedDate'
        }

        # Category filtering
        if spec.categories:
            query['categories'] = spec.categories

        # Year filtering
        if spec.year_from:
            query['year_from'] = spec.year_from
        if spec.year_to:
            query['year_to'] = spec.year_to

        # Note: arXiv doesn't support venue or citation filtering
        # min_citations and venues are ignored

        return query

    def build_all_queries(self, spec: QuerySpecification) -> Dict[str, Dict]:
        """
        Build queries for all three sources

        Args:
            spec: Query specification

        Returns:
            Dict mapping source name to query dict
        """
        return {
            'openalex': self.build_openalex_query(spec),
            'semantic_scholar': self.build_semantic_scholar_query(spec),
            'arxiv': self.build_arxiv_query(spec)
        }


def generate_query_variations(base_query: str) -> List[QuerySpecification]:
    """
    Generate multiple query variations from a base query

    This helps increase coverage by:
    - Broader queries
    - Specific sub-topics
    - Different terminology

    Args:
        base_query: User's research question

    Returns:
        List of query specifications
    """
    variations = []

    # Variation 1: Original query
    variations.append(QuerySpecification(query_text=base_query))

    # Variation 2: Broader (remove specific terms)
    # This is simplified - could use NLP to extract core concepts
    words = base_query.split()
    if len(words) > 3:
        broader_query = ' '.join(words[:4])  # Keep first 4 words
        variations.append(QuerySpecification(query_text=broader_query))

    # Variation 3: Add "survey" or "review"
    variations.append(QuerySpecification(query_text=f"{base_query} survey review"))

    return variations


if __name__ == "__main__":
    # Test query builder
    builder = MultiSourceQueryBuilder()

    spec = QuerySpecification(
        query_text="deep learning change detection remote sensing",
        year_from=2020,
        min_citations=10,
        fields_of_study=["Computer Science"],
        categories=["cs.CV", "cs.LG"]
    )

    queries = builder.build_all_queries(spec)

    print("OpenAlex Query:")
    print(queries['openalex'])
    print("\nSemantic Scholar Query:")
    print(queries['semantic_scholar'])
    print("\narXiv Query:")
    print(queries['arxiv'])
