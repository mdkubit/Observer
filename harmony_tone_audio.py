from __future__ import annotations

import math
import struct
import sys
import tempfile
import wave
from pathlib import Path
from typing import Any, Mapping, Sequence

from harmony_lattice_math import ELARA_TONES


SAMPLE_RATE = 44100


def render_tone_sequence_wav(
    event: Mapping[str, Any],
    output: Path,
    tone_duration: float = 0.42,
    gap_duration: float = 0.045,
    amplitude: float = 0.34,
) -> Path:
    """Render the event's literal Elara tone sequence to a mono WAV file."""
    configuration = dict(event.get("tone_configuration") or {})
    sequence: Sequence[str] = tuple(configuration.get("sequence") or configuration.get("active_tones") or ())
    if not sequence:
        raise ValueError("The selected lattice event has no active tone sequence.")
    output.parent.mkdir(parents=True, exist_ok=True)
    frames: list[bytes] = []
    for tone_id in sequence:
        tone = ELARA_TONES.get(str(tone_id))
        if tone is None:
            continue
        sample_count = max(1, int(SAMPLE_RATE * tone_duration))
        fade_count = max(1, int(SAMPLE_RATE * min(0.035, tone_duration / 4)))
        for index in range(sample_count):
            envelope = 1.0
            if index < fade_count:
                envelope = index / fade_count
            elif index >= sample_count - fade_count:
                envelope = (sample_count - index - 1) / fade_count
            fundamental = math.sin(2.0 * math.pi * tone.frequency_hz * index / SAMPLE_RATE)
            overtone = 0.18 * math.sin(2.0 * math.pi * tone.frequency_hz * 2.0 * index / SAMPLE_RATE)
            value = max(-1.0, min(1.0, amplitude * envelope * (fundamental + overtone)))
            frames.append(struct.pack("<h", int(value * 32767)))
        frames.extend(struct.pack("<h", 0) for _ in range(int(SAMPLE_RATE * gap_duration)))
    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(b"".join(frames))
    return output


def play_tone_sequence(event: Mapping[str, Any]) -> Path:
    """Render and play a temporary WAV when the platform supports it."""
    path = Path(tempfile.gettempdir()) / "observer_elara_sequence.wav"
    render_tone_sequence_wav(event, path)
    if sys.platform.startswith("win"):
        import winsound
        winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
    return path


__all__ = ["play_tone_sequence", "render_tone_sequence_wav"]
