from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

QDRANT_PATH = PROJECT_ROOT / "qdrant_data"
COLLECTION_NAME = "company_documents"

# Initial threshold for testing, not a production-calibrated value.
MIN_SCORE = 0.25


def search_documents(question: str, limit: int = 2, min_score: float = MIN_SCORE) -> list[dict]:
    """Retrieve relevant document chunks above a minimum similarity score."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    query_vector = embeddings.embed_query(question)

    client = QdrantClient(path=str(QDRANT_PATH))

    try:
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=limit,
            with_payload=True,
        ).points

        retrieved_chunks = []

        for result in results:
            if result.score is None or result.score < min_score:
                continue

            payload = result.payload or {}
            text = payload.get("text", "")

            if not text.strip():
                continue

            retrieved_chunks.append(
                {
                    "text": text,
                    "document_name": payload.get("document_name", ""),
                    "page_number": payload.get("page_number"),
                    "score": result.score,
                }
            )

        return retrieved_chunks

    finally:
        client.close()


if __name__ == "__main__":
    questions = [
        "What is the warranty period?",
        "What should I do if the display does not turn on?",
        "What colors are available?",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")

        chunks = search_documents(question)

        if not chunks:
            print("No chunks passed the minimum similarity threshold.")
            continue

        for chunk in chunks:
            print(f"Document: {chunk['document_name']}")
            print(f"Page: {chunk['page_number']}")
            print(f"Similarity score: {chunk['score']:.4f}")
            print(f"Text: {chunk['text']}")
            print("-" * 50)