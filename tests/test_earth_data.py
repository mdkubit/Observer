from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from earth_data import (
    _parse_noaa_1m,
    _parse_noaa_3h,
    collect_earth_data,
    geomagnetic_kp,
    moon_phase,
    schumann_reference,
    usable_value,
)


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

    def test_parse_official_three_hour_header_rows_uses_latest_timestamp(self) -> None:
        payload = [
            ["time_tag", "Kp", "a_running", "station_count"],
            ["2026-07-30 15:00:00.000", "1.67", "6", "8"],
            ["2026-07-30 18:00:00.000", "1.33", "5", "8"],
        ]
        value, timestamp, metadata = _parse_noaa_3h(payload)
        self.assertEqual(value, 1.33)
        self.assertTrue(timestamp.startswith("2026-07-30T18:00:00"))
        self.assertEqual(metadata["record_shape"], "header_rows")
        self.assertEqual(metadata["station_count"], "8")

    def test_parse_official_three_hour_object_records_uses_latest_timestamp(self) -> None:
        payload = [
            {"time_tag": "2026-07-30T15:00:00", "Kp": "1.67", "a_running": "6", "station_count": "8"},
            {"time_tag": "2026-07-30T18:00:00", "Kp": "1.33", "a_running": "5", "station_count": "8"},
        ]
        value, timestamp, metadata = _parse_noaa_3h(payload)
        self.assertEqual(value, 1.33)
        self.assertEqual(timestamp, "2026-07-30T18:00:00")
        self.assertEqual(metadata["record_shape"], "objects")
        self.assertEqual(metadata["a_running"], "5")

    def test_parse_one_minute_product_prefers_estimated_kp(self) -> None:
        payload = [
            {"time_tag": "2026-07-30T21:47:00", "kp_index": 0.0, "estimated_kp": 1.67},
            {"time_tag": "2026-07-30T21:48:00", "kp_index": 0.0, "estimated_kp": 2.0},
        ]
        value, timestamp, metadata = _parse_noaa_1m(payload)
        self.assertEqual(value, 2.0)
        self.assertEqual(timestamp, "2026-07-30T21:48:00")
        self.assertEqual(metadata["field_used"], "estimated_kp")

    @patch("earth_data._get_json")
    def test_geomagnetic_kp_prefers_official_object_product(self, get_json) -> None:
        get_json.return_value = [
            {"time_tag": "2026-07-30T18:00:00", "Kp": "1.33", "a_running": "5", "station_count": "8"}
        ]
        datum = geomagnetic_kp().to_dict()
        self.assertEqual(datum["status"], "ok")
        self.assertEqual(datum["method"], "fetched")
        self.assertEqual(datum["value"], 1.33)
        self.assertEqual(datum["metadata"]["record_shape"], "objects")

    @patch("earth_data._get_json")
    def test_geomagnetic_kp_falls_back_to_one_minute_product(self, get_json) -> None:
        get_json.side_effect = [
            RuntimeError("3-hour unavailable"),
            [{"time_tag": "2026-07-30T21:48:00", "kp_index": 0.0, "estimated_kp": 1.67}],
        ]
        datum = geomagnetic_kp().to_dict()
        self.assertEqual(datum["status"], "ok")
        self.assertEqual(datum["method"], "fetched_fallback")
        self.assertEqual(datum["value"], 1.67)
        self.assertIn("3-hour product", datum["error"])


if __name__ == "__main__":
    unittest.main()
