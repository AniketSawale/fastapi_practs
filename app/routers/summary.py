from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.models import SummaryResponse
from app.services.analysis import aggregate_readings, build_summary_prompt
from app.services.llm import LLMClient, get_llm_client
from app.services.storage import TelemetryStore, get_store
import httpx
router = APIRouter(prefix="/devices", tags=["summary"])

DeviceIdPath = Path(
    description="Device identifier",
    min_length=1,
    max_length=64,
    pattern=r"^[a-zA-Z0-9_-]+$",
)


@router.get(
    "/{device_id}/summary",
    response_model=SummaryResponse,
    summary="LLM-generated summary of recent telemetry",
)
async def device_summary(
    device_id: str = DeviceIdPath,
    limit: int = Query(default=100, ge=1, le=1000),
    store: TelemetryStore = Depends(get_store),
    llm: LLMClient = Depends(get_llm_client),
) -> SummaryResponse:
    """Aggregate recent readings and return an LLM-generated plain-language summary."""
    readings = await store.list_for_device(device_id, limit=limit)
    if not readings:
        raise HTTPException(
            status_code=404,
            detail=f"No telemetry found for device '{device_id}'",
        )

    stats = aggregate_readings(readings)
    prompt = build_summary_prompt(device_id, stats)

    try:
        summary_text = await llm.summarize(prompt)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="LLM provider returned an error",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error generating summary",
        ) from exc

    return SummaryResponse(
        device_id=device_id,
        reading_count=stats["reading_count"],
        summary=summary_text,
        stats=stats,
    )
