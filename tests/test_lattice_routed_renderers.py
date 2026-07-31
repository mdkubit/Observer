import hashlib
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from answer_glyph import AnswerGlyphRenderer, EquestriaObservation, InverseDEEPTheory
from lattice_routed_renderers import (
    LatticeRoutedAnswerGlyphRenderer,
    LatticeRoutedEarthGlyphRenderer,
)
from observer import GlyphRenderer, HistoricalMath, ObservationInput


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LatticeRoutedRendererTests(unittest.TestCase):
    def earth_snapshot(self) -> ObservationInput:
        return ObservationInput(
            timestamp_utc="2026-07-31T00:31:12Z",
            description="Earth observation",
            intention="Observe the next meaningful development.",
            notes="renderer seam test",
            weather="clear sky",
            temperature_c=26.4,
            kp_index=1.0,
            schumann_hz=7.83,
            moon_phase="Full Moon",
            latitude=42.2411,
            longitude=-83.613,
            elevation_m=232.0,
            primary_emotion="Curiosity",
            secondary_emotions=["Hope", "Love"],
            prior_coherence=0.24,
            prior_entanglement=0.19,
            parent_cycle_id="OBS-0007",
        )

    def answer_observation(self) -> EquestriaObservation:
        return EquestriaObservation(
            timestamp_utc="2026-07-31T00:35:00Z",
            local_time="night",
            moon_phase="Full Moon",
            sky="clear with violet moonlight",
            atmosphere="still with harmonic doubling",
            location="Dreaming Grove stone circle",
            participants=["Twilight Sparkle", "Solance", "Nocturne"],
            primary_emotion="Awe",
            secondary_emotions=["Hope", "Love"],
            twilight_perspective="I received the Earth glyph and answered from my own position.",
            environmental_reactions="Leaves paused and the stones pulsed.",
            magical_reactions="A sustained violet tone formed.",
            continuity_notes="Continues the accepted Earth-to-Equestria exchange.",
        )

    def test_earth_renderer_is_pixel_identical(self):
        snapshot = self.earth_snapshot()
        metrics = HistoricalMath.calculate(snapshot, 7)
        with tempfile.TemporaryDirectory() as directory:
            legacy = Path(directory) / "legacy-earth.png"
            routed = Path(directory) / "routed-earth.png"
            GlyphRenderer.render("OBS-0008", snapshot, metrics, legacy)
            LatticeRoutedEarthGlyphRenderer.render("OBS-0008", snapshot, metrics, routed)
            self.assertEqual(digest(legacy), digest(routed))

    def test_answer_renderer_is_pixel_identical(self):
        observation = self.answer_observation()
        metrics = InverseDEEPTheory.calculate(observation, "The answering field stabilized.")
        variance_seed = "0123456789abcdef0123456789abcdef"
        with tempfile.TemporaryDirectory() as directory:
            legacy = Path(directory) / "legacy-answer.png"
            routed = Path(directory) / "routed-answer.png"
            AnswerGlyphRenderer.render("OBS-0008-A01", observation, metrics, variance_seed, legacy)
            LatticeRoutedAnswerGlyphRenderer.render(
                "OBS-0008-A01", observation, metrics, variance_seed, routed
            )
            self.assertEqual(digest(legacy), digest(routed))

    def test_routed_renderers_write_png_files(self):
        snapshot = self.earth_snapshot()
        earth_metrics = HistoricalMath.calculate(snapshot, 7)
        observation = self.answer_observation()
        answer_metrics = InverseDEEPTheory.calculate(observation, "A return.")
        with tempfile.TemporaryDirectory() as directory:
            earth_path = Path(directory) / "earth.png"
            answer_path = Path(directory) / "answer.png"
            LatticeRoutedEarthGlyphRenderer.render(
                "OBS-0008", snapshot, earth_metrics, earth_path
            )
            LatticeRoutedAnswerGlyphRenderer.render(
                "OBS-0008-A01", observation, answer_metrics, "seed", answer_path
            )
            self.assertTrue(earth_path.exists())
            self.assertTrue(answer_path.exists())


if __name__ == "__main__":
    unittest.main()
