"""Contract tests for the public sample data.

These tests never touch the network: they assert over the versioned sample
files and over the pure validation helpers used by the fetch scripts.
"""

import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "pipeline"))


class DonkiWindowTest(unittest.TestCase):
    def setUp(self):
        import fetch_donki

        self.mod = fetch_donki

    def test_rejects_window_longer_than_60_days(self):
        with self.assertRaises(ValueError):
            self.mod.validate_window("2024-01-01", "2024-03-02")

    def test_accepts_window_of_exactly_60_days(self):
        self.mod.validate_window("2024-01-01", "2024-03-01")

    def test_chunks_cover_the_requested_range_without_gaps(self):
        chunks = self.mod.window_chunks("2024-01-01", "2024-05-01")
        self.assertEqual(chunks[0][0], "2024-01-01")
        self.assertEqual(chunks[-1][1], "2024-05-01")
        for start, end in chunks:
            self.mod.validate_window(start, end)
        for (_, prev_end), (next_start, _) in zip(chunks, chunks[1:]):
            self.assertEqual(prev_end, next_start)


class DonkiDatasetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = json.loads((DATA / "donki-sep.json").read_text())["events"]

    def test_events_carry_the_fields_the_engine_reasons_over(self):
        required = {"sepID", "eventTime", "instruments"}
        for event in self.events:
            self.assertTrue(required <= set(event), event)

    def test_event_times_are_iso_utc(self):
        for event in self.events:
            self.assertRegex(event["eventTime"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$")

    def test_event_ids_are_unique(self):
        ids = [event["sepID"] for event in self.events]
        self.assertEqual(len(ids), len(set(ids)))

    def test_covers_the_may_2024_storm_series(self):
        """The May 2024 storm series is the anchor the engine is verified against."""
        in_storm = [
            e for e in self.events if "2024-05-08" <= e["eventTime"][:10] <= "2024-05-20"
        ]
        self.assertGreaterEqual(len(in_storm), 5, "May 2024 storm series missing")


class OsdrDatasetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.studies = json.loads((DATA / "osdr-bone-studies.json").read_text())["studies"]

    def test_studies_carry_accession_and_title(self):
        for study in self.studies:
            self.assertRegex(study["accession"], r"^OSD-\d+$")
            self.assertTrue(study["title"])

    def test_accessions_are_unique(self):
        accessions = [s["accession"] for s in self.studies]
        self.assertEqual(len(accessions), len(set(accessions)))

    def test_bone_measurement_techniques_are_recorded(self):
        techniques = {t for s in self.studies for t in s["techniques"]}
        self.assertTrue(
            techniques & {"Dual-Energy X-Ray Absorptiometry", "Micro-Computed Tomography"},
            techniques,
        )


if __name__ == "__main__":
    unittest.main()
