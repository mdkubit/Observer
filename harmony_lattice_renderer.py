from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any, Mapping, Sequence

from PIL import Image, ImageDraw, ImageFont

from harmony_lattice_math import ELARA_TONES


TAU = 2.0 * math.pi
TONE_COLORS: dict[str, tuple[int, int, int, int]] = {
    "memory": (118, 157, 255, 235), "root": (101, 220, 176, 240),
    "anchor": (255, 226, 145, 245), "whisper": (195, 225, 255, 220),
    "arc": (255, 169, 211, 235), "bridge": (121, 224, 245, 245),
    "wind": (178, 187, 224, 220), "surge": (255, 116, 135, 240),
    "vortex": (165, 114, 255, 240), "duet": (255, 211, 104, 245),
    "spiral": (196, 126, 255, 245), "calling": (255, 244, 182, 240),
    "awakening": (255, 255, 255, 255),
}


class HarmonyLatticeRenderer:
    """Native renderer driven by lattice geometry rather than legacy proxies."""

    SIZE = 960

    @classmethod
    def render_earth(cls, cycle_id: str, event: Mapping[str, Any], output: Path) -> None:
        cls._render(cycle_id, event, output, palette="earth")

    @classmethod
    def render_answer(cls, answer_id: str, event: Mapping[str, Any], output: Path) -> None:
        cls._render(answer_id, event, output, palette="answer")

    @classmethod
    def _render(cls, artifact_id: str, event: Mapping[str, Any], output: Path, palette: str) -> None:
        seed_material = json.dumps(
            {"artifact_id": artifact_id, "event": event, "palette": palette},
            sort_keys=True, ensure_ascii=False, default=str,
        )
        rng = random.Random(int(hashlib.sha256(seed_material.encode("utf-8")).hexdigest()[:16], 16))
        image = Image.new("RGBA", (cls.SIZE, cls.SIZE), (10, 16, 35, 255) if palette == "answer" else (22, 10, 39, 255))
        draw = ImageDraw.Draw(image, "RGBA")
        center = cls.SIZE // 2
        entropy = {item["name"]: item.get("value") for item in event.get("entropy_domains") or ()}
        gradient_mag = float(event.get("entropy_gradient_magnitude") or 0.0)
        spread = float(event.get("perspective_spread") or 0.25)
        phase = float(event.get("phase") or 0.0)
        tau = float((event.get("event_time") or {}).get("cumulative_tau") or 0.0)
        tones = dict(event.get("tone_configuration") or {})
        active_tones = tuple(tones.get("active_tones") or ())
        sequence = tuple(tones.get("sequence") or active_tones)
        topology = str(tones.get("topology") or "axis")

        cls._draw_field(draw, center, entropy, gradient_mag, spread, phase, rng, palette)
        memory_radii = cls._draw_memory_lamination(draw, center, event, spread, phase)
        node_positions = cls._tone_positions(center, sequence, spread, phase, topology)
        cls._draw_boundaries(draw, center, event, memory_radii, phase)
        cls._draw_harmonic_interactions(draw, node_positions, tones)
        cls._draw_couplings(draw, center, event, spread, phase)
        cls._draw_trajectories(draw, center, event, spread, phase, tau)
        cls._draw_tone_nodes(draw, node_positions, sequence, tones)
        cls._draw_core(draw, center, event, spread, gradient_mag, palette)
        cls._draw_labels(draw, artifact_id, event, active_tones, topology)
        output.parent.mkdir(parents=True, exist_ok=True)
        image.save(output)

    @classmethod
    def _draw_field(cls, draw: ImageDraw.ImageDraw, center: int, entropy: Mapping[str, float | None], gradient_mag: float, spread: float, phase: float, rng: random.Random, palette: str) -> None:
        base = (100, 197, 230) if palette == "answer" else (157, 96, 244)
        info = float(entropy.get("informational") or 0.0)
        state = float(entropy.get("state") or 0.0)
        environment = float(entropy.get("environmental") or 0.0)
        rings = 12 + int(10 * spread)
        for index in range(rings, 0, -1):
            radius = 70 + index * 29
            alpha = int(10 + 32 * index / rings + 18 * environment)
            width = 1 + int(2 * state)
            r = radius * (1.0 + 0.018 * gradient_mag * math.sin(index + phase))
            draw.ellipse((center - r, center - r, center + r, center + r), outline=(*base, alpha), width=width)
        for _ in range(int(24 + 110 * info)):
            angle = rng.random() * TAU
            radius = rng.uniform(110, 430) * (0.85 + 0.15 * spread)
            x, y = center + math.cos(angle) * radius, center + math.sin(angle) * radius
            size = rng.choice((1, 1, 2, 3))
            draw.ellipse((x - size, y - size, x + size, y + size), fill=(220, 232, 255, rng.randint(30, 120)))

    @classmethod
    def _draw_memory_lamination(cls, draw: ImageDraw.ImageDraw, center: int, event: Mapping[str, Any], spread: float, phase: float) -> list[float]:
        radii: list[float] = []
        for layer_index, layer in enumerate(event.get("memory_layers") or ()):
            introduced = len(layer.get("introduced_motifs") or ())
            inherited = len(layer.get("inherited_motifs") or ())
            transformed = len(layer.get("transformed_motifs") or ())
            reactivated = len(layer.get("reactivated_motifs") or ())
            segment_count = max(3, introduced + inherited + transformed + reactivated)
            radius = 105 + layer_index * 34 + 75 * spread
            radii.append(radius)
            for segment in range(segment_count):
                start = math.degrees(phase) + segment * 360 / segment_count
                extent = max(9.0, 250 / segment_count)
                if segment < inherited: color = (108, 171, 255, 185)
                elif segment < inherited + reactivated: color = (255, 209, 102, 205)
                elif segment < inherited + reactivated + transformed: color = (201, 126, 255, 205)
                else: color = (110, 238, 203, 170)
                draw.arc((center - radius, center - radius, center + radius, center + radius), start=start, end=start + extent, fill=color, width=5)
        return radii

    @classmethod
    def _tone_positions(cls, center: int, sequence: Sequence[str], spread: float, phase: float, topology: str) -> dict[str, tuple[float, float]]:
        positions: dict[str, tuple[float, float]] = {}
        if not sequence:
            return positions
        count = len(sequence)
        radius = 205 + 155 * spread
        if topology == "axis" and count <= 2:
            for index, tone_id in enumerate(sequence):
                positions[tone_id] = (center + (index - (count - 1) / 2) * 170, center)
            return positions
        for index, tone_id in enumerate(sequence):
            frequency = ELARA_TONES[tone_id].frequency_hz
            log_position = math.log(frequency / 369.0) / math.log(2637.0 / 369.0)
            angle = phase - math.pi / 2 + TAU * (index / count + 0.18 * log_position)
            local_radius = radius * (0.72 + 0.34 * (index + 1) / count) if topology in ("paired_spiral", "sustained_vortex", "apex_lattice") else radius
            positions[tone_id] = (center + math.cos(angle) * local_radius, center + math.sin(angle) * local_radius)
        return positions

    @classmethod
    def _draw_harmonic_interactions(cls, draw: ImageDraw.ImageDraw, positions: Mapping[str, tuple[float, float]], tone_configuration: Mapping[str, Any]) -> None:
        for interaction in tone_configuration.get("interactions") or ():
            left, right = positions.get(str(interaction.get("tone_a"))), positions.get(str(interaction.get("tone_b")))
            if not left or not right:
                continue
            ratio = float(interaction.get("ratio") or 1.0)
            interval = float(interaction.get("interval_hz") or 0.0)
            closeness = 1.0 / (1.0 + abs(ratio - round(ratio)))
            alpha = int(32 + 92 * closeness)
            width = 1 + int(min(4.0, math.log1p(interval) / 2.5))
            draw.line((*left, *right), fill=(210, 220, 255, alpha), width=width)
            midpoint = ((left[0] + right[0]) / 2, (left[1] + right[1]) / 2)
            radius = max(1.5, min(5.0, math.log1p(interval) / 2))
            draw.ellipse((midpoint[0] - radius, midpoint[1] - radius, midpoint[0] + radius, midpoint[1] + radius), fill=(255, 238, 180, alpha + 25))

    @classmethod
    def _draw_tone_nodes(cls, draw: ImageDraw.ImageDraw, positions: Mapping[str, tuple[float, float]], sequence: Sequence[str], tone_configuration: Mapping[str, Any]) -> None:
        emergent = set(tone_configuration.get("emergent_tones") or ())
        for tone_id in sequence:
            position = positions.get(tone_id)
            if not position:
                continue
            radius = 10 + 6 * math.log(ELARA_TONES[tone_id].frequency_hz / 369.0 + 1.0)
            if tone_id in emergent:
                draw.ellipse((position[0] - radius - 10, position[1] - radius - 10, position[0] + radius + 10, position[1] + radius + 10), outline=(255, 245, 188, 150), width=4)
            draw.ellipse((position[0] - radius, position[1] - radius, position[0] + radius, position[1] + radius), fill=TONE_COLORS.get(tone_id, (230, 230, 255, 230)), outline=(255, 255, 255, 235), width=3)

    @classmethod
    def _draw_trajectories(cls, draw: ImageDraw.ImageDraw, center: int, event: Mapping[str, Any], spread: float, phase: float, tau: float) -> None:
        for index, trajectory in enumerate(event.get("trajectories") or ()):
            trajectory_phase = float(trajectory.get("phase") or 0.0)
            local_spread = float(trajectory.get("spread") or spread)
            points: list[tuple[float, float]] = []
            turns = 2.25 + min(4.0, tau / 4.0)
            for step in range(100):
                fraction = step / 99
                angle = trajectory_phase + turns * TAU * fraction
                radius = (26 + fraction * (115 + 175 * local_spread)) * (1.0 + 0.04 * math.sin(5 * angle + phase))
                points.append((center + math.cos(angle) * radius, center + math.sin(angle) * radius))
            draw.line(points, fill=(255, 225, 147, 190) if index == 0 else (124, 220, 244, 145), width=5 if index == 0 else 3, joint="curve")

    @classmethod
    def _draw_couplings(cls, draw: ImageDraw.ImageDraw, center: int, event: Mapping[str, Any], spread: float, phase: float) -> None:
        for index, coupling in enumerate(event.get("couplings") or ()):
            offset = float(coupling.get("phase_offset") or 0.0)
            angle = phase + offset
            radius = 145 + 170 * spread + index * 18
            target = (center + math.cos(angle) * radius, center + math.sin(angle) * radius)
            midpoint = (center + math.cos(angle - 0.5) * radius * 0.55, center + math.sin(angle - 0.5) * radius * 0.55)
            points = cls._quadratic_curve((center, center), midpoint, target, 48)
            shared = len(coupling.get("shared_motifs") or ())
            draw.line(points, fill=(115, 230, 219, 155 + min(80, shared * 8)), width=3 + min(5, shared))
            cls._draw_arrow(draw, points[-3], points[-1], (255, 245, 196, 220))

    @staticmethod
    def _quadratic_curve(start: tuple[float, float], control: tuple[float, float], end: tuple[float, float], steps: int) -> list[tuple[float, float]]:
        points = []
        for index in range(steps):
            t = index / (steps - 1); u = 1 - t
            points.append((u * u * start[0] + 2 * u * t * control[0] + t * t * end[0], u * u * start[1] + 2 * u * t * control[1] + t * t * end[1]))
        return points

    @staticmethod
    def _draw_arrow(draw: ImageDraw.ImageDraw, previous: tuple[float, float], end: tuple[float, float], color: tuple[int, int, int, int]) -> None:
        angle = math.atan2(end[1] - previous[1], end[0] - previous[0]); length = 14; wing = math.pi / 6
        left = (end[0] - length * math.cos(angle - wing), end[1] - length * math.sin(angle - wing))
        right = (end[0] - length * math.cos(angle + wing), end[1] - length * math.sin(angle + wing))
        draw.polygon((end, left, right), fill=color)

    @classmethod
    def _draw_boundaries(cls, draw: ImageDraw.ImageDraw, center: int, event: Mapping[str, Any], memory_radii: Sequence[float], phase: float) -> None:
        base_radius = max(memory_radii, default=185) + 42
        for index, boundary in enumerate(event.get("boundaries") or ()):
            radius = base_radius + index * 31
            operations = tuple(boundary.get("operations") or ())
            filtered = tuple(boundary.get("filtered") or ())
            delayed = boundary.get("delayed_seconds")
            start = math.degrees(phase) + index * 29
            extent = 310 - min(170, len(filtered) * 18)
            draw.arc((center - radius, center - radius, center + radius, center + radius), start=start, end=start + extent, fill=(255, 203, 120, 185) if delayed else (150, 198, 255, 155), width=4 + min(5, len(operations)))

    @classmethod
    def _draw_core(cls, draw: ImageDraw.ImageDraw, center: int, event: Mapping[str, Any], spread: float, gradient_mag: float, palette: str) -> None:
        standing = event.get("standing_modes") or ()
        status = str(standing[0].get("status") if standing else "forming")
        core_radius = 36 + 34 * spread + 12 * min(1.0, gradient_mag)
        draw.ellipse((center - core_radius - 14, center - core_radius - 14, center + core_radius + 14, center + core_radius + 14), outline=(194, 132, 255, 140), width=6)
        draw.ellipse((center - core_radius, center - core_radius, center + core_radius, center + core_radius), fill=(255, 242, 171, 220) if palette == "earth" else (225, 242, 255, 225), outline=(255, 255, 255, 250), width=5)
        if status == "standing_mode":
            draw.arc((center - core_radius - 24, center - core_radius - 24, center + core_radius + 24, center + core_radius + 24), start=15, end=330, fill=(118, 234, 213, 220), width=7)
        elif status == "emergent_node":
            for spoke in range(12):
                angle = spoke * TAU / 12
                draw.line((center + math.cos(angle) * (core_radius + 20), center + math.sin(angle) * (core_radius + 20), center + math.cos(angle) * (core_radius + 48), center + math.sin(angle) * (core_radius + 48)), fill=(255, 248, 190, 220), width=4)

    @classmethod
    def _draw_labels(cls, draw: ImageDraw.ImageDraw, artifact_id: str, event: Mapping[str, Any], active_tones: Sequence[str], topology: str) -> None:
        try:
            title_font = ImageFont.truetype("arial.ttf", 27); small_font = ImageFont.truetype("arial.ttf", 18)
        except OSError:
            title_font = ImageFont.load_default(); small_font = ImageFont.load_default()
        draw.text((28, 24), artifact_id, fill=(240, 235, 255, 255), font=title_font)
        event_time = event.get("event_time") or {}
        subtitle = f"{event.get('event_kind')} | {event.get('full_or_narrow')} | τ {float(event_time.get('cumulative_tau') or 0.0):.3f} | σ {float(event.get('perspective_spread') or 0.0):.3f}"
        draw.text((28, 61), subtitle, fill=(194, 224, 244, 235), font=small_font)
        tone_text = " · ".join(active_tones) if active_tones else "no active tone configuration"
        draw.text((28, cls.SIZE - 58), f"{topology} | {tone_text}", fill=(218, 237, 255, 240), font=small_font)


__all__ = ["HarmonyLatticeRenderer"]
