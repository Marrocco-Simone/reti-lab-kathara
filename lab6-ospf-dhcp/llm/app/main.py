from fastapi import FastAPI, Query, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
import httpx
import json
import traceback
from typing import AsyncGenerator

app = FastAPI(title="LLM Streaming Service", version="1.0.0")

OLLAMA_URL = "http://localhost:11434/api/generate"
SYSTEM_PROMPT = (
    "You are a professional and helpful assistant. "
    "Always maintain a formal and respectful tone. "
    "Never use profanity or inappropriate language. "
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom validation error handler for missing query parameters."""
    errors = exc.errors()
    missing_params = []

    for error in errors:
        if error["type"] == "missing":
            param_name = error["loc"][-1]
            missing_params.append(param_name)

    if missing_params and "q" in missing_params:
        return JSONResponse(
            status_code=422,
            content={
                "error": "Missing required query parameter",
                "missing": ["q"],
                "help": "Usage: /ask?q=your_question (use underscores or %20 for spaces)",
                "example": "curl -N 'http://llm.startup.net/ask?q=What_is_DNS?'"
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": errors
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Generic exception handler for debugging."""
    error_traceback = traceback.format_exc()

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "type": type(exc).__name__,
            "message": str(exc),
            "path": request.url.path,
            "traceback": error_traceback
        }
    )


async def generate_stream(question: str) -> AsyncGenerator[str, None]:
    """
    Generates a streaming response from the LLM.
    Yields each token as it's generated.
    """
    prompt = f"{SYSTEM_PROMPT}\n\nUser: {question}\nAssistant:"

    payload = {
        "model": "gemma3:270m",
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.7,
            "num_predict": 256
        }
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", OLLAMA_URL, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                token = data["response"]
                                yield token
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        yield f"\n\nError: {str(e)}"


@app.get("/ask")
async def ask_question(
    q: str = Query(..., description="Question to ask the LLM")
) -> StreamingResponse:
    """
    Streams an AI-generated response to the given question.

    Use with curl: curl -N 'http://llm.startup.net/ask?q=your_question'
    For spaces, use underscores or URL encoding (%20)
    The -N flag disables buffering to see the streaming effect.

    Parameters:
    - q: Question to ask the LLM
    """
    return StreamingResponse(
        generate_stream(q),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with service information."""
    return {
        "service": "LLM Streaming Service",
        "version": "1.0.0",
        "model": "gemma3:270m",
        "endpoint": "/ask?q=<your question>",
        "usage": "curl -N 'http://llm.startup.net/ask?q=What_is_DNS?' (use _ or %20 for spaces)"
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
