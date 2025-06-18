from rank_bm25 import BM25Okapi
import os
import random
import numpy as np
import torch

SEED = 42
os.environ["PYTHONHASHSEED"] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

import pandas as pd
import ast
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss

class Retriever:
    def __init__(self, csv_path="../data/embeddings.csv", model_name="BAAI/bge-large-en-v1.5"):
        self.embed_model = SentenceTransformer(model_name)
        self.knowledge_df = pd.read_csv(csv_path)
        self.knowledge_embeddings = np.array(
            self.knowledge_df['embedding'].apply(lambda x: np.array(ast.literal_eval(x), dtype=np.float32)).tolist(),
            dtype=np.float32
        )
        faiss.normalize_L2(self.knowledge_embeddings)
        self.knowledge_texts = self.knowledge_df['sentence_chunk'].tolist()
        self.knowledge_pages = self.knowledge_df['page_number'].tolist() if 'page_number' in self.knowledge_df else [None]*len(self.knowledge_texts)
        # Build BM25 corpus (lower‑cased, whitespace tokenisation is fine for PDF chunks)
        self.corpus_tokens = [txt.lower().split() for txt in self.knowledge_texts]
        self.bm25 = BM25Okapi(self.corpus_tokens)
        # Build FAISS index
        self.index = faiss.IndexFlatL2(self.knowledge_embeddings.shape[1])
        self.index.add(self.knowledge_embeddings)
        # Prepare cross-encoder for reranking
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def embed_query(self, query: str) -> np.ndarray:
        vec = self.embed_model.encode([query], normalize_embeddings=True)[0]
        return vec.astype(np.float32)

    def retrieve(self, query: str, top_k=10) -> list:
        # ---- dense retrieval -------------------------------------------------
        query_embedding = self.embed_query(query).reshape(1, -1)
        D, I = self.index.search(query_embedding, 30)            # dense top‑30
        dense_ids = I[0].tolist()

        # ---- sparse retrieval (BM25) ----------------------------------------
        tokenised_q = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenised_q)
        bm25_top30_ids = np.argsort(bm25_scores)[-30:][::-1].tolist()

        # Debug print: Top 10 BM25 results
        print("\nTop 10 BM25 results for query:", query)
        for idx in np.argsort(bm25_scores)[-10:][::-1]:
            print(f"Score: {bm25_scores[idx]:.4f} | Chunk: {self.knowledge_texts[idx][:120]}")

        # ---- pool & dedupe ---------------------------------------------------
        pool_ids = list(dict.fromkeys(dense_ids + bm25_top30_ids))  # preserves order

        # ---- gather candidate chunks ----------------------------------------
        candidates = [
            (self.knowledge_texts[i],
             self.knowledge_pages[i],
             float(bm25_scores[i]))   # keep BM25 score just for debugging
            for i in pool_ids
        ]

        # ---- cross‑encoder rerank -------------------------------------------
        pairs = [(query, chunk) for chunk, _, _ in candidates]
        ce_scores = self.cross_encoder.predict(pairs)            # numpy array
        ranked_idx = np.argsort(ce_scores)[::-1][:top_k]

        return [
            (candidates[i][0],           # chunk text
             candidates[i][1],           # page
             float(ce_scores[i]))        # cross‑encoder score
            for i in ranked_idx
        ]
