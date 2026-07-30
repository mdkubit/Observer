from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USER_AGENT = "Universal-Horizon-Observer/0.2"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
NOAA_KP_URL = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
DEFAULT_SCHUMANN_HZ = 7.83


@dataclass(frozen=True)
class Datum:
    value: Any
    timestamp_utc: str
    source: str
    method: str
    status: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_json(url: str, params: dict[str, Any] | None = None, timeout: float = 8.0) -> Any:
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(str(exc)) from exc


def moon_phase(at: datetime | None = None) -> Datum:
    at = at or datetime.now(timezone.utc)
    if at.tzinfo is None:
        at = at.replace(tzinfo=timezone.utc)
    reference = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    synodic_month = 29.53058867
    age_days = ((at.astimezone(timezone.utc) - reference).total_seconds() / 86400.0) % synodic_month
    fraction = age_days / synodic_month
    names = [
        "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
        "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent",
    ]
    phase = names[int((fraction * 8) + 0.5) % 8]
    return Datum(
        value={"phase": phase, "age_days": age_days, "illumination_fraction": (1 - math.cos(2 * math.pi * fraction)) / 2},
        timestamp_utc=at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        source="local astronomical calculation",
        method="calculated",
        status="ok",
    )


def weather(latitude: float, longitude: float) -> Datum:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
        "temperature_unit": "celsius",
        "timezone": "UTC",
    }
    try:
        payload = _get_json(OPEN_METEO_URL, params)
        current = payload["current"]
        code = int(current["weather_code"])
        descriptions = {
            0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast clouds",
            45: "fog", 48: "depositing rime fog", 51: "light drizzle", 53: "drizzle",
            55: "dense drizzle", 56: "freezing drizzle", 57: "dense freezing drizzle",
            61: "light rain", 63: "rain", 65: "heavy rain", 66: "freezing rain",
            67: "heavy freezing rain", 71: "light snow", 73: "snow", 75: "heavy snow",
            77: "snow grains", 80: "rain showers", 81: "rain showers", 82: "violent rain showers",
            85: "snow showers", 86: "heavy snow showers", 95: "thunderstorm",
            96: "thunderstorm with hail", 99: "severe thunderstorm with hail",
        }
        return Datum(
            value={
                "weather": descriptions.get(code, f"weather code {code}"),
                "temperature_c": float(current["temperature_2m"]),
                "weather_code": code,
            },
            timestamp_utc=str(current.get("time", now_utc())).replace("+00:00", "Z"),
            source="Open-Meteo current weather",
            method="fetched",
            status="ok",
        )
    except (RuntimeError, KeyError, TypeError, ValueError) as exc:
        return Datum(None, now_utc(), "Open-Meteo current weather", "fetched", "error", str(exc))


def geomagnetic_kp() -> Datum:
    try:
        payload = _get_json(NOAA_KP_URL)
        if not isinstance(payload, list) or not payload:
            raise ValueError("No Kp records returned")
        latest = payload[-1]
        return Datum(
            value=float(latest["kp_index"]),
            timestamp_utc=str(latest.get("time_tag", now_utc())).replace("+00:00", "Z"),
            source="NOAA SWPC planetary K-index 1-minute feed",
            method="fetched",
            status="ok",
        )
    except (RuntimeError, KeyError, TypeError, ValueError) as exc:
        return Datum(None, now_utc(), "NOAA SWPC planetary K-index 1-minute feed", "fetched", "error", str(exc))


def schumann_reference(manual_value: float = DEFAULT_SCHUMANN_HZ) -> Datum:
    """Return an explicit reference/manual value.

    The historical scraper was fragile and did not provide a trustworthy, stable machine-readable
    source. Until a source is selected and validated, Observer records this as a manual/reference
    datum rather than pretending it was fetched live.
    """
    return Datum(
        value=float(manual_value),
        timestamp_utc=now_utc(),
        source="Observer Schumann reference",
        method="manual_reference",
        status="ok",
    )


def location(latitude: float, longitude: float, elevation_m: float) -> Datum:
    return Datum(
        value={"latitude": latitude, "longitude": longitude, "elevation_m": elevation_m},
        timestamp_utc=now_utc(),
        source="Observer sanctum configuration",
        method="manual_configuration",
        status="ok",
    )


def collect_earth_data(
    latitude: float,
    longitude: float,
    elevation_m: float,
    schumann_hz: float = DEFAULT_SCHUMANN_HZ,
    fetch_live: bool = True,
) -> dict[str, dict[str, Any]]:
    weather_datum = weather(latitude, longitude) if fetch_live else Datum(
        None, now_utc(), "Open-Meteo current weather", "fetched", "disabled", "Live fetch disabled"
    )
    kp_datum = geomagnetic_kp() if fetch_live else Datum(
        None, now_utc(), "NOAA SWPC planetary K-index 1-minute feed", "fetched", "disabled", "Live fetch disabled"
    )
    return {
        "weather": weather_datum.to_dict(),
        "geomagnetic_kp": kp_datum.to_dict(),
        "moon": moon_phase().to_dict(),
        "schumann": schumann_reference(schumann_hz).to_dict(),
        "location": location(latitude, longitude, elevation_m).to_dict(),
    }


def usable_value(datum: dict[str, Any], fallback: Any) -> Any:
    return datum.get("value") if datum.get("status") == "ok" and datum.get("value") is not None else fallback
