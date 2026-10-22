
import re


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 80,
) -> list[str]:
    """Create chunks from complete sentences where possible."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    text = " ".join(text.split())

    if not text:
        return []

    # Split after sentence-ending punctuation.
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current = ""

    for sentence in sentences:
        # Handle a single sentence longer than chunk_size.
        if len(sentence) > chunk_size:
            if current:
                chunks.append(current)
                current = ""

            start = 0
            while start < len(sentence):
                end = min(start + chunk_size, len(sentence))

                if end < len(sentence):
                    boundary = sentence.rfind(" ", start, end)
                    if boundary > start:
                        end = boundary

                chunks.append(sentence[start:end].strip())
                start = end

                while start < len(sentence) and sentence[start] == " ":
                    start += 1

            continue

        candidate = f"{current} {sentence}".strip()

        if current and len(candidate) > chunk_size:
            chunks.append(current)

            # Retain recent complete sentences as overlap.
            overlap_parts = []
            overlap_length = 0

            for part in reversed(re.split(r"(?<=[.!?])\s+", current)):
                if overlap_length + len(part) > overlap:
                    break

                overlap_parts.insert(0, part)
                overlap_length += len(part) + 1

            current = " ".join(overlap_parts)
            current = f"{current} {sentence}".strip()

        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 500,
    overlap: int = 80,
) -> list[dict]:
    """Chunk document records and preserve source information."""

    results = []

    for document in documents:
        chunks = chunk_text(
            document["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for number, chunk in enumerate(chunks, start=1):
            results.append({
                "source": document["source"],
                "location": document["location"],
                "chunk_id": number,
                "text": chunk,
            })

    return results


if __name__ == "__main__":
    sample = (
        "Wi-Fi Troubleshooting Guide. "
        "Step 1: Enable Wi-Fi. "
        "Step 2: Turn off airplane mode. "
        "Step 3: Restart the router."
    )

    results = chunk_text(sample, chunk_size=70, overlap=15)

    for number, chunk in enumerate(results, start=1):
        print(f"\nChunk {number}: {chunk}")

