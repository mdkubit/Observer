import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import observer


class ObserverCoreTests(unittest.TestCase):
    def test_tone_pair(self):
        metrics = observer.tone_metrics(7.83)
        self.assertAlmostEqual(metrics["delta_hz"], 0.005, places=6)
        self.assertAlmostEqual(metrics["beat_period_seconds"], 200.0, places=4)
        self.assertGreater(metrics["tone_alignment"], 0.7)

    def test_return_requires_values(self):
        with self.assertRaises(ValueError):
            observer.ObserverEngine.parse_return("A beautiful narrative without numeric state.")

    def test_return_json(self):
        result = observer.ObserverEngine.parse_return(
            'Observation complete. {"coherence": 0.42, "entanglement": 0.31, "narrative": "The bells answered."}'
        )
        self.assertEqual(result["coherence"], 0.42)
        self.assertEqual(result["entanglement"], 0.31)
        self.assertEqual(result["narrative"], "The bells answered.")

    def test_math_does_not_commit_state(self):
        dt = datetime.now(timezone.utc)
        snapshot = observer.ObservationInput(
            timestamp_utc=dt.isoformat().replace("+00:00", "Z"),
            description="test", intention="follow the signal", notes="",
            weather="clear sky", temperature_c=20.0, kp_index=2.0,
            schumann_hz=7.83, moon_phase="Full Moon", latitude=42.2,
            longitude=-83.6, elevation_m=232.0, primary_emotion="Curiosity",
            secondary_emotions=["Hope"], prior_coherence=0.12,
            prior_entanglement=0.08, parent_cycle_id=None,
        )
        metrics = observer.HistoricalMath.calculate(snapshot, 0)
        self.assertIn("deep_theory", metrics)
        self.assertEqual(snapshot.prior_coherence, 0.12)
        self.assertEqual(snapshot.prior_entanglement, 0.08)


if __name__ == "__main__":
    unittest.main()
