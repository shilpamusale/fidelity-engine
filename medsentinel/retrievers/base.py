"""
Module: medsentinel/retrievers/base.py

Defines the abstract interface for retrievers used in RAG-style skills.

Features:
- Unified retriever contract (`retrieve` method)
- Accepts query and optional metadata/context

Intended Use:
All retrievers (e.g., Pinecone, FAISS, Vertex Search) should subclass this.

Author: MedSentinel Team (2025)
"""

from abc import ABC, abstractmethod
from typing import List


class RetrieverInterface(ABC):
    """
    Abstract interface for retrievers used in RAG pipelines.
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
         Retrieve relevant documents given a query.
        Args:
            query: User or system-generated query string.
            top_k: Number of documents to return.
        Returns:
            List of document strings (top_k results).
        """
        pass
