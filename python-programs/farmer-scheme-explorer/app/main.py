from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.rag_chain import ask_question


app = FastAPI(
    title="Farmer Scheme RAG API",
    description=(
        "RAG API for retrieving Tamil Nadu "
        "farmer schemes from a local FAISS database."
    ),
    version="1.0.0",
)


class QuestionRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=3,
        description="Farmer's question",
    )


class Source(BaseModel):

    scheme: str | None = None
    department: str | None = None
    sno: str | int | float | None = None


class QuestionResponse(BaseModel):

    answer: str
    sources: list[Source]


@app.get("/")
def root():

    return {
        "application": "Farmer Scheme RAG",
        "status": "running",
    }


@app.get("/health")
def health():

    return {
        "status": "UP"
    }


@app.post(
    "/api/v1/schemes/ask",
    response_model=QuestionResponse,
)
def ask_scheme(request: QuestionRequest):

    try:

        result = ask_question(
            request.question
        )

        return result

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to process question: "
                f"{str(exc)}"
            ),
        )