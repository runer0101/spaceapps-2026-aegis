"""HTTP contract of the telemetry server.

The demo must run with nothing but the Python standard library, so the server
is exercised the way a judge will use it: plain HTTP against a real socket.
"""

import json
import pathlib
import sys
import threading
import unittest
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server import app  # noqa: E402


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.make_server(port=0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def get(self, path, timeout=10):
        url = f"http://127.0.0.1:{self.port}{path}"
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status, response.headers.get("Content-Type"), response.read()

    def test_scenarios_endpoint_lists_every_scenario(self):
        status, content_type, body = self.get("/api/scenarios")
        self.assertEqual(status, 200)
        self.assertIn("application/json", content_type)
        payload = json.loads(body)
        self.assertEqual(len(payload["scenarios"]), 3)
        self.assertEqual(payload["default"], "mars_storm_2024")
        for scenario in payload["scenarios"]:
            self.assertTrue(scenario["id"])
            self.assertTrue(scenario["title"])
            self.assertGreater(scenario["days"], 0)

    def test_simulate_returns_a_full_timeline(self):
        status, _, body = self.get("/api/simulate?scenario=quiet_cruise")
        self.assertEqual(status, 200)
        frames = json.loads(body)["frames"]
        self.assertEqual(len(frames), 30)
        self.assertEqual(frames[0]["t_day"], 0.0)

    def test_unknown_scenario_is_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.get("/api/simulate?scenario=does_not_exist")
        self.assertEqual(caught.exception.code, 404)
        payload = json.loads(caught.exception.read())
        self.assertIn("error", payload)

    def test_stream_emits_frames_as_server_sent_events(self):
        url = f"http://127.0.0.1:{self.port}/stream?scenario=quiet_cruise&interval=0.01"
        frames = []
        with urllib.request.urlopen(url, timeout=10) as response:
            self.assertIn("text/event-stream", response.headers.get("Content-Type"))
            for raw in response:
                line = raw.decode().strip()
                if line.startswith("data:"):
                    frames.append(json.loads(line[5:].strip()))
                    if len(frames) == 3:
                        break
        self.assertEqual([frame["t_day"] for frame in frames], [0.0, 1.0, 2.0])

    def test_index_page_is_served(self):
        status, content_type, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", content_type)
        self.assertIn(b"<html", body.lower())

    def test_path_traversal_is_refused(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.get("/../../etc/passwd")
        self.assertEqual(caught.exception.code, 404)


class EvidenceTest(unittest.TestCase):
    """The triage module retrieves real OSDR studies; it never invents one."""

    @classmethod
    def setUpClass(cls):
        cls.server = app.make_server(port=0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def get(self, path):
        url = f"http://127.0.0.1:{self.port}{path}"
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.status, json.loads(response.read())

    def test_bone_indicator_returns_osdr_bone_studies(self):
        status, payload = self.get("/api/evidence?indicator=bmd_pct")
        self.assertEqual(status, 200)
        self.assertTrue(payload["studies"])
        for study in payload["studies"]:
            self.assertRegex(study["accession"], r"^OSD-\d+$")
            self.assertTrue(study["title"])
        self.assertIn("NASA", payload["source"])

    def test_radiation_indicator_returns_radiation_studies(self):
        _, payload = self.get("/api/evidence?indicator=dose_msv")
        self.assertTrue(payload["studies"])
        self.assertEqual(payload["indicator"], "dose_msv")

    def test_unknown_indicator_returns_an_empty_result_not_an_error(self):
        status, payload = self.get("/api/evidence?indicator=not_an_indicator")
        self.assertEqual(status, 200)
        self.assertEqual(payload["studies"], [])


if __name__ == "__main__":
    unittest.main()
