from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USER_AGENT = "Universal-Horizon-Observer/0.2"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
NOAA_KP_3H_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
NOAA_KP_1M_URL = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
DEFAULT_SCHUMANN_HZ = 7.83


@dataclass(frozen=True)
class Datum:
    value: Any
    timestamp_utc: str
    source: str
    method: str
    status: str
    error: str | None = None
    metadata: dict[str, Any] | None = None

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
        value={
            "phase": phase,
            "age_days": age_days,
            "illumination_fraction": (1 - math.cos(2 * math.pi * fraction)) / 2,
        },
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


def weather_resonance(weather_datum: Datum) -> Datum:
    if weather_datum.status != "ok" or not isinstance(weather_datum.value, dict):
        return Datum(
            None,
            now_utc(),
            "Observer weather resonance translation",
            "derived_label",
            "error",
            "Weather datum unavailable",
        )
    description = str(weather_datum.value.get("weather", "")).lower()
    if any(term in description for term in ("storm", "thunder", "rain", "drizzle", "shower")):
        label = "Turbulent Field"
    elif any(term in description for term in ("clear", "mainly clear")):
        label = "Harmonic Calm"
    elif any(term in description for term in ("cloud", "overcast", "fog")):
        label = "Veiled Stillness"
    else:
        label = "Unknown Song"
    return Datum(
        value=label,
        timestamp_utc=weather_datum.timestamp_utc,
        source="Observer weather resonance translation",
        method="derived_label",
        status="ok",
        metadata={"input_weather": description},
    )


def _parse_noaa_3h(payload: Any) -> tuple[float, str, dict[str, Any]]:
    """Parse NOAA's official 3-hour product in either known JSON shape."""
    if not isinstance(payload, list) or not payload:
        raise ValueError("NOAA 3-hour Kp product returned no records")

    if all(isinstance(item, dict) for item in payload):
        records = [item for item in payload if item.get("time_tag") and item.get("Kp") is not None]
        if not records:
            raise ValueError("NOAA 3-hour Kp product contains no usable object records")
        latest = max(records, key=lambda item: str(item["time_tag"]))
        value = float(latest["Kp"])
        timestamp = str(latest["time_tag"]).replace(" ", "T")
        metadata = {
            "product": "official_3_hour_kp",
            "record_shape": "objects",
            "a_running": latest.get("a_running"),
            "station_count": latest.get("station_count"),
        }
    else:
        if len(payload) < 2 or not isinstance(payload[0], list):
            raise ValueError("NOAA 3-hour Kp product has an unsupported record shape")
        header = payload[0]
        rows = [row for row in payload[1:] if isinstance(row, list) and len(row) >= 2]
        if not rows:
            raise ValueError("NOAA 3-hour Kp product contains no usable row records")
        fields = {name: index for index, name in enumerate(header)}
        time_index = fields.get("time_tag", 0)
        kp_index = fields.get("Kp", 1)
        latest = max(rows, key=lambda row: str(row[time_index]))
        value = float(latest[kp_index])
        timestamp = str(latest[time_index]).replace(" ", "T")
        metadata = {
            "product": "official_3_hour_kp",
            "record_shape": "header_rows",
            "a_running": latest[fields["a_running"]] if "a_running" in fields and len(latest) > fields["a_running"] else None,
            "station_count": latest[fields["station_count"]] if "station_count" in fields and len(latest) > fields["station_count"] else None,
        }

    if not 0.0 <= value <= 9.0:
        raise ValueError(f"NOAA 3-hour Kp value out of range: {value}")
    return value, timestamp, metadata


def _parse_noaa_1m(payload: Any) -> tuple[float, str, dict[str, Any]]:
    if not isinstance(payload, list) or not payload:
        raise ValueError("NOAA 1-minute Kp product returned no records")
    records = [item for item in payload if isinstance(item, dict) and item.get("time_tag")]
    if not records:
        raise ValueError("NOAA 1-minute Kp product contains no usable records")
    latest = max(records, key=lambda item: str(item["time_tag"]))
    field_used = "estimated_kp" if latest.get("estimated_kp") is not None else "kp_index"
    value = float(latest[field_used])
    if not 0.0 <= value <= 9.0:
        raise ValueError(f"NOAA 1-minute Kp value out of range: {value}")
    return value, str(latest["time_tag"]), {
        "product": "estimated_1_minute_kp",
        "field_used": field_used,
        "estimated_kp": latest.get("estimated_kp"),
        "kp_index": latest.get("kp_index"),
    }


