from fastapi import FastAPI

app = FastAPI(
    title="Connected Lighting Telemetry API",
    description="Telemetry ingest and analytics for connected lighting devices.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """
    Liveness probe for the service.
    """
    return {"status": "ok"}
