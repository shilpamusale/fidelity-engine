import numpy as np
import re
import tqdm
import PyPDF2
import pandas as pd
from typing import List, Dict
from sentence_transformers import SentenceTransformer


def text_formatter(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\n", " ").strip())


def clean_text(txt: str) -> str:
    txt = txt.replace("•", "-").replace("–", "-")
    return re.sub(r"\s+", " ", txt)


def split_into_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def open_and_read_pdf(pdf_path: str) -> List[Dict]:
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        # Skip the first 8 pages (i.e., start from page index 8)
        # Table of Contents causing issues
        return [
            {"page_number": i, "text": text_formatter(page.extract_text() or "")}
            for i, page in enumerate(
                tqdm.tqdm(
                    pdf_reader.pages[8:], desc="Reading PDF (skipping first 8 pages)"
                ),
                start=8,
            )
        ]


def split_list(
    input_list: List[str], slice_size: int, overlap: int = 5
) -> List[List[str]]:
    step = slice_size - overlap
    return [input_list[i : i + slice_size] for i in range(0, len(input_list), step)]


def chunk_pdf_text(
    pages_and_texts: List[Dict], num_sentence_chunk_size: int = 4, overlap: int = 3
) -> pd.DataFrame:
    all_chunks = []
    for item in pages_and_texts:
        sentences = split_into_sentences(clean_text(item["text"]))
        for chunk in split_list(sentences, num_sentence_chunk_size, overlap):
            joined = " ".join(chunk)
            all_chunks.append(
                {
                    "page_number": item["page_number"],
                    "sentence_chunk": joined,
                    "chunk_char_count": len(joined),
                    "chunk_word_count": len(joined.split()),
                    "chunk_token_count": len(joined) / 4.0,
                }
            )
    return pd.DataFrame(all_chunks)


def embed_chunks(
    df: pd.DataFrame, model: SentenceTransformer, min_token_length: int = 4
) -> List[Dict]:
    filtered = df[df["chunk_token_count"] > min_token_length].to_dict(orient="records")
    for item in tqdm.tqdm(filtered, desc="Generating Embeddings"):
        vec = model.encode(item["sentence_chunk"], normalize_embeddings=True).astype(
            np.float32
        )
        item["embedding"] = vec
    return filtered


def store_in_csv(chunks: List[Dict], csv_file_path: str = "embeddings.csv") -> None:
    df = pd.DataFrame(chunks)
    df["embedding"] = df["embedding"].apply(lambda x: x.tolist())
    df.to_csv(csv_file_path, index=False)
    print(f"Embeddings stored in '{csv_file_path}'")


def embed_pdf_into_csv(
    pdf_path,
    embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
    csv_file_path="embeddings.csv",
):
    model = SentenceTransformer(embedding_model_name)
    pages_and_texts = open_and_read_pdf(pdf_path)
    df_chunks = chunk_pdf_text(pages_and_texts, num_sentence_chunk_size=3, overlap=2)
    chunks = embed_chunks(df_chunks, model)
    store_in_csv(chunks, csv_file_path)


if __name__ == "__main__":
    embed_pdf_into_csv(
        pdf_path="enhanced_model_agent/data/nutrition_handbook.pdf",
        embedding_model_name="BAAI/bge-large-en-v1.5",
        csv_file_path="enhanced_model_agent/data/embeddings.csv",
    )
