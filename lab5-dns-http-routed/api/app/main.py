from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional, Any
import asyncio
import traceback

app = FastAPI(title="Backend API Service", version="1.0.0")

visitor_count = 0


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - simple OK message."""
    return {"status": "ok", "message": "Backend API is running"}


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested path '{request.url.path}' does not exist",
            "available_endpoints": ["/", "/visitors", "/delay", "/payload", "/health"]
        }
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

    if missing_params:
        endpoint_help = {
            "/delay": "Usage: /delay?seconds=10 (seconds: 0-300)",
            "/payload": "Usage: /payload?chars=50000 (chars: 1-1000000)"
        }

        help_message = endpoint_help.get(request.url.path, "Check the API documentation")

        return JSONResponse(
            status_code=422,
            content={
                "error": "Missing required query parameter",
                "missing": missing_params,
                "help": help_message
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


@app.get("/visitors")
async def get_visitors() -> dict[str, int]:
    """
    Returns the number of visitors.
    Increments the counter on each request.
    """
    try:
        global visitor_count
        visitor_count += 1
        return {"visitors": visitor_count}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error incrementing visitor count",
                "type": type(e).__name__,
                "message": str(e)
            }
        )


@app.get("/delay")
async def delay_response(
    seconds: int = Query(..., ge=0, le=300, description="Number of seconds to wait before responding")
) -> dict[str, Any]:
    """
    Waits for the specified number of seconds before responding.
    Useful for testing TCP timeout behavior.

    Parameters:
    - seconds: Time to wait (0-300 seconds) - REQUIRED

    Example: /delay?seconds=10
    """
    try:
        await asyncio.sleep(seconds)
        return {
            "message": f"Responded after {seconds} seconds",
            "seconds": seconds
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error during delay",
                "type": type(e).__name__,
                "message": str(e),
                "requested_seconds": seconds
            }
        )


@app.get("/payload")
async def large_payload(
    chars: int = Query(..., ge=1, le=1000000, description="Number of characters to return")
) -> dict[str, Any]:
    """
    Returns a response with the specified number of characters.
    Useful for testing TCP multi-packet transmission.

    Parameters:
    - chars: Number of characters to include in the payload (1-1000000) - REQUIRED

    Example: /payload?chars=50000
    """
    try:
        payload_data = "A" * chars
        return {
            "message": "Large payload response",
            "chars": chars,
            "data": payload_data
        }
    except MemoryError as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Memory error: payload too large",
                "type": "MemoryError",
                "message": str(e),
                "requested_chars": chars
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error generating payload",
                "type": type(e).__name__,
                "message": str(e),
                "requested_chars": chars
            }
        )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
