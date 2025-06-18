# nli_filtered_agent/rag_wrapper.py

from RAG_agent.rag.retriever import Retriever as RAGRetriever

class NliRetrieverWrapper:
    def __init__(self, csv_path="RAG_agent/data/embeddings.csv"):
        self.rag = RAGRetriever(csv_path=csv_path)

    def retrieve(self, query: str) -> str:
        results = self.rag.retrieve(query, top_k=1)
        return results[0][0] if results else ""