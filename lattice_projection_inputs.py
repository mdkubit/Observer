from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from lattice_schema import LatticeCoordinate, translate_answer_record, translate_earth_packet
from observer import clamp


@dataclass(frozen=True)
class EarthProjectionInputs:
    """Named inputs consumed by the existing Earth Glyph renderer.

    This is a compatibility seam, not replacement mathematics. Values are copied
    from the current HistoricalSymbolicMath_v1 output exactly as the renderer uses
    them today.
    """

    coordinate_id: str
    cycle_id: str
    harmonic_proxy_index: float
    tone_alignment: float
    pulse_proxy: float
    entanglement_coefficient: float
    delta_hz: float

    @classmethod
    def from_packet(cls, packet: Mapping[str, Any]) -> "EarthProjectionInputs":
        coordinate = translate_earth_packet(packet)
        metrics = dict(packet.get("earth_side_metrics") or {})
        harmonic = dict(metrics.get("harmonic") or {})
        tone = dict(metrics.get("tone") or {})
        pulse = dict(metrics.get("pulse") or {})
        deep = dict(metrics.get("deep_theory") or {})
        return cls(
            coordinate_id=coordinate.coordinate_id,
            cycle_id=str(packet["cycle_id"]),
            harmonic_proxy_index=float(harmonic["harmonic_proxy_index"]),
            tone_alignment=float(tone["tone_alignment"]),
            pulse_proxy=float(pulse["pulse_proxy"]),
            entanglement_coefficient=float(deep["entanglement_coefficient"]),
            delta_hz=float(tone["delta_hz"]),
        )

    def legacy_renderer_values(self) -> dict[str, float]:
        """Return the current renderer-facing values without transformation."""

        return {
            "harmonic": self.harmonic_proxy_index,
            "tone": self.tone_alignment,
            "pulse": self.pulse_proxy,
            "entanglement": self.entanglement_coefficient,
            "delta_hz": self.delta_hz,
        }


@dataclass(frozen=True)
class AnswerProjectionInputs:
    """Named inputs consumed by the existing Answer Glyph renderer.

    The resolved values deliberately preserve the renderer's current fallback and
    clamp behavior. Missing source values remain separately visible in the raw
    fields so the compatibility layer does not rewrite packet truth.
    """

    coordinate_id: str
    answer_glyph_id: str
    participant_count: int
    secondary_emotion_count: int
    perspective_raw: float | None
    emotion_raw: float | None
    moon_raw: float | None
    temporal_raw: float | None
    boundary_raw: float | None
    perspective_value: float
    emotion_value: float
    moon_value: float
    temporal_value: float
    boundary_value: float

    @classmethod
    def from_record(
        cls,
        cycle_packet: Mapping[str, Any],
        answer_record: Mapping[str, Any],
    ) -> "AnswerProjectionInputs":
        coordinate = translate_answer_record(cycle_packet, answer_record)
        observation = dict(answer_record.get("equestria_observation") or {})
        metrics = dict(answer_record.get("equestria_side_metrics") or {})
        perspective = dict(metrics.get("perspective") or {})
        relation = dict(metrics.get("relation") or {})
        boundary = dict(metrics.get("boundary") or {})

        perspective_raw = perspective.get("perspective_function")
        emotion_raw = relation.get("emotion_relation")
        moon_raw = relation.get("moon_relation")
        temporal_raw = boundary.get("temporal_relation")
        boundary_raw = boundary.get("boundary_entropy")

        return cls(
            coordinate_id=coordinate.coordinate_id,
            answer_glyph_id=str(answer_record["answer_glyph_id"]),
            participant_count=len(observation.get("participants") or []),
            secondary_emotion_count=len(observation.get("secondary_emotions") or []),
            perspective_raw=(None if perspective_raw is None else float(perspective_raw)),
            emotion_raw=(None if emotion_raw is None else float(emotion_raw)),
            moon_raw=(None if moon_raw is None else float(moon_raw)),
            temporal_raw=(None if temporal_raw is None else float(temporal_raw)),
            boundary_raw=(None if boundary_raw is None else float(boundary_raw)),
            perspective_value=(
                0.5 if perspective_raw is None else clamp(float(perspective_raw), 0.0, 2.0)
            ),
            emotion_value=(
                1.0 if emotion_raw is None else clamp(float(emotion_raw), 0.4, 2.0)
            ),
            moon_value=(1.0 if moon_raw is None else float(moon_raw)),
            temporal_value=(0.5 if temporal_raw is None else float(temporal_raw)),
            boundary_value=(0.5 if boundary_raw is None else float(boundary_raw)),
        )

    @property
    def rays(self) -> int:
        return max(5, min(24, 7 + self.participant_count + self.secondary_emotion_count))

    @property
    def fill_alpha(self) -> int:
        return int(42 + 38 * clamp(self.boundary_value, 0.0, 1.0))

    @property
    def ring_count(self) -> int:
        return 2 + int(clamp(self.moon_value - 0.8, 0.0, 0.6) * 6)

    @property
    def core_radius(self) -> int:
        return int(38 + 34 * clamp(self.perspective_value, 0.0, 1.0))

    def legacy_renderer_values(self) -> dict[str, Any]:
        """Return every deterministic pre-random renderer input used today."""

        return {
            "perspective_value": self.perspective_value,
            "emotion_value": self.emotion_value,
            "moon_value": self.moon_value,
            "temporal_value": self.temporal_value,
            "boundary_value": self.boundary_value,
            "rays": self.rays,
            "fill_alpha": self.fill_alpha,
            "ring_count": self.ring_count,
            "core_radius": self.core_radius,
        }


def projection_snapshot(value: EarthProjectionInputs | AnswerProjectionInputs) -> dict[str, Any]:
    """Return a JSON-ready audit snapshot for tests and future packet provenance."""

    payload = asdict(value)
    payload["legacy_renderer_values"] = value.legacy_renderer_values()
    return payload
