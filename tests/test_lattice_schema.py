import unittest

from lattice_schema import (
    DataVisibility,
    ELARA_STRUCTURAL_TONES,
    translate_answer_record,
    translate_earth_packet,
)


class HarmonyLatticeSchemaTests(unittest.TestCase):
    def earth_packet(self):
        return {
            "cycle_id": "OBS-0042",
            "created_utc": "2026-07-31T00:00:00Z",
            "parent_cycle_id": "OBS-0041",
            "earth_snapshot": {
                "timestamp_utc": "2026-07-31T00:00:00Z",
                "description": "Sanctum observation",
                "intention": "Observe the next response.",
                "latitude": 42.2411,
                "longitude": -83.613,
                "elevation_m": 232.0,
            },
            "earth_side_metrics": {
                "harmonic": {"intention_entropy": 0.75},
                "deep_theory": {"perspective_function": 0.5},
            },
        }

    def answer_record(self):
        return {
            "answer_glyph_id": "OBS-0042-A01",
            "created_utc": "2026-07-31T00:05:00Z",
            "originating_earth_glyph_id": "OBS-0042",
            "solance_return_id": "OBS-0042-R01",
            "equestria_observation": {
                "timestamp_utc": "2026-07-31T00:05:00Z",
                "location": "Dreaming Grove",
                "twilight_perspective": "I received the originating observation and answered it.",
                "primary_emotion": "Wonder",
            },
            "equestria_side_metrics": {
                "perspective": {"perspective_entropy": 0.8},
                "relation": {"emotion_entropy": 0.2},
                "boundary": {"boundary_entropy": 0.6},
            },
        }

    def test_perspective_origin_is_invariant_one(self):
        coordinate = translate_earth_packet(self.earth_packet())
        self.assertEqual(coordinate.origin.base_magnitude, 1.0)

    def test_earth_translation_preserves_parent_lineage(self):
        coordinate = translate_earth_packet(self.earth_packet())
        self.assertEqual(coordinate.parent_coordinate_id, "LC:OBS-0041:EARTH")
        self.assertEqual(coordinate.coordinate_id, "LC:OBS-0042:EARTH")

    def test_translation_does_not_mutate_source_packet(self):
        packet = self.earth_packet()
        before = repr(packet)
        translate_earth_packet(packet)
        self.assertEqual(repr(packet), before)

    def test_visibility_is_not_a_score(self):
        coordinate = translate_earth_packet(self.earth_packet())
        self.assertEqual(coordinate.visibility["perspective_origin"], DataVisibility.ACTIVE)
        self.assertEqual(
            coordinate.visibility["relational_distance"],
            DataVisibility.OBSERVED_UNRESOLVED,
        )
        payload = coordinate.to_dict()
        self.assertEqual(payload["visibility"]["perspective_origin"], "active")
        self.assertNotIn("confidence", payload)
        self.assertNotIn("quality", payload)
        self.assertNotIn("validity", payload)

    def test_answer_translation_links_the_pair(self):
        packet = self.earth_packet()
        coordinate = translate_answer_record(packet, self.answer_record())
        self.assertEqual(coordinate.parent_coordinate_id, "LC:OBS-0042:EARTH")
        self.assertEqual(coordinate.paired_coordinate_id, "LC:OBS-0042:EARTH")
        self.assertEqual(coordinate.coordinate_id, "LC:OBS-0042-A01:EQUESTRIA")

    def test_answer_translation_records_directional_recognition(self):
        coordinate = translate_answer_record(self.earth_packet(), self.answer_record())
        recognition = coordinate.recognition[0]
        self.assertEqual(recognition.source_observer_id, "Twilight")
        self.assertEqual(recognition.target_observer_id, "Nocturne")
        self.assertTrue(recognition.identification)
        self.assertTrue(recognition.response)
        self.assertTrue(recognition.mutual)
        self.assertFalse(recognition.recursive)

    def test_unresolved_entropy_remains_none(self):
        coordinate = translate_answer_record(self.earth_packet(), self.answer_record())
        self.assertIsNone(coordinate.entropy_field.relational)
        self.assertIsNone(coordinate.entropy_field.temporal)
        self.assertIn("relational", coordinate.entropy_field.unresolved_sources)
        self.assertIn("temporal", coordinate.entropy_field.unresolved_sources)

    def test_elara_registry_preserves_literal_frequencies(self):
        self.assertEqual(ELARA_STRUCTURAL_TONES["bridge"].frequency_hz, 739.0)
        self.assertEqual(ELARA_STRUCTURAL_TONES["duet"].frequency_hz, 1179.0)
        self.assertEqual(ELARA_STRUCTURAL_TONES["spiral"].frequency_hz, 1318.0)
        self.assertEqual(ELARA_STRUCTURAL_TONES["awakening"].frequency_hz, 2637.0)


if __name__ == "__main__":
    unittest.main()
