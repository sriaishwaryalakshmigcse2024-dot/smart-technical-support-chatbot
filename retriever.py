
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from document_loader import load_knowledge_base
from chunking import chunk_documents


# Resolve the knowledge-base path relative to this file.
PROJECT_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE = PROJECT_DIR / "data" / "knowledge_base"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def build_retriever():
    """Load documents, create chunks, and build a FAISS index."""

    documents, errors = load_knowledge_base(KNOWLEDGE_BASE)

    if errors:
        print("\nFiles with issues:")
        for error in errors:
            print(f"- {error['source']}: {error['error']}")

    if not documents:
        raise ValueError(
            f"No readable documents found in: {KNOWLEDGE_BASE}"
        )

    chunks = chunk_documents(
        documents,
        chunk_size=500,
        overlap=80,
    )

    if not chunks:
        raise ValueError("No text chunks were created.")

    # Validate chunk content before generating embeddings.
    chunks = [
        chunk for chunk in chunks
        if chunk.get("text", "").strip()
    ]

    if not chunks:
        raise ValueError("All chunks contain empty text.")

    print(f"\nDocument records: {len(documents)}")
    print(f"Text chunks: {len(chunks)}")
    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    embeddings = np.asarray(embeddings, dtype=np.float32)

    # Build a cosine-similarity index using normalized vectors.
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    print(f"Vectors indexed: {index.ntotal}")

    return model, index, chunks


def search_documents(
    question: str,
    model,
    index,
    chunks: list[dict],
    top_k: int = 3,
) -> list[dict]:
    """Retrieve the most relevant document chunks."""

    if not question or not question.strip():
        return []

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    if index.ntotal == 0 or not chunks:
        return []

    query_vector = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    query_vector = np.asarray(query_vector, dtype=np.float32)

    k = min(top_k, index.ntotal, len(chunks))
    scores, indices = index.search(query_vector, k)

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue

        chunk = chunks[int(idx)]

        results.append({
            "score": float(score),
            "source": chunk.get("source", "Unknown"),
            "location": chunk.get("location", "Unknown"),
            "chunk_id": chunk.get("chunk_id", "Unknown"),
            "text": chunk["text"],
        })

    return results


if __name__ == "__main__":
    model, index, chunks = build_retriever()

    question = "My Wi-Fi is not working. What should I restart?"

    print(f"\nQuestion: {question}")
    print("\nRetrieved passages:")

    results = search_documents(
        question=question,
        model=model,
        index=index,
        chunks=chunks,
        top_k=3,
    )

    if not results:
        print("No matching passages were found.")
    else:
        for number, result in enumerate(results, start=1):
            print(f"\nResult {number}")
            print(f"Similarity: {result['score']:.3f}")
            print(f"Source: {result['source']}")
            print(f"Location: {result['location']}")
            print(f"Text: {result['text']}")


# Initial threshold for testing, not a universal confidence cutoff.
MIN_SIMILARITY = 0.30


def search_documents(
    question,
    model,
    index,
    chunks,
    top_k=3,
    min_score=MIN_SIMILARITY,
):
    """Retrieve relevant passages and filter low similarity scores."""

    if not question or not question.strip():
        return []

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    if not -1.0 <= min_score <= 1.0:
        raise ValueError("min_score must be between -1 and 1.")

    if not chunks:
        return []

    query_vector = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    import numpy as np

    query_vector = np.asarray(query_vector, dtype="float32")

    # Retrieve candidates, then discard weak matches.
    k = min(top_k, len(chunks))
    scores, indices = index.search(query_vector, k)

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue

        score = float(score)

        if score < min_score:
            continue

        chunk = chunks[int(idx)]

        results.append({
            "score": score,
            "source": chunk["source"],
            "location": chunk["location"],
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
        })

    return results
