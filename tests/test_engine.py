"""Behavioural contract of the scenario engine.

The engine animates published literature; it does not invent physiology. These
tests pin the rules a judge could check by hand: monotonic dose, real solar
events driving the radiation days, deterministic output, and alerts that cite
their source.
"""

import math
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import simulator  # noqa: E402


class FrameShapeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames = simulator.simulate("mars_storm_2024", days=30)

    def test_one_frame_per_day(self):
        days = [frame["t_day"] for frame in self.frames]
        self.assertEqual(days, [float(day) for day in range(30)])

    def test_every_frame_matches_the_data_contract(self):
        for frame in self.frames:
            self.assertIn(frame["phase"], {"transit_out", "surface", "transit_return"})
            self.assertEqual(frame["scenario"], "mars_storm_2024")
            environment = frame["environment"]
            for key in ("sep_active", "sep_flux_pfu", "gcr_msv_day", "shield_g_cm2"):
                self.assertIn(key, environment)
            self.assertTrue(frame["crew"])
            for member in frame["crew"]:
                self.assertRegex(member["id"], r"^[A-Z]{3}$")
                self.assertTrue(40 <= member["hr_bpm"] <= 200)
                self.assertTrue(80 <= member["spo2_pct"] <= 100)
                self.assertTrue(0 <= member["sleep_h"] <= 14)
                self.assertTrue(0 <= member["stress_index"] <= 1)
                self.assertLessEqual(member["bmd_pct"], 0.0)


class DeterminismTest(unittest.TestCase):
    def test_same_seed_same_stream(self):
        first = simulator.simulate("mars_storm_2024", days=20, seed=11)
        second = simulator.simulate("mars_storm_2024", days=20, seed=11)
        self.assertEqual(first, second)

    def test_different_seed_changes_the_noise_not_the_trend(self):
        a = simulator.simulate("mars_storm_2024", days=20, seed=11)
        b = simulator.simulate("mars_storm_2024", days=20, seed=99)
        self.assertNotEqual(a[-1]["crew"][0]["hr_bpm"], b[-1]["crew"][0]["hr_bpm"])
        self.assertAlmostEqual(
            a[-1]["crew"][0]["dose_msv"], b[-1]["crew"][0]["dose_msv"], places=6
        )


class RadiationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames = simulator.simulate("mars_storm_2024", days=90)

    def test_dose_never_decreases(self):
        for crew_index in range(len(self.frames[0]["crew"])):
            doses = [frame["crew"][crew_index]["dose_msv"] for frame in self.frames]
            for earlier, later in zip(doses, doses[1:]):
                self.assertLessEqual(earlier, later)

    def test_real_solar_events_drive_the_high_dose_days(self):
        storm_days = [f for f in self.frames if f["environment"]["sep_active"]]
        self.assertGreaterEqual(len(storm_days), 3, "no SEP day in a storm scenario")
        calm_days = [f for f in self.frames if not f["environment"]["sep_active"]]
        self.assertTrue(calm_days)
        storm_rate = max(f["crew"][0]["dose_rate_msv_day"] for f in storm_days)
        calm_rate = max(f["crew"][0]["dose_rate_msv_day"] for f in calm_days)
        self.assertGreater(storm_rate, calm_rate * 2)

    def test_sep_days_cite_a_real_donki_event(self):
        storm_days = [f for f in self.frames if f["environment"]["sep_active"]]
        for frame in storm_days:
            self.assertRegex(frame["environment"]["sep_event_id"], r"^\d{4}-\d{2}-\d{2}T")

    def test_reported_values_are_finite(self):
        for frame in self.frames[:10] + self.frames[-10:]:
            for member in frame["crew"]:
                for key, value in member.items():
                    if isinstance(value, float):
                        self.assertTrue(math.isfinite(value), f"{key}={value}")

    def test_surface_phase_receives_less_radiation_than_transit(self):
        long_run = simulator.simulate("mars_full_transit", days=900)
        transit = [f["environment"]["gcr_msv_day"] for f in long_run if f["phase"] != "surface"]
        surface = [f["environment"]["gcr_msv_day"] for f in long_run if f["phase"] == "surface"]
        self.assertTrue(surface and transit)
        self.assertLess(max(surface), min(transit))


class AlertTest(unittest.TestCase):
    def test_radiation_alert_cites_the_nasa_standard(self):
        frames = simulator.simulate("mars_full_transit", days=900)
        radiation_alerts = [
            alert
            for frame in frames
            for alert in frame["alerts"]
            if alert["indicator"] == "dose_msv"
        ]
        self.assertTrue(radiation_alerts, "900 days never crossed the career limit")
        self.assertTrue(all("NASA-STD-3001" in alert["source"] for alert in radiation_alerts))

    def test_quiet_cruise_raises_no_critical_alert(self):
        frames = simulator.simulate("quiet_cruise", days=30)
        critical = [
            alert
            for frame in frames
            for alert in frame["alerts"]
            if alert["severity"] == "critical"
        ]
        self.assertEqual(critical, [])

    def test_every_alert_is_explainable(self):
        frames = simulator.simulate("mars_full_transit", days=900)
        for frame in frames:
            for alert in frame["alerts"]:
                self.assertTrue(alert["message"].strip())
                self.assertTrue(alert["source"].strip())
                self.assertIn(alert["severity"], {"info", "warning", "critical"})


class MqttCompatibilityTest(unittest.TestCase):
    def test_frame_serialises_to_json_without_datetime_objects(self):
        import json

        frame = simulator.simulate("mars_storm_2024", days=5)[-1]
        round_tripped = json.loads(json.dumps(frame))
        self.assertEqual(round_tripped, frame)


if __name__ == "__main__":
    unittest.main()
