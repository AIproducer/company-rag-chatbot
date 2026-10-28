# Company RAG Chatbot

An AI-powered document question-answering application built using Retrieval-Augmented Generation (RAG). The chatbot retrieves relevant information from company PDF documents and uses a large language model to generate answers grounded in the retrieved context.

## Project Overview

This project demonstrates how to build a document-based AI assistant that can answer questions using company documentation rather than relying solely on the model's general knowledge.

Users can ask questions about company information, product guides, customer support policies, and employee handbook documents through a simple Streamlit interface.

## Key Features

- **PDF Document Ingestion:** Extracts text from PDF documents.
- **Text Chunking:** Splits documents into smaller, overlapping chunks for retrieval.
- **Vector Search:** Stores and retrieves document embeddings using Qdrant.
- **Semantic Embeddings:** Uses OpenAI's `text-embedding-3-small` embedding model.
- **AI-Powered Answers:** Uses `gpt-4.1-mini` to generate answers from retrieved context.
- **Source Citations:** Displays document names and page numbers.
- **Hallucination Reduction:** Uses context-based prompting and a fallback response when sufficient information is unavailable.
- **REST API:** Provides endpoints through FastAPI.
- **Interactive Chat Interface:** Allows users to ask questions through Streamlit.
- **Local Vector Storage:** Uses Qdrant for persistent local storage.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| LangChain | LLM and embedding integration |
| OpenAI API | Text embeddings and answer generation |
| Qdrant | Vector database and semantic search |
| PyMuPDF | PDF text extraction |
| FastAPI | REST API |
| Streamlit | Interactive user interface |
| Pydantic | Request validation |
| python-dotenv | Environment variable management |

## Architecture

1. **Document Ingestion:** Load PDF files from the data directory.
2. **Text Extraction:** Extract text and page information using PyMuPDF.
3. **Chunking:** Split extracted text into overlapping chunks.
4. **Embedding Generation:** Convert chunks into vector embeddings.
5. **Vector Storage:** Store vectors and metadata in Qdrant.
6. **Question Retrieval:** Convert the user's question into an embedding and retrieve relevant chunks.
7. **Answer Generation:** Pass the retrieved context to the language model.
8. **Source Display:** Return the answer with supporting document names and page numbers.

## Project Structure

```text
company-rag-chatbot/
├── app/
│   ├── ingestion.py
│   ├── main.py
│   ├── rag_pipeline.py
│   ├── retriever.py
│   └── vector_store.py
├── data/
│   └── pdfs/
├── evaluation/
│   ├── evaluate_rag.py
│   └── test_questions.json
├── frontend/
│   └── chat_ui.py
├── qdrant_data/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd company-rag-chatbot
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Create a virtual environment

```bash
python -m venv rag-chatbot
```

Activate it on Windows PowerShell:

```powershell
.\rag-chatbot\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Replace the placeholder with your own OpenAI API key. Never commit your real API key to GitHub.

### 5. Build the vector database

After placing your PDF documents in `data/pdfs/`, run:

```bash
python -m app.vector_store
```

If your project uses a different command to build the vector database, use the command defined in your implementation.

## Run the Application

### Start the FastAPI backend

Open a terminal in the project directory and run:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Start the Streamlit frontend

Open a second terminal, activate the virtual environment, and run:

```bash
streamlit run frontend/chat_ui.py
```

Open the local URL displayed by Streamlit in your browser.

## Example Questions

- What is the company's name?
- What does the Smart Water Bottle do?
- What is the product warranty?
- What is the customer support response time?
- What are the company's office hours?
- Which product colors are available?

The chatbot is designed to indicate when the available documents do not contain enough information to answer a question.

## Security and Limitations

- An active OpenAI API key and internet access are required for API-based embeddings and answer generation.
- API usage may incur charges.
- The example company documents are fictional demonstration data.
- Retrieval quality depends on document quality, chunking, embedding similarity, and retrieval settings.
- Responses should be evaluated before using the application for real business decisions.
- Do not upload confidential documents or expose API credentials in a public repository.

## Future Improvements

- Automated retrieval and answer evaluation.
- Improved retrieval using reranking and metadata filters.
- User authentication and access control.
- Support for additional document formats.
- Deployment to a cloud platform.
- Monitoring, logging, and performance optimization.

## Author

Developed as a portfolio project demonstrating skills in Python, Generative AI, Retrieval-Augmented Generation, vector databases, API development, and AI application development.