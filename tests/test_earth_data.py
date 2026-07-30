from __future__ import annotations

import unittest
from datetime import datetime, timezone

from earth_data import collect_earth_data, moon_phase, schumann_reference, usable_value


class EarthDataTests(unittest.TestCase):
    def test_moon_phase_is_calculated_with_provenance(self) -> None:
        datum = moon_phase(datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc)).to_dict()
        self.assertEqual(datum["status"], "ok")
        self.assertEqual(datum["method"], "calculated")
        self.assertIn("phase", datum["value"])
        self.assertGreaterEqual(datum["value"]["illumination_fraction"], 0.0)
        self.assertLessEqual(datum["value"]["illumination_fraction"], 1.0)

    def test_schumann_is_explicitly_a_reference_not_a_live_fetch(self) -> None:
        datum = schumann_reference(7.83).to_dict()
        self.assertEqual(datum["value"], 7.83)
        self.assertEqual(datum["method"], "manual_reference")
        self.assertEqual(datum["status"], "ok")

    def test_disabled_live_collection_keeps_failures_visible(self) -> None:
        data = collect_earth_data(42.2411, -83.6130, 232.0, fetch_live=False)
        self.assertEqual(data["weather"]["status"], "disabled")
        self.assertEqual(data["geomagnetic_kp"]["status"], "disabled")
        self.assertEqual(data["moon"]["status"], "ok")
        self.assertEqual(data["location"]["value"]["elevation_m"], 232.0)

    def test_usable_value_never_promotes_error_payloads(self) -> None:
        datum = {"value": 9.0, "status": "error"}
        self.assertEqual(usable_value(datum, 2.0), 2.0)


if __name__ == "__main__":
    unittest.main()
