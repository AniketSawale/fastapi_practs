import asyncio
from collections import defaultdict, deque
from typing import Protocol

from app.models import TelemetryReadingOut


class TelemetryStore(Protocol):
    """Storage interface. Async so implementations can be DB-backed without changing."""

    async def add(self, reading: TelemetryReadingOut) -> None: ...
    async def list_for_device(
        self, device_id: str, limit: int = 100) -> list[TelemetryReadingOut]: ...

    async def list_devices(self) -> list[str]: ...


class InMemoryTelemetryStore:
    """Thread-safe in-memory store. Suitable for dev and single-instance deployments."""

    def __init__(self, max_per_device: int = 1000) -> None:
        self.max_per_device = max_per_device
        self._data: dict[str, deque[TelemetryReadingOut]] = defaultdict(
            lambda: deque(maxlen=max_per_device)
        )
        self._lock = asyncio.Lock()

    async def add(self, reading: TelemetryReadingOut) -> None:
        async with self._lock:
            self._data[reading.device_id].append(reading)

    async def list_for_device(
        self, device_id: str, limit: int = 100
    ) -> list[TelemetryReadingOut]:
        async with self._lock:
            return list(self._data[device_id])[-limit:]

    async def list_devices(self) -> list[str]:
        async with self._lock:
            return list(self._data.keys())


_store: InMemoryTelemetryStore | None = None


def get_store() -> TelemetryStore:
    """FastAPI depenedency that returns the storage instance."""

    global _store
    if _store is None:
        _store = InMemoryTelemetryStore()

    return _store
