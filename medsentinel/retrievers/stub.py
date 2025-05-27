"""
medsentinel/retrievers/stub.py

Implements a basic in-memory retriever for development/testing purposes.

Returns hardcoded clinical passages relevant to queries.

Intended Use:
Use for unit testing or development before integrating real vector DBs.

Author: MedSentinel Team (2025)
"""

from typing import List
from medsentinel.retrievers.base import RetrieverInterface


class StubRetriever(RetrieverInterface):
    """
    Simple retriever returning hardcoded clinical docs.
    """

    def __init__(self) -> None:
        self.documents: List[str] = [
            "Patients with diabetes are at higher risk for hospital readmission.",
            "Social determinants like housing instability affect ED utilization.",
            "Community Health Workers (CHWs) reduce avoidable readmissions.",
            "A history of ED visits is a strong predictor of 30-day readmission.",
        ]

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        return self.documents[:top_k]
