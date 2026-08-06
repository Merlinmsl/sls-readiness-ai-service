from fastapi import FastAPI

app = FastAPI(
    title="SLS Readiness AI Service",
    description=(
        "AI-powered SLS readiness assessment microservice "
        "for supported Sri Lankan food businesses."
    ),
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the current service health status."""
    return {
        "status": "healthy",
        "service": "sls-readiness-ai-service",
        "version": "0.1.0",
    }