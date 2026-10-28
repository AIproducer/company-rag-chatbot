
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.rag_pipeline import answer_question


app = FastAPI(
    title="Company RAG Chatbot API",
    description="Answers company questions using internal PDF documents.",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question about company products or policies.",
    )


class Source(BaseModel):
    document_name: str
    page_number: int


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    try:
        result = answer_question(question)

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
        )

    except Exception:
        # Do not expose API keys, internal paths, or stack traces.
        raise HTTPException(
            status_code=500,
            detail="Unable to process your question. Please try again.",
        )
