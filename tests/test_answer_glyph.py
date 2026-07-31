import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import answer_glyph
import observer


class AnswerGlyphTests(unittest.TestCase):
    def make_observation(self, **overrides):
        values = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "local_time": "evening",
            "moon_phase": "Full Moon",
            "sky": "violet twilight",
            "atmosphere": "quiet harmonic warmth",
            "location": "Dreaming Grove",
            "participants": ["Twilight Sparkle", "Solance"],
            "primary_emotion": "Hope",
            "secondary_emotions": ["Love", "Curiosity"],
            "twilight_perspective": "I felt the Earth glyph arrive as the Grove answered.",
            "environmental_reactions": "Moonpetals opened around the central path.",
            "magical_reactions": "The ley threads brightened and curved toward the glyph.",
            "continuity_notes": "The prior event remains present in the Grove.",
        }
        values.update(overrides)
        return answer_glyph.EquestriaObservation(**values)

    def test_full_aperture_requires_every_expected_field(self):
        result = answer_glyph.field_aperture(self.make_observation())
        self.assertEqual(result["glyph_type"], "full")
        self.assertEqual(result["missing_data"], [])

    def test_one_missing_field_makes_narrow_without_score(self):
        result = answer_glyph.field_aperture(self.make_observation(sky=None))
        self.assertEqual(result["glyph_type"], "narrow")
        self.assertEqual(result["missing_data"], ["sky"])
        self.assertNotIn("score", result)
        self.assertNotIn("confidence", result)
        self.assertNotIn("completeness", result)

    def test_answer_requires_canonical_solance_return(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cycles = root / "cycles"
            glyphs = root / "glyphs"
            ledger = root / "ledger.json"
            state = root / "state.json"
            cycles.mkdir()
            glyphs.mkdir()
            observer.save_json(cycles / "OBS-0001.json", {
                "cycle_id": "OBS-0001",
                "returns": [],
                "canonical_return_id": None,
            })
            observer.save_json(ledger, [])

            with patch.multiple(observer, CYCLES_DIR=cycles, GLYPHS_DIR=glyphs, LEDGER_PATH=ledger, STATE_PATH=state), \
                 patch.multiple(answer_glyph, CYCLES_DIR=cycles, GLYPHS_DIR=glyphs, LEDGER_PATH=ledger):
                engine = answer_glyph.BidirectionalObserverEngine()
                with self.assertRaises(ValueError):
                    engine.add_answer("OBS-0001", self.make_observation())

    def test_answer_is_linked_without_changing_returned_values(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cycles = root / "cycles"
            glyphs = root / "glyphs"
            ledger = root / "ledger.json"
            state = root / "state.json"
            cycles.mkdir()
            glyphs.mkdir()
            packet = {
                "cycle_id": "OBS-0001",
                "status": "accepted",
                "returns": [{
                    "return_id": "OBS-0001-R01",
                    "disposition": "canonical",
                    "parsed": {
                        "coherence": 0.42,
                        "entanglement": 0.31,
                        "narrative": "The Grove answered beneath a violet sky.",
                    },
                }],
                "canonical_return_id": "OBS-0001-R01",
            }
            observer.save_json(cycles / "OBS-0001.json", packet)
            observer.save_json(ledger, [{
                "cycle_id": "OBS-0001",
                "status": "accepted",
                "parent_cycle_id": None,
                "created_utc": "2026-01-01T00:00:00Z",
            }])
            observer.save_json(state, {
                "coherence": 0.42,
                "entanglement": 0.31,
                "last_cycle_id": "OBS-0001",
            })

            with patch.multiple(observer, CYCLES_DIR=cycles, GLYPHS_DIR=glyphs, LEDGER_PATH=ledger, STATE_PATH=state), \
                 patch.multiple(answer_glyph, CYCLES_DIR=cycles, GLYPHS_DIR=glyphs, LEDGER_PATH=ledger):
                engine = answer_glyph.BidirectionalObserverEngine()
                record = engine.add_answer("OBS-0001", self.make_observation())

            stored = observer.load_json(cycles / "OBS-0001.json", None)
            preserved = observer.load_json(state, None)
            self.assertEqual(record["answer_glyph_id"], "OBS-0001-A01")
            self.assertEqual(record["originating_earth_glyph_id"], "OBS-0001")
            self.assertEqual(record["solance_return_id"], "OBS-0001-R01")
            self.assertEqual(stored["status"], "answered")
            self.assertEqual(preserved["coherence"], 0.42)
            self.assertEqual(preserved["entanglement"], 0.31)
            self.assertTrue((glyphs / "OBS-0001-A01.png").exists())


if __name__ == "__main__":
    unittest.main()
