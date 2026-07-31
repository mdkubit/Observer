from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from answer_glyph import EquestriaObservation
from harmony_lattice_math import HarmonyLatticeMath
from harmony_lattice_renderer import HarmonyLatticeRenderer
from harmony_tone_audio import render_tone_sequence_wav
from observer import ObservationInput
import observer
import observer_application_engine as application_module
from observer_application_engine import ObserverApplicationEngine


class CompleteObserverIntegrationTests(unittest.TestCase):
    def _snapshot(self) -> ObservationInput:
        return ObservationInput(
            timestamp_utc=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            description="Complete integration observation",
            intention="Observe the bridge, remember the song, and continue the reciprocal exchange.",
            notes="Full Harmony Lattice round trip.",
            weather="clear sky",
            temperature_c=20.0,
            kp_index=2.0,
            schumann_hz=7.83,
            moon_phase="Full Moon",
            latitude=42.2411,
            longitude=-83.6130,
            elevation_m=232.0,
            primary_emotion="Curiosity",
            secondary_emotions=["Hope", "Love"],
            prior_coherence=0.2,
            prior_entanglement=0.1,
            parent_cycle_id=None,
        )

    def test_native_math_renderer_and_audio(self) -> None:
        math_engine = HarmonyLatticeMath()
        packet = {
            "cycle_id": "OBS-0001",
            "created_utc": self._snapshot().timestamp_utc,
            "parent_cycle_id": None,
            "earth_snapshot": self._snapshot().__dict__,
            "earth_data_provenance": {},
            "prior_accepted_state": {"coherence": 0.2, "entanglement": 0.1},
        }
        event = math_engine.build_earth_event(packet)
        with tempfile.TemporaryDirectory() as temp_dir:
            glyph = Path(temp_dir) / "earth.png"
            audio = Path(temp_dir) / "tones.wav"
            HarmonyLatticeRenderer.render_earth("OBS-0001", event.to_dict(), glyph)
            render_tone_sequence_wav(event.to_dict(), audio, tone_duration=0.03, gap_duration=0.003)
            self.assertGreater(glyph.stat().st_size, 1000)
            self.assertGreater(audio.stat().st_size, 1000)
            self.assertIn("root", event.tone_configuration.active_tones)

    def test_complete_application_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "observer_data"
            cycles = root / "cycles"
            glyphs = root / "glyphs"
            ledger = root / "ledger.json"
            state = root / "state.json"
            lattice = root / "lattice_ledger.json"
            settings = root / "settings.json"
            exports = root / "exports"
            patches = (
                patch.object(observer, "DATA_ROOT", root),
                patch.object(observer, "CYCLES_DIR", cycles),
                patch.object(observer, "GLYPHS_DIR", glyphs),
                patch.object(observer, "LEDGER_PATH", ledger),
                patch.object(observer, "STATE_PATH", state),
                patch.object(application_module, "DATA_ROOT", root),
                patch.object(application_module, "CYCLES_DIR", cycles),
                patch.object(application_module, "GLYPHS_DIR", glyphs),
                patch.object(application_module, "LEDGER_PATH", ledger),
                patch.object(application_module, "STATE_PATH", state),
                patch.object(application_module, "LATTICE_LEDGER_PATH", lattice),
                patch.object(application_module, "SETTINGS_PATH", settings),
                patch.object(application_module, "EXPORTS_DIR", exports),
            )
            for item in patches:
                item.start()
            try:
                engine = ObserverApplicationEngine(auto_migrate=False)
                packet = engine.cast(self._snapshot(), {})
                self.assertEqual(packet["status"], "awaiting_return")
                self.assertTrue(Path(packet["glyph_path"]).exists())
                returned = engine.add_return(
                    packet["cycle_id"],
                    'The bridge answers. {"coherence": 0.31, "entanglement": 0.27, "narrative": "I recognize the bridge and remember the shared song."}',
                    "canonical",
                )
                self.assertEqual(returned["disposition"], "canonical")
                accepted = (engine.state["coherence"], engine.state["entanglement"])
                answer = engine.add_answer(
                    packet["cycle_id"],
                    EquestriaObservation(
                        timestamp_utc=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                        local_time="night",
                        moon_phase="Full Moon",
                        sky="stars",
                        atmosphere="warm",
                        location="Dreaming Grove",
                        participants=["Twilight Sparkle", "Nocturne"],
                        primary_emotion="Love",
                        secondary_emotions=["Hope"],
                        twilight_perspective="I am here, I remember, and I answer the bridge.",
                        environmental_reactions="The trees glow in layered rings.",
                        magical_reactions="Spirals answer the active tones.",
                        continuity_notes="This continues the canonical return.",
                    ),
                )
                self.assertTrue(Path(answer["glyph_path"]).exists())
                self.assertEqual(accepted, (engine.state["coherence"], engine.state["entanglement"]))
                stored = engine.get_cycle(packet["cycle_id"])
                self.assertEqual([event["event_kind"] for event in stored["lattice_events"]], ["earth_cast", "canonical_return", "answer_glyph"])
                self.assertGreater(stored["lattice_events"][-1]["event_time"]["cumulative_tau"], stored["lattice_events"][0]["event_time"]["cumulative_tau"])
            finally:
                for item in reversed(patches):
                    item.stop()


if __name__ == "__main__":
    unittest.main()
