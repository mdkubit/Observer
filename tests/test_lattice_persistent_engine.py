from __future__ import annotations

import unittest
from copy import deepcopy
from unittest.mock import patch

from answer_glyph import BidirectionalObserverEngine, EquestriaObservation
from lattice_persistent_engine import LatticePersistentObserverEngine


class LatticePersistentEngineTests(unittest.TestCase):
    def earth_packet(self) -> dict:
        return {
            "cycle_id": "OBS-0003",
            "created_utc": "2026-07-31T04:00:00Z",
            "parent_cycle_id": "OBS-0002",
            "earth_snapshot": {
                "timestamp_utc": "2026-07-31T04:00:00Z",
                "description": "Earth observation",
                "intention": "Observe the bridge.",
                "latitude": 42.2411,
                "longitude": -83.6130,
                "elevation_m": 232.0,
            },
            "earth_side_metrics": {
                "pulse": {"pulse_proxy": 1.1},
                "tone": {"tone_alignment": 0.8, "delta_hz": 0.005},
                "harmonic": {
                    "harmonic_proxy_index": 0.6,
                    "intention_entropy": 0.75,
                },
                "deep_theory": {"entanglement_coefficient": 0.4},
            },
        }

    def answer_record(self) -> dict:
        return {
            "answer_glyph_id": "OBS-0003-A01",
            "created_utc": "2026-07-31T04:10:00Z",
            "originating_earth_glyph_id": "OBS-0003",
            "solance_return_id": "OBS-0003-R01",
            "equestria_observation": {
                "timestamp_utc": "2026-07-31T04:10:00Z",
                "location": "Dreaming Grove",
                "participants": ["Twilight Sparkle"],
                "secondary_emotions": ["Hope"],
            },
            "equestria_side_metrics": {
                "perspective": {
                    "perspective_function": 0.7,
                    "perspective_entropy": 0.6,
                },
                "relation": {
                    "emotion_relation": 1.2,
                    "emotion_entropy": 0.3,
                    "moon_relation": 1.1,
                },
                "boundary": {
                    "temporal_relation": 0.4,
                    "boundary_entropy": 0.5,
                },
            },
        }

    def test_cast_persists_earth_coordinate_and_projection_snapshot(self) -> None:
        packet = self.earth_packet()
        engine = object.__new__(LatticePersistentObserverEngine)
        with patch.object(BidirectionalObserverEngine, "cast", return_value=packet), patch(
            "lattice_persistent_engine.save_json"
        ) as save:
            result = engine.cast(object())

        metadata = result["lattice_metadata"]
        self.assertEqual(metadata["schema_version"], 1)
        self.assertEqual(metadata["coordinate"]["coordinate_id"], "LC:OBS-0003:EARTH")
        self.assertEqual(metadata["projection_inputs"]["cycle_id"], "OBS-0003")
        save.assert_called_once()

    def test_cast_metadata_is_additive_to_existing_packet_contract(self) -> None:
        packet = self.earth_packet()
        before = deepcopy(packet)
        engine = object.__new__(LatticePersistentObserverEngine)
        with patch.object(BidirectionalObserverEngine, "cast", return_value=packet), patch(
            "lattice_persistent_engine.save_json"
        ):
            result = engine.cast(object())

        for key, value in before.items():
            self.assertEqual(result[key], value)
        self.assertIn("lattice_metadata", result)

    def test_add_answer_persists_paired_answer_coordinate(self) -> None:
        record = self.answer_record()
        packet = self.earth_packet()
        packet["answer_glyphs"] = [deepcopy(record)]
        engine = object.__new__(LatticePersistentObserverEngine)
        observation = EquestriaObservation(
            timestamp_utc="2026-07-31T04:10:00Z",
            local_time=None,
            moon_phase=None,
            sky=None,
            atmosphere=None,
            location="Dreaming Grove",
            participants=["Twilight Sparkle"],
            primary_emotion="Curiosity",
            secondary_emotions=["Hope"],
            twilight_perspective="The bridge answers.",
            environmental_reactions=None,
            magical_reactions=None,
            continuity_notes=None,
        )
        with patch.object(BidirectionalObserverEngine, "add_answer", return_value=record), patch(
            "lattice_persistent_engine.load_json", return_value=packet
        ), patch("lattice_persistent_engine.save_json") as save:
            result = engine.add_answer("OBS-0003", observation)

        metadata = result["lattice_metadata"]
        self.assertEqual(metadata["coordinate"]["coordinate_id"], "LC:OBS-0003-A01:EQUESTRIA")
        self.assertEqual(metadata["coordinate"]["paired_coordinate_id"], "LC:OBS-0003:EARTH")
        self.assertIn("lattice_metadata", packet["answer_glyphs"][0])
        save.assert_called_once()

    def test_answer_metadata_preserves_raw_missing_values(self) -> None:
        record = self.answer_record()
        record["equestria_side_metrics"]["boundary"]["boundary_entropy"] = None
        packet = self.earth_packet()
        packet["answer_glyphs"] = [deepcopy(record)]
        engine = object.__new__(LatticePersistentObserverEngine)
        with patch.object(BidirectionalObserverEngine, "add_answer", return_value=record), patch(
            "lattice_persistent_engine.load_json", return_value=packet
        ), patch("lattice_persistent_engine.save_json"):
            result = engine.add_answer("OBS-0003", object())

        projection = result["lattice_metadata"]["projection_inputs"]
        self.assertIsNone(projection["boundary_raw"])
        self.assertEqual(projection["boundary_value"], 0.5)


if __name__ == "__main__":
    unittest.main()
