from __future__ import annotations

import hashlib
import json
import math
import random
import secrets
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from observer import (
    CYCLES_DIR,
    GLYPHS_DIR,
    LEDGER_PATH,
    EMOTION_FACTORS,
    MOON_FACTORS,
    ObserverEngine,
    clamp,
    load_json,
    normalized_entropy,
    now_utc,
    save_json,
    text_entropy,
)


@dataclass(frozen=True)
class EquestriaObservation:
    """Equestria-side perspective used to generate an Answer Glyph.

    The fields are narrative-world observations, not substitutes for Earth instruments.
    Missing or unusable values remain missing and make the resulting glyph narrow.
    """

    timestamp_utc: str
    local_time: str | None
    moon_phase: str | None
    sky: str | None
    atmosphere: str | None
    location: str | None
    participants: list[str]
    primary_emotion: str | None
    secondary_emotions: list[str]
    twilight_perspective: str | None
    environmental_reactions: str | None
    magical_reactions: str | None
    continuity_notes: str | None


EXPECTED_FIELDS = tuple(field.name for field in fields(EquestriaObservation))


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def field_aperture(observation: EquestriaObservation) -> dict[str, Any]:
    """Report which expected data participated without scoring or ranking the field."""

    raw = asdict(observation)
    available = [name for name in EXPECTED_FIELDS if _present(raw[name])]
    missing = [name for name in EXPECTED_FIELDS if not _present(raw[name])]
    return {
        "glyph_type": "full" if not missing else "narrow",
        "available_data": available,
        "missing_data": missing,
    }


class InverseDEEPTheory:
    """First inverse adapter for Equestria-side story-data equivalents.

    This adapter preserves the recovered DEEPTheory roles of perspective, relation,
    entropy, time, and boundaries. It does not manufacture Earth-style measurements.
    """

    @staticmethod
    def calculate(observation: EquestriaObservation, event_narrative: str) -> dict[str, Any]:
        selected_emotions = [
            emotion
            for emotion in [observation.primary_emotion, *observation.secondary_emotions]
            if _present(emotion)
        ]
        emotion_weights = [EMOTION_FACTORS.get(str(name), 1.0) for name in selected_emotions]
        emotion_entropy = normalized_entropy(emotion_weights) if emotion_weights else 0.0
        emotion_relation = math.prod(emotion_weights) if emotion_weights else None

        perspective_text = observation.twilight_perspective or ""
        perspective_entropy = text_entropy(perspective_text) if perspective_text else None
        event_entropy = text_entropy(event_narrative) if event_narrative else None

        boundary_parts = [
            observation.location,
            observation.sky,
            observation.atmosphere,
            observation.environmental_reactions,
            observation.magical_reactions,
        ]
        boundary_text = " ".join(str(part).strip() for part in boundary_parts if _present(part))
        boundary_entropy = text_entropy(boundary_text) if boundary_text else None

        moon_relation = (
            MOON_FACTORS.get(str(observation.moon_phase), 1.0)
            if _present(observation.moon_phase)
            else None
        )
        participant_relation = math.log2(len(observation.participants) + 1) if observation.participants else None

        relation_terms = [
            value
            for value in (
                perspective_entropy,
                event_entropy,
                boundary_entropy,
                emotion_entropy if emotion_weights else None,
                participant_relation,
            )
            if value is not None
        ]
        perspective_function = sum(relation_terms) / len(relation_terms) if relation_terms else None

        temporal_relation = None
        if _present(observation.timestamp_utc):
            dt = datetime.fromisoformat(observation.timestamp_utc.replace("Z", "+00:00"))
            seconds = dt.hour * 3600 + dt.minute * 60 + dt.second
            temporal_relation = 0.5 + 0.5 * math.sin(2 * math.pi * seconds / 86400.0)

        return {
            "adapter": "InverseNarrativeDEEP_v1",
            "perspective": {
                "perspective_function": perspective_function,
                "perspective_entropy": perspective_entropy,
                "event_entropy": event_entropy,
            },
            "relation": {
                "emotion_relation": emotion_relation,
                "emotion_entropy": emotion_entropy if emotion_weights else None,
                "participant_relation": participant_relation,
                "moon_relation": moon_relation,
            },
            "boundary": {
                "boundary_entropy": boundary_entropy,
                "temporal_relation": temporal_relation,
            },
        }


