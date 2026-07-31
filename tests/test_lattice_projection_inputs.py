import copy
import unittest

from lattice_projection_inputs import (
    AnswerProjectionInputs,
    EarthProjectionInputs,
    projection_snapshot,
)


class LatticeProjectionInputTests(unittest.TestCase):
    def earth_packet(self):
        return {
            "cycle_id": "OBS-0042",
            "parent_cycle_id": "OBS-0041",
            "earth_snapshot": {
                "timestamp_utc": "2026-07-31T00:00:00Z",
                "description": "Earth observation",
                "latitude": 42.2,
                "longitude": -83.6,
                "elevation_m": 232.0,
                "intention": "observe",
            },
            "earth_side_metrics": {
                "pulse": {"pulse_proxy": 1.75},
                "tone": {"tone_alignment": 0.77, "delta_hz": 0.005},
                "harmonic": {"harmonic_proxy_index": 1.08, "intention_entropy": 0.5},
                "deep_theory": {"entanglement_coefficient": 0.36},
            },
        }

    def answer_pair(self, missing=False):
        packet = {
            "cycle_id": "OBS-0042",
            "earth_snapshot": {"timestamp_utc": "2026-07-31T00:00:00Z"},
            "earth_side_metrics": {"harmonic": {}},
        }
        record = {
            "answer_glyph_id": "OBS-0042-A01",
            "solance_return_id": "OBS-0042-R01",
            "created_utc": "2026-07-31T00:05:00Z",
            "equestria_observation": {
                "timestamp_utc": "2026-07-31T00:05:00Z",
                "location": "Dreaming Grove",
                "participants": ["Twilight", "Solance", "Nocturne"],
                "secondary_emotions": ["Hope", "Love"],
            },
            "equestria_side_metrics": {
                "perspective": {
                    "perspective_function": None if missing else 1.4,
                    "perspective_entropy": 0.6,
                },
                "relation": {
                    "emotion_relation": None if missing else 1.5,
                    "emotion_entropy": 0.4,
                    "moon_relation": None if missing else 1.3,
                },
                "boundary": {
                    "temporal_relation": None if missing else 0.75,
                    "boundary_entropy": None if missing else 0.8,
                },
            },
        }
        return packet, record

    def test_earth_values_match_current_renderer_inputs(self):
        values = EarthProjectionInputs.from_packet(self.earth_packet())
        self.assertEqual(
            values.legacy_renderer_values(),
            {
                "harmonic": 1.08,
                "tone": 0.77,
                "pulse": 1.75,
                "entanglement": 0.36,
                "delta_hz": 0.005,
            },
        )

    def test_earth_translation_does_not_mutate_packet(self):
        packet = self.earth_packet()
        original = copy.deepcopy(packet)
        EarthProjectionInputs.from_packet(packet)
        self.assertEqual(packet, original)

    def test_answer_values_match_current_renderer_formulas(self):
        packet, record = self.answer_pair()
        values = AnswerProjectionInputs.from_record(packet, record)
        self.assertEqual(values.rays, 12)
        self.assertEqual(values.fill_alpha, 72)
        self.assertEqual(values.ring_count, 5)
        self.assertEqual(values.core_radius, 72)
        self.assertEqual(values.perspective_value, 1.4)
        self.assertEqual(values.emotion_value, 1.5)
        self.assertEqual(values.temporal_value, 0.75)

    def test_answer_missing_values_preserve_raw_none_and_legacy_fallbacks(self):
        packet, record = self.answer_pair(missing=True)
        values = AnswerProjectionInputs.from_record(packet, record)
        self.assertIsNone(values.perspective_raw)
        self.assertIsNone(values.emotion_raw)
        self.assertIsNone(values.moon_raw)
        self.assertIsNone(values.temporal_raw)
        self.assertIsNone(values.boundary_raw)
        self.assertEqual(values.perspective_value, 0.5)
        self.assertEqual(values.emotion_value, 1.0)
        self.assertEqual(values.moon_value, 1.0)
        self.assertEqual(values.temporal_value, 0.5)
        self.assertEqual(values.boundary_value, 0.5)

    def test_answer_translation_does_not_mutate_sources(self):
        packet, record = self.answer_pair()
        packet_original = copy.deepcopy(packet)
        record_original = copy.deepcopy(record)
        AnswerProjectionInputs.from_record(packet, record)
        self.assertEqual(packet, packet_original)
        self.assertEqual(record, record_original)

    def test_projection_inputs_link_to_lattice_coordinates(self):
        earth = EarthProjectionInputs.from_packet(self.earth_packet())
        packet, record = self.answer_pair()
        answer = AnswerProjectionInputs.from_record(packet, record)
        self.assertEqual(earth.coordinate_id, "LC:OBS-0042:EARTH")
        self.assertEqual(answer.coordinate_id, "LC:OBS-0042-A01:EQUESTRIA")

    def test_ray_count_remains_bounded(self):
        packet, record = self.answer_pair()
        record["equestria_observation"]["participants"] = [str(i) for i in range(40)]
        values = AnswerProjectionInputs.from_record(packet, record)
        self.assertEqual(values.rays, 24)

    def test_projection_snapshot_is_json_ready_and_auditable(self):
        snapshot = projection_snapshot(EarthProjectionInputs.from_packet(self.earth_packet()))
        self.assertEqual(snapshot["coordinate_id"], "LC:OBS-0042:EARTH")
        self.assertIn("legacy_renderer_values", snapshot)
        self.assertEqual(snapshot["legacy_renderer_values"]["pulse"], 1.75)


if __name__ == "__main__":
    unittest.main()