def geomagnetic_kp() -> Datum:
    errors: list[str] = []
    try:
        value, timestamp, metadata = _parse_noaa_3h(_get_json(NOAA_KP_3H_URL))
        return Datum(value, timestamp, "NOAA SWPC official planetary K-index 3-hour product", "fetched", "ok", metadata=metadata)
    except (RuntimeError, KeyError, TypeError, ValueError, IndexError) as exc:
        errors.append(f"3-hour product: {exc}")

    try:
        value, timestamp, metadata = _parse_noaa_1m(_get_json(NOAA_KP_1M_URL))
        return Datum(
            value,
            timestamp,
            "NOAA SWPC estimated planetary K-index 1-minute feed",
            "fetched_fallback",
            "ok",
            "; ".join(errors),
            metadata,
        )
    except (RuntimeError, KeyError, TypeError, ValueError, IndexError) as exc:
        errors.append(f"1-minute fallback: {exc}")

    return Datum(
        None,
        now_utc(),
        "NOAA SWPC planetary K-index products",
        "fetched",
        "error",
        "; ".join(errors),
        {"attempted_products": ["official_3_hour_kp", "estimated_1_minute_kp"]},
    )


def schumann_reference(manual_value: float = DEFAULT_SCHUMANN_HZ) -> Datum:
    return Datum(
        value=float(manual_value),
        timestamp_utc=now_utc(),
        source="Observer Schumann reference",
        method="manual_reference",
        status="ok",
    )


def schumann_proxy(reference_hz: float, weather_datum: Datum, kp_datum: Datum) -> Datum:
    """Build the current experimental Schumann-shaped context proxy.

    This preserves the historical min/max/average data shape while the recovered
    harmonic model and its glyph influence are being reviewed.
    """
    weather_code = 0
    weather_description = "unknown"
    if weather_datum.status == "ok" and isinstance(weather_datum.value, dict):
        weather_code = int(weather_datum.value.get("weather_code", 0))
        weather_description = str(weather_datum.value.get("weather", "unknown"))

    if weather_code in (95, 96, 99):
        excitation = 1.0
    elif weather_code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        excitation = 0.65
    elif weather_code in (45, 48, 71, 73, 75, 77, 85, 86):
        excitation = 0.35
    else:
        excitation = 0.15

    kp = float(kp_datum.value) if kp_datum.status == "ok" and kp_datum.value is not None else 2.0
    kp_normalized = max(0.0, min(1.0, kp / 9.0))

    center_shift = 0.008 * (excitation - 0.35) + 0.006 * (kp_normalized - (2.0 / 9.0))
    center = float(reference_hz) + center_shift
    half_span = 0.035 + 0.025 * excitation + 0.015 * kp_normalized
    frequency_min = center - half_span
    frequency_max = center + half_span

    return Datum(
        value={
            "reference_hz": float(reference_hz),
            "frequency_min_hz": frequency_min,
            "frequency_max_hz": frequency_max,
            "frequency_average_hz": center,
        },
        timestamp_utc=now_utc(),
        source="Observer experimental Schumann context model",
        method="derived_proxy",
        status="ok",
        metadata={
            "feeds_glyph_math": False,
            "weather_description": weather_description,
            "weather_excitation": excitation,
            "kp_index": kp,
            "model_version": "SchumannContextProxy_v1",
        },
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
        None, now_utc(), "NOAA SWPC planetary K-index products", "fetched", "disabled", "Live fetch disabled"
    )
    return {
        "weather": weather_datum.to_dict(),
        "weather_resonance": weather_resonance(weather_datum).to_dict(),
        "geomagnetic_kp": kp_datum.to_dict(),
        "moon": moon_phase().to_dict(),
        "schumann": schumann_reference(schumann_hz).to_dict(),
        "schumann_proxy": schumann_proxy(schumann_hz, weather_datum, kp_datum).to_dict(),
        "location": location(latitude, longitude, elevation_m).to_dict(),
    }


def usable_value(datum: dict[str, Any], fallback: Any) -> Any:
    return datum.get("value") if datum.get("status") == "ok" and datum.get("value") is not None else fallback