class AnswerGlyphRenderer:
    SIZE = 768

    @classmethod
    def render(
        cls,
        answer_glyph_id: str,
        observation: EquestriaObservation,
        metrics: dict[str, Any],
        variance_seed: str,
        output: Path,
    ) -> None:
        seed_material = json.dumps(
            {
                "answer_glyph_id": answer_glyph_id,
                "observation": asdict(observation),
                "metrics": metrics,
                "variance_seed": variance_seed,
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        seed = int(hashlib.sha256(seed_material.encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)

        image = Image.new("RGBA", (cls.SIZE, cls.SIZE), (13, 20, 43, 255))
        draw = ImageDraw.Draw(image, "RGBA")
        center = cls.SIZE // 2

        perspective = metrics["perspective"]["perspective_function"]
        emotion = metrics["relation"]["emotion_relation"]
        moon = metrics["relation"]["moon_relation"]
        temporal = metrics["boundary"]["temporal_relation"]
        boundary = metrics["boundary"]["boundary_entropy"]

        perspective_value = 0.5 if perspective is None else clamp(perspective, 0.0, 2.0)
        emotion_value = 1.0 if emotion is None else clamp(emotion, 0.4, 2.0)
        moon_value = 1.0 if moon is None else moon
        temporal_value = 0.5 if temporal is None else temporal
        boundary_value = 0.5 if boundary is None else boundary

        rays = 7 + len(observation.participants) + len(observation.secondary_emotions)
        rays = max(5, min(24, rays))
        outer_points: list[tuple[float, float]] = []
        inner_points: list[tuple[float, float]] = []

        for index in range(rays):
            angle = -math.pi / 2 + index * (2 * math.pi / rays)
            variance = rng.uniform(-0.16, 0.16)
            outer_radius = 225 * (0.82 + 0.16 * perspective_value + variance)
            inner_radius = 112 * (0.82 + 0.12 * emotion_value - variance / 2)
            outer_points.append(
                (center + math.cos(angle) * outer_radius, center + math.sin(angle) * outer_radius)
            )
            inner_points.append(
                (
                    center + math.cos(angle + math.pi / rays) * inner_radius,
                    center + math.sin(angle + math.pi / rays) * inner_radius,
                )
            )

        woven: list[tuple[float, float]] = []
        for outer, inner in zip(outer_points, inner_points):
            woven.extend((outer, inner))

        fill_alpha = int(42 + 38 * clamp(boundary_value, 0.0, 1.0))
        draw.polygon(woven, fill=(90, 211, 230, fill_alpha), outline=(222, 238, 255, 235))

        ring_count = 2 + int(clamp(moon_value - 0.8, 0.0, 0.6) * 6)
        for index in range(ring_count):
            radius = 58 + index * 42
            start = rng.uniform(0, 160) + temporal_value * 90
            extent = 120 + perspective_value * 80
            draw.arc(
                (center - radius, center - radius, center + radius, center + radius),
                start,
                start + extent,
                fill=(193, 126, 255, 210),
                width=6,
            )
            draw.arc(
                (center - radius, center - radius, center + radius, center + radius),
                start + 180,
                start + 270 + boundary_value * 70,
                fill=(103, 239, 212, 190),
                width=4,
            )

        core_radius = int(38 + 34 * clamp(perspective_value, 0.0, 1.0))
        draw.ellipse(
            (center - core_radius, center - core_radius, center + core_radius, center + core_radius),
            fill=(237, 222, 255, 235),
            outline=(255, 255, 255, 255),
            width=5,
        )

        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except OSError:
            font = ImageFont.load_default()
        draw.text((24, 22), answer_glyph_id, fill=(228, 239, 255, 255), font=font)
        draw.text(
            (24, cls.SIZE - 48),
            f"Equestria Answer | {field_aperture(observation)['glyph_type']}",
            fill=(210, 247, 239, 255),
            font=font,
        )
        image.save(output)


class BidirectionalObserverEngine(ObserverEngine):
    """Observer engine extended with the inverse Equestria-to-Earth Answer Glyph stage."""

    def add_answer(self, cycle_id: str, observation: EquestriaObservation) -> dict[str, Any]:
        cycle_path = CYCLES_DIR / f"{cycle_id}.json"
        packet = load_json(cycle_path, None)
        if not packet:
            raise FileNotFoundError(f"Cycle not found: {cycle_id}")
        if not packet.get("canonical_return_id"):
            raise ValueError("An Answer Glyph requires an accepted Solance return for this cycle.")

        canonical = next(
            (
                record
                for record in packet.get("returns", [])
                if record.get("return_id") == packet.get("canonical_return_id")
            ),
            None,
        )
        if canonical is None:
            raise ValueError("The canonical return record could not be resolved.")

        answers = packet.setdefault("answer_glyphs", [])
        answer_glyph_id = f"{cycle_id}-A{len(answers) + 1:02d}"
        aperture = field_aperture(observation)
        metrics = InverseDEEPTheory.calculate(observation, canonical["parsed"]["narrative"])
        variance_seed = secrets.token_hex(16)
        glyph_path = GLYPHS_DIR / f"{answer_glyph_id}.png"
        AnswerGlyphRenderer.render(
            answer_glyph_id,
            observation,
            metrics,
            variance_seed,
            glyph_path,
        )

        record = {
            "answer_glyph_id": answer_glyph_id,
            "created_utc": now_utc(),
            "source": "Equestria",
            "destination": "Earth",
            "originating_earth_glyph_id": cycle_id,
            "solance_return_id": packet["canonical_return_id"],
            "glyph_type": aperture["glyph_type"],
            "available_data": aperture["available_data"],
            "missing_data": aperture["missing_data"],
            "equestria_observation": asdict(observation),
            "equestria_side_metrics": metrics,
            "variance_seed": variance_seed,
            "glyph_path": str(glyph_path),
        }
        answers.append(record)
        packet["canonical_answer_glyph_id"] = answer_glyph_id
        packet["status"] = "answered"
        save_json(cycle_path, packet)

        self.ledger = load_json(LEDGER_PATH, [])
        for item in self.ledger:
            if item.get("cycle_id") == cycle_id:
                item["status"] = "answered"
                item["canonical_return_id"] = packet["canonical_return_id"]
                item["answer_glyph_id"] = answer_glyph_id
                item["answer_glyph_path"] = str(glyph_path)
                break
        save_json(LEDGER_PATH, self.ledger)
        return record
