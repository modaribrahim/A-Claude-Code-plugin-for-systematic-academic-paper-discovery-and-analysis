"""
Embedding-Based Semantic Ranking for Academic Papers

Computes embeddings for papers and ranks them by semantic similarity to queries.
Uses sentence-transformers for efficient embedding computation.

Based on research:
- "Taxonomy-guided Semantic Indexing for Academic Paper" (arXiv 2024)
- "Explicit Semantic Ranking for Academic Search" (ACM WWW 2017)
- Best practices for semantic search in academic repositories
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer


class PaperEmbedder:
    """
    Compute and rank papers by semantic similarity

    Uses sentence-transformers models pre-trained on scientific text.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedder with a sentence transformer model

        Default model: all-MiniLM-L6-v2 (fast, efficient, good quality)

        Alternative models:
        - "sentence-transformers/allenai-specter" (scientific papers, larger)
        - "sentence-transformers/all-mpnet-base-v2" (better quality, slower)

        Args:
            model_name: HuggingFace model name
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print("✓ Model loaded")

    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode search query into embedding

        Args:
            query: Search query string

        Returns:
            Embedding vector
        """
        return self.model.encode(query, show_progress_bar=False)

    def encode_paper(self, paper: Dict) -> np.ndarray:
        """
        Encode paper into embedding

        Uses title + abstract for best representation.
        Falls back to title only if abstract missing.

        Args:
            paper: Paper dictionary with title and abstract fields

        Returns:
            Embedding vector
        """
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')

        # Combine title and abstract
        if abstract and len(abstract) > 50:
            text = f"{title}. {abstract}"
        else:
            text = title

        return self.model.encode(text, show_progress_bar=False)

    def encode_papers(self, papers: List[Dict]) -> List[np.ndarray]:
        """
        Encode multiple papers

        Args:
            papers: List of paper dictionaries

        Returns:
            List of embedding vectors
        """
        texts = []

        for paper in papers:
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')

            if abstract and len(abstract) > 50:
                text = f"{title}. {abstract}"
            else:
                text = title

            texts.append(text)

        return self.model.encode(texts, show_progress_bar=False, batch_size=32)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (-1 to 1, where 1 is identical)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def rank_papers_by_query(
        self,
        papers: List[Dict],
        query: str,
        top_k: Optional[int] = None
    ) -> List[Tuple[Dict, float]]:
        """
        Rank papers by semantic similarity to query

        Args:
            papers: List of paper dictionaries
            query: Search query string
            top_k: Return only top k papers (None = return all)

        Returns:
            List of (paper, score) tuples sorted by similarity
        """
        if not papers:
            return []

        # Encode query
        query_embedding = self.encode_query(query)

        # Encode papers
        paper_embeddings = self.encode_papers(papers)

        # Calculate similarities
        scored_papers = []
        for paper, embedding in zip(papers, paper_embeddings):
            similarity = self.cosine_similarity(query_embedding, embedding)
            scored_papers.append((paper, similarity))

        # Sort by similarity (descending)
        scored_papers.sort(key=lambda x: x[1], reverse=True)

        # Return top k if specified
        if top_k:
            scored_papers = scored_papers[:top_k]

        return scored_papers

    def filter_top_k(
        self,
        papers: List[Dict],
        query: str,
        k: int = 20
    ) -> List[Dict]:
        """
        Filter and return top k most relevant papers

        Args:
            papers: List of paper dictionaries
            query: Search query string
            k: Number of papers to return

        Returns:
            List of top k papers
        """
        ranked = self.rank_papers_by_query(papers, query, top_k=k)
        return [paper for paper, score in ranked]


class SourceSpecificRanker:
    """
    Rank papers separately within each source before merging

    This prevents one source from dominating results due to
    embedding bias toward that source's writing style.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize ranker

        Args:
            model_name: Sentence transformer model name
        """
        self.embedder = PaperEmbedder(model_name)

    def rank_per_source(
        self,
        papers_by_source: Dict[str, List[Dict]],
        query: str,
        top_k_per_source: int = 20
    ) -> Dict[str, List[Dict]]:
        """
        Rank papers separately within each source

        Args:
            papers_by_source: Dict mapping source name to list of papers
            query: Search query string
            top_k_per_source: Number of top papers to keep per source

        Returns:
            Dict mapping source name to top k papers
        """
        ranked_by_source = {}

        for source, papers in papers_by_source.items():
            if not papers:
                ranked_by_source[source] = []
                continue

            print(f"  Ranking {len(papers)} papers from {source}...")
            top_papers = self.embedder.filter_top_k(papers, query, k=top_k_per_source)
            ranked_by_source[source] = top_papers
            print(f"    → Kept top {len(top_papers)}")

        return ranked_by_source

    def merge_ranked_results(
        self,
        ranked_by_source: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        Merge top papers from all sources

        Args:
            ranked_by_source: Dict of top papers per source

        Returns:
            Combined list of papers
        """
        all_papers = []

        for source, papers in ranked_by_source.items():
            # Tag with source
            for paper in papers:
                paper['_rank_source'] = source
            all_papers.extend(papers)

        return all_papers


if __name__ == "__main__":
    # Test embedding ranking
    embedder = PaperEmbedder()

    test_papers = [
        {
            'title': 'Deep Learning for Change Detection in Remote Sensing',
            'abstract': 'We propose a deep learning approach for detecting changes in satellite imagery.',
            'year': 2024
        },
        {
            'title': 'Transformer Models for Computer Vision',
            'abstract': 'A survey of transformer architectures applied to vision tasks.',
            'year': 2023
        },
        {
            'title': 'Change Detection with CNNs',
            'abstract': 'Convolutional neural networks for bitemporal image analysis.',
            'year': 2022
        }
    ]

    query = "change detection deep learning"
    top_papers = embedder.filter_top_k(test_papers, query, k=2)

    print(f"\nQuery: {query}")
    print(f"Top {len(top_papers)} papers:")
    for i, paper in enumerate(top_papers, 1):
        print(f"{i}. {paper['title']}")
