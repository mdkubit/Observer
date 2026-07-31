from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from lattice_projection_inputs import AnswerProjectionInputs, EarthProjectionInputs
from observer import ObservationInput, clamp


class LatticeRoutedEarthGlyphRenderer:
    """Current Earth renderer routed through the lattice projection-input seam.

    Geometry, seed material, colors, dimensions, and output remain unchanged.
    The only architectural change is that renderer-facing values are now obtained
    from EarthProjectionInputs instead of reading nested metrics directly.
    """

    SIZE = 768

    @classmethod
    def render(
        cls,
        cycle_id: str,
        snapshot: ObservationInput,
        metrics: dict[str, Any],
        output: Path,
    ) -> None:
        packet = {
            "cycle_id": cycle_id,
            "parent_cycle_id": snapshot.parent_cycle_id,
            "earth_snapshot": asdict(snapshot),
            "earth_side_metrics": metrics,
        }
        projection = EarthProjectionInputs.from_packet(packet)
        values = projection.legacy_renderer_values()

        seed_text = json.dumps(
            {"cycle": cycle_id, "snapshot": asdict(snapshot), "metrics": metrics},
            sort_keys=True,
        )
        seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)
        image = Image.new("RGBA", (cls.SIZE, cls.SIZE), (20, 13, 38, 255))
        draw = ImageDraw.Draw(image, "RGBA")
        center = cls.SIZE // 2

        harmonic = values["harmonic"]
        tone = values["tone"]
        pulse = values["pulse"]
        entanglement = values["entanglement"]
        delta_hz = values["delta_hz"]

        for radius in range(360, 40, -18):
            alpha = int(15 + 55 * (radius / 360))
            draw.ellipse(
                (center - radius, center - radius, center + radius, center + radius),
                outline=(138, 92, 246, alpha),
                width=2,
            )

        points = []
        lobes = 11
        for index in range(lobes * 2):
            angle = -math.pi / 2 + index * math.pi / lobes
            base = 230 if index % 2 == 0 else 115
            modulation = 1 + 0.18 * math.sin(index * pulse + harmonic * math.pi)
            radius = base * modulation
            points.append(
                (center + math.cos(angle) * radius, center + math.sin(angle) * radius)
            )
        fill = (171, int(80 + 120 * tone), 244, 72)
        draw.polygon(points, fill=fill, outline=(244, 219, 255, 235))

        ring_count = 3 + int(clamp(entanglement, 0, 1) * 5)
        for idx in range(ring_count):
            radius = 72 + idx * 38
            start = rng.uniform(0, 120)
            extent = 170 + tone * 160
            draw.arc(
                (center - radius, center - radius, center + radius, center + radius),
                start,
                start + extent,
                fill=(90, 229, 219, 210),
                width=7,
            )
            draw.arc(
                (center - radius, center - radius, center + radius, center + radius),
                start + 190,
                start + 335,
                fill=(255, 111, 97, 185),
                width=4,
            )

        delta_scale = clamp(delta_hz / 0.02, 0.0, 1.0)
        core_radius = int(42 + 48 * (1 - delta_scale))
        draw.ellipse(
            (center - core_radius, center - core_radius, center + core_radius, center + core_radius),
            fill=(255, 243, 174, 230),
            outline=(255, 255, 255, 255),
            width=5,
        )
        draw.line((center, 95, center, cls.SIZE - 95), fill=(255, 255, 255, 80), width=2)
        draw.line((95, center, cls.SIZE - 95, center), fill=(255, 255, 255, 80), width=2)

        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except OSError:
            font = ImageFont.load_default()
        draw.text((24, 22), cycle_id, fill=(238, 225, 255, 255), font=font)
        draw.text(
            (24, cls.SIZE - 48),
            f"7.830 ↔ 7.835 Hz | Δ {delta_hz:.3f} Hz",
            fill=(218, 240, 255, 255),
            font=font,
        )
        image.save(output)


class LatticeRoutedAnswerGlyphRenderer:
    """Current Answer renderer routed through the lattice projection-input seam."""

    SIZE = 768

    @classmethod
    def render(
        cls,
        answer_glyph_id: str,
        observation: Any,
        metrics: dict[str, Any],
        variance_seed: str,
        output: Path,
    ) -> None:
        cycle_id = answer_glyph_id.rsplit("-A", 1)[0]
        cycle_packet = {"cycle_id": cycle_id}
        answer_record = {
            "answer_glyph_id": answer_glyph_id,
            "solance_return_id": f"{cycle_id}-R01",
            "equestria_observation": asdict(observation),
            "equestria_side_metrics": metrics,
        }
        projection = AnswerProjectionInputs.from_record(cycle_packet, answer_record)
        values = projection.legacy_renderer_values()

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

        perspective_value = values["perspective_value"]
        emotion_value = values["emotion_value"]
        moon_value = values["moon_value"]
        temporal_value = values["temporal_value"]
        boundary_value = values["boundary_value"]
        rays = values["rays"]

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

        draw.polygon(
            woven,
            fill=(90, 211, 230, values["fill_alpha"]),
            outline=(222, 238, 255, 235),
        )

        for index in range(values["ring_count"]):
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

        core_radius = values["core_radius"]
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
        glyph_type = "full" if all(
            value not in (None, "", [], (), {}) for value in asdict(observation).values()
        ) else "narrow"
        draw.text(
            (24, cls.SIZE - 48),
            f"Equestria Answer | {glyph_type}",
            fill=(210, 247, 239, 255),
            font=font,
        )
        image.save(output)
