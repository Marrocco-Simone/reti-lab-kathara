from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
import httpx
import traceback

app = FastAPI(title="Frontend Service", version="1.0.0")


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Generic exception handler for debugging."""
    error_traceback = traceback.format_exc()

    # Return HTML error for browser requests, JSON for API requests
    if "text/html" in request.headers.get("accept", ""):
        return HTMLResponse(
            content=f"""<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body>
<h1>Internal Server Error</h1>
<p>Type: {type(exc).__name__}</p>
<p>Message: {str(exc)}</p>
<pre>{error_traceback}</pre>
</body>
</html>""",
            status_code=500
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": error_traceback
            }
        )


@app.get("/", response_class=HTMLResponse)
async def get_visitors_page() -> str:
    """
    Fetches visitor count from the backend API and returns an HTML page.
    Demonstrates DNS resolution: frontend.startup.net -> api.startup.net
    """
    backend_url = "http://api.startup.net/visitors"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(backend_url)
            response.raise_for_status()
            data = response.json()

        visitor_count = data.get("visitors", 0)

        html_content = f"""<!DOCTYPE html>
<html>
<head><title>Visitor Counter</title></head>
<body>
<h1>We had {visitor_count} visitors!</h1>
</body>
</html>"""

        return html_content

    except httpx.RequestError as exc:
        error_html = f"""<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body>
<h1>Error connecting to backend: {str(exc)}</h1>
</body>
</html>"""
        return error_html
    except httpx.HTTPStatusError as exc:
        error_html = f"""<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body>
<h1>Backend error: {exc.response.status_code}</h1>
</body>
</html>"""
        return error_html


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
