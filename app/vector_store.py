
import uuid
from dotenv import load_dotenv
from pathlib import Path

import pymupdf  # Not required here, but used by the ingestion module.
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient, models

from app.ingestion import ingest_pdfs
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


PROJECT_ROOT = Path(__file__).resolve().parent.parent
QDRANT_PATH = PROJECT_ROOT / "qdrant_data"
COLLECTION_NAME = "company_documents"


def build_vector_store():
    # Step 1: Read and chunk the PDF documents.
    chunks = ingest_pdfs()

    if not chunks:
        raise ValueError(
            "No PDF chunks found. Add a readable PDF to data/pdfs first."
        )

    # Step 2: Initialize the OpenAI embedding model.
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    # Step 3: Generate embeddings for all chunks.
    texts = [chunk["text"] for chunk in chunks]
    vectors = embeddings.embed_documents(texts)

    if not vectors:
        raise ValueError("No embeddings were generated.")

    # Step 4: Open a persistent local Qdrant database.
    # Close other Qdrant clients using this same directory first.
    client = QdrantClient(path=str(QDRANT_PATH))

    try:
        # Rebuild the collection for this initial development script.
        if client.collection_exists(COLLECTION_NAME):
            client.delete_collection(COLLECTION_NAME)

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=len(vectors[0]),
                distance=models.Distance.COSINE,
            ),
        )

        # Step 5: Store vectors, text, and source metadata.
        points = []

        for chunk, vector in zip(chunks, vectors):
            points.append(
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "text": chunk["text"],
                        "document_name": chunk["document_name"],
                        "page_number": chunk["page_number"],
                        "chunk_id": chunk["chunk_id"],
                    },
                )
            )

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True,
        )

        print("\nVector database created successfully!")
        print(f"Collection: {COLLECTION_NAME}")
        print(f"Stored chunks: {len(points)}")
        print(f"Database location: {QDRANT_PATH}")

    finally:
        client.close()


if __name__ == "__main__":
    build_vector_store()
