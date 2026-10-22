
from retriever import build_retriever, search_documents


def generate_answer(
    question: str,
    model,
    index,
    chunks: list[dict],
    top_k: int = 3,
) -> str:
    """Generate a basic answer using retrieved knowledge."""

    results = search_documents(
        question=question,
        model=model,
        index=index,
        chunks=chunks,
        top_k=top_k,
    )

    if not results:
        return (
            "I could not find relevant information in the "
            "technical-support knowledge base. Please contact IT support."
        )

    # Combine the retrieved passages into supporting context.
    context = "\n".join(
        result["text"] for result in results
    )

    # Return the retrieved context as a basic grounded response.
    return (
        "Here is the relevant information from the "
        "technical-support knowledge base:\n\n"
        f"{context}"
    )


if __name__ == "__main__":
    model, index, chunks = build_retriever()

    print("\nSmart Technical Support Chatbot")
    print("Type 'exit' to stop.")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Chatbot: Goodbye!")
            break

        if not question:
            print("Chatbot: Please enter a question.")
            continue

        answer = generate_answer(
            question,
            model,
            index,
            chunks,
        )

        print(f"\nChatbot: {answer}")
