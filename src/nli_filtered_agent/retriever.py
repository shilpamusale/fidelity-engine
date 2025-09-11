# # nli_filtered_agent/retriever.py

# from sentence_transformers import SentenceTransformer
# import faiss
# import os

# class RAGRetriever:
#     def __init__(self, kb_path="nli_filtered_agent/
# data/full_nutrition_knowledge_base.txt",
# model_name="all-MiniLM-L6-v2", threshold=0.6):
#         self.kb_path = kb_path
#         self.model = SentenceTransformer(model_name)
#         self.threshold = threshold
#         self.chunks = self._load_chunks()
#         self.embeddings = self.model.encode(self.chunks, normalize_embeddings=True)
#         self.index = self._build_index(self.embeddings)

#     def _load_chunks(self):
#         if not os.path.exists(self.kb_path):
#             raise FileNotFoundError(f"Knowledge base file not found: {self.kb_path}")
#         with open(self.kb_path, "r", encoding="utf-8") as f:
#             text = f.read()

#         # Split into chunks (adjust size as needed)
#         return [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

#     def _build_index(self, embeddings):
#         dim = embeddings.shape[1]
#         index = faiss.IndexFlatIP(dim)
#         index.add(embeddings)
#         return index

#     def retrieve(self, query, top_k=3):
#         query_embedding = self.model.encode([query], normalize_embeddings=True)
#         scores, indices = self.index.search(query_embedding, top_k)

#         retrieved_chunks = []
#         for score, idx in zip(scores[0], indices[0]):
#             if score >= self.threshold:
#                 retrieved_chunks.append(self.chunks[idx])
#             else:
#                 print(f"[RAG FILTER] ❌ Skipping chunk (score={score:.2f})")

#         if not retrieved_chunks:
#             print("[RAG] ⚠️ No relevant chunk found for query:", query)

#         return " ".join(retrieved_chunks) if retrieved_chunks else ""


from sentence_transformers import SentenceTransformer
import faiss
import os


class RAGRetriever:
    def __init__(
        self,
        kb_path="nli_filtered_agent/data/full_nutrition_knowledge_base.txt",
        model_name="all-MiniLM-L6-v2",
        threshold=0.6,
    ):
        self.kb_path = kb_path
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold
        self.chunks = self._load_chunks()
        self.embeddings = self.model.encode(self.chunks, normalize_embeddings=True)
        self.index = self._build_index(self.embeddings)

    def _load_chunks(self):
        if not os.path.exists(self.kb_path):
            raise FileNotFoundError(f"Knowledge base file not found: {self.kb_path}")
        with open(self.kb_path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
        print(f"[RAG]  Loaded {len(chunks)} knowledge chunks.")
        return chunks

    def _build_index(self, embeddings):
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)
        return index

    # def retrieve(self, query, top_k=3):
    #     query_embedding = self.model.encode([query], normalize_embeddings=True)
    #     scores, indices = self.index.search(query_embedding, top_k)

    #     print(f"[RAG] 🔍 Query: {query}")
    #     print(f"[RAG] 🧠 Top-{top_k} scores: {scores[0]}")

    #     retrieved_chunks = []
    #     for score, idx in zip(scores[0], indices[0]):
    #         chunk = self.chunks[idx]
    #         if score >= self.threshold:
    #             print(f"[RAG]  Accepted: Score={score:.3f} | Chunk={chunk[:60]}...")
    #             retrieved_chunks.append(chunk)
    #         else:
    #             print(f"[RAG] ❌ Rejected: Score={score:.3f} | Chunk={chunk[:60]}...")

    #     # Fallback: if nothing above threshold, return top-1 anyway
    #     if not retrieved_chunks and len(indices[0]) > 0:
    #         fallback_chunk = self.chunks[indices[0][0]]
    #         fallback_score = scores[0][0]
    #         print(f"[RAG] ⚠️ Using fallback chunk (score={fallback_score:.3f})")
    #         return fallback_chunk

    #     return " ".join(retrieved_chunks) if retrieved_chunks else ""

    def retrieve(self, query, top_k=3):
        query_embedding = self.model.encode([query], normalize_embeddings=True)
        scores, indices = self.index.search(query_embedding, top_k)

        print(f"\n🔍 [RAG] Query: {query}")
        print(f"📊 [RAG] Top-{top_k} Scores: {scores[0]}")

        retrieved_chunks = []

        for score, idx in zip(scores[0], indices[0]):
            chunk = self.chunks[idx]
            if score >= self.threshold:
                print(f" [RAG] Accepted: {score:.3f} → {chunk[:60]}...")
                retrieved_chunks.append(chunk)
            else:
                print(f"❌ [RAG] Rejected: {score:.3f} → {chunk[:60]}...")

        # Fallback if all scores are below threshold
        if not retrieved_chunks and len(indices[0]) > 0:
            fallback_chunk = self.chunks[indices[0][0]]
            fallback_score = scores[0][0]
            print(
                f"⚠️ [RAG] Using fallback: {fallback_score:.3f}"
                + "→ {fallback_chunk[:60]}..."
            )
            return fallback_chunk

        result = " ".join(retrieved_chunks) if retrieved_chunks else ""
        print(
            f"\n📘 [RAG FINAL] Returning Premise:\n{result if result else '❌ EMPTY'}"
        )
        return result


# 🧪 CLI Debugging
if __name__ == "__main__":
    retriever = RAGRetriever(threshold=0.6)
    test_query = "What is the major component for muscle development?"
    result = retriever.retrieve(test_query)
    print("\n[RAG RESULT] 🧾 Retrieved Context:\n", result)
