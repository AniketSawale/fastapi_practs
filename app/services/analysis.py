import json
from statistics import mean, stdev
from typing import Any

from app.models import TelemetryReadingOut


def aggregate_readings(readings: list[TelemetryReadingOut]) -> dict[str, Any]:

    if not readings:
        return {}

    lumens = [r.lumens for r in readings]
    power = [r.power_watts for r in readings]
    temp = [r.temperature_c for r in readings]

    status_counts: dict[str, int] = {}
    for r in readings:
        status_counts[r.status.value] = status_counts.get(
            r.status.value, 0) + 1

    return {
        "reading_count": len(readings),
        "time_from": readings[0].timestamp.isoformat(),
        "time_to": readings[-1].timestamp.isoformat(),
        "lumens_mean": round(mean(lumens), 1),
        "lumens_range": [round(min(lumens), 1), round(max(lumens), 1)],
        "lumens_stdev": round(stdev(lumens), 1) if len(lumens) > 1 else 0.0,
        "power_watts_mean": round(mean(power), 2),
        "power_watts_range": [round(min(power), 2), round(max(power), 2)],
        "temperature_c_mean": round(mean(temp), 1),
        "temperature_c_range": [round(min(temp), 1), round(max(temp), 1)],
        "motion_events": sum(1 for r in readings if r.motion_detected),
        "status_counts": status_counts,
    }


def build_summary_prompt(device_id: str, status: dict[str, Any]) -> str:
    return (
        f"Device ID: {device_id}\n"
        f"Telemetry statistics:\n{json.dumps(stats, indent=2)}\n\n"
        "Write a 2-3 sentence plain-language summary of this device's recent state. "
        "Highlight anomalies (errors, unusual ranges) if present; otherwise note that "
        "operation is normal."
    )
