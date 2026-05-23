from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.models import DeviceSummary, TelemetryReadingIn, TelemetryReadingOut
from app.services.storage import TelemetryStore, get_store

router = APIRouter(prefix="/devices", tags=["telemetry"])

DeviceIdPath = Path(
    description="Device identifier.",
    min_length=1,
    max_length=64,
    pattern=r"^[a-zA-Z0-9_-]+$",
)


@router.post(
    "/{device_id}/telemetry",
    response_model=TelemetryReadingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a telemetry reading",
)
async def ingest_telemetry(
    payload: TelemetryReadingIn,
    device_id: str = DeviceIdPath,
    store: TelemetryStore = Depends(get_store),
) -> TelemetryReadingOut:
    reading = TelemetryReadingOut(device_id=device_id, **payload.model_dump())
    await store.add(reading=reading)
    return reading


@router.get(
    "/{device_id}/telemetry",
    response_model=list[TelemetryReadingOut],
    summary="List recent telemetry readings for a device",
)
async def list_telemetry(
    device_id: str = DeviceIdPath,
    limit: int = Query(default=100, ge=1, le=1000),
    store: TelemetryStore = Depends(get_store),
) -> list[TelemetryReadingOut]:
    readings = await store.list_for_device(device_id, limit=limit)
    if not readings:
        raise HTTPException(
            status_code=404, detail=f"No telemetry found for device '{device_id}'"
        )
    return readings


@router.get(
    "",
    response_model=list[DeviceSummary],
    summary="List known devices",
)
async def list_devices(
    store: TelemetryStore = Depends(get_store),
) -> list[DeviceSummary]:
    device_ids = await store.list_devices()
    summaries: list[DeviceSummary] = []
    for device_id in device_ids:
        readings = await store.list_for_device(device_id, limit=1000)
        summaries.append(
            DeviceSummary(
                device_id=device_id,
                reading_count=len(readings),
                last_seen=readings[-1].timestamp if readings else None,
            )
        )
    return summaries
