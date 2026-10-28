
from pathlib import Path

import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF_DIRECTORY = PROJECT_ROOT / "data" / "pdfs"


def extract_pdf_pages(pdf_path: Path) -> list[dict]:
    """Extract text from a PDF and preserve page numbers."""

    extracted_pages = []

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                extracted_pages.append(
                    {
                        "document_name": pdf_path.name,
                        "page_number": page_number,
                        "text": text,
                    }
                )

    return extracted_pages


def create_chunks(
    pages: list[dict],
    chunk_size: int = 450,
    chunk_overlap: int = 75,
) -> list[dict]:
    """Split page text into chunks and preserve source metadata."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
    )

    chunks = []

    for page in pages:
        documents = splitter.create_documents(
            texts=[page["text"]],
            metadatas=[
                {
                    "document_name": page["document_name"],
                    "page_number": page["page_number"],
                }
            ],
        )

        for document in documents:
            chunks.append(
                {
                    "document_name": document.metadata["document_name"],
                    "page_number": document.metadata["page_number"],
                    "chunk_id": len(chunks),
                    "start_index": document.metadata.get("start_index", 0),
                    "text": document.page_content,
                }
            )

    return chunks


def ingest_pdfs() -> list[dict]:
    """Extract and chunk all PDFs in the data directory."""

    pdf_files = sorted(PDF_DIRECTORY.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in: {PDF_DIRECTORY}")
        return []

    all_pages = []

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")

        try:
            pages = extract_pdf_pages(pdf_path)
            all_pages.extend(pages)
            print(f"  Extracted text from {len(pages)} pages.")

        except Exception as error:
            print(f"  ERROR processing {pdf_path.name}: {error}")

    chunks = create_chunks(all_pages)

    print(f"\nTotal pages extracted: {len(all_pages)}")
    print(f"Total chunks created: {len(chunks)}")

    return chunks


if __name__ == "__main__":
    chunks = ingest_pdfs()

    for chunk in chunks[:3]:
        print("\n--- CHUNK ---")
        print(f"Document: {chunk['document_name']}")
        print(f"Page: {chunk['page_number']}")
        print(f"Text: {chunk['text'][:200]}")