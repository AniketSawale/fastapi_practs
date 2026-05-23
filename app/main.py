from fastapi import FastAPI

from app.config import get_settings
from app.routers import telemetry, summary

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Telemetry ingest and analystcs for connected lighting devices.",
    version="0.1.0",
)

app.include_router(telemetry.router)
app.include_router(summary.router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
