import pytest 
from retriever import search_documents


class FakeModel:
    def encode(self, texts, **kwargs):
        import numpy as np
        return np.array([[1.0, 0.0]], dtype="float32")


class FakeIndex:
    def search(self, query_vector, k):
        import numpy as np
        return (
            np.array([[0.90, 0.10]], dtype="float32"),
            np.array([[0, 1]], dtype="int64"),
        )


def test_low_similarity_results_are_filtered():
    chunks = [
        {
            "source": "wifi.txt",
            "location": "Page 1",
            "chunk_id": 0,
            "text": "Restart the wireless router.",
        },
        {
            "source": "cooking.txt",
            "location": "Page 1",
            "chunk_id": 1,
            "text": "Bake the cake for 30 minutes.",
        },
    ]

    results = search_documents(
        "How do I fix Wi-Fi?",
        FakeModel(),
        FakeIndex(),
        chunks,
        top_k=2,
        min_score=0.30,
    )

    assert len(results) == 1
    assert results[0]["source"] == "wifi.txt"
    assert results[0]["score"] == pytest.approx(0.90)

def test_empty_question_returns_no_results():
    results = search_documents(
        "",
        FakeModel(),
        FakeIndex(),
        [],
    )

    assert results == []
