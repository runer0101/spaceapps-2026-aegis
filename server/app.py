"""Serve the dashboard, the timeline API and the live telemetry stream.

Run it with:
    python3 -m server.app --port 8000

Standard library only: no pip install, no build step, no node.
"""

import argparse
import json
import mimetypes
import pathlib
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
sys.path.insert(0, str(ROOT))

from engine import scenarios, simulator  # noqa: E402

mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/javascript", ".mjs")
mimetypes.add_type("application/octet-stream", ".glb")

# Which OSDR corpus term answers each indicator the engine can raise.
EVIDENCE_TERMS = {
    "bmd_pct": "bone",
    "muscle_pct": "muscle",
    "dose_msv": "radiation",
    "hr_bpm": "cardiovascular",
    "sleep_h": "sleep",
    "stress_index": "behavioral",
}
OSDR_DATASET = ROOT / "data" / "osdr-bone-studies.json"
_osdr_cache = None


def osdr_studies():
    global _osdr_cache
    if _osdr_cache is None:
        _osdr_cache = json.loads(OSDR_DATASET.read_text())["studies"]
    return _osdr_cache


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, fmt, *args):
        pass

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/api/scenarios":
                return self.api_scenarios()
            if parsed.path == "/api/simulate":
                return self.api_simulate(query)
            if parsed.path == "/api/evidence":
                return self.api_evidence(query)
            if parsed.path == "/stream":
                return self.stream(query)
            return self.static(parsed.path)
        except BrokenPipeError:
            return

    def api_scenarios(self):
        listing = [
            {
                "id": key,
                "title": value["title"],
                "days": value["days"],
                "epoch": value["epoch"],
                "summary": value["summary"],
            }
            for key, value in scenarios.SCENARIOS.items()
        ]
        self.send_json({"scenarios": listing, "default": scenarios.default_scenario()})

    def api_simulate(self, query):
        scenario_id = query.get("scenario", [scenarios.default_scenario()])[0]
        if scenario_id not in scenarios.SCENARIOS:
            return self.send_json({"error": f"unknown scenario: {scenario_id}"}, 404)
        frames = simulator.simulate(scenario_id)
        self.send_json({"scenario": scenario_id, "count": len(frames), "frames": frames})

    def api_evidence(self, query):
        """Retrieve the real OSDR studies behind an indicator. No model, no invention."""
        indicator = query.get("indicator", [""])[0]
        term = EVIDENCE_TERMS.get(indicator)
        studies = []
        if term:
            for study in osdr_studies():
                haystack = (study["title"] + " " + " ".join(study["matched_terms"])).lower()
                if term in haystack:
                    studies.append(
                        {
                            "accession": study["accession"],
                            "title": study["title"],
                            "techniques": study["techniques"],
                        }
                    )
        self.send_json(
            {
                "indicator": indicator,
                "term": term,
                # A study whose title names the topic is better evidence than one
                # that merely matched a search term, so it is shown first.
                "studies": sorted(
                    studies, key=lambda s: 0 if term in s["title"].lower() else 1
                )[:3],
                "source": "NASA Open Science Data Repository (ALSDA)",
            }
        )

    def stream(self, query):
        scenario_id = query.get("scenario", [scenarios.default_scenario()])[0]
        if scenario_id not in scenarios.SCENARIOS:
            return self.send_json({"error": f"unknown scenario: {scenario_id}"}, 404)
        try:
            interval = float(query.get("interval", ["0.18"])[0])
        except ValueError:
            return self.send_json({"error": "interval must be a number"}, 400)
        interval = max(0.005, min(2.0, interval))
        try:
            start = max(0, int(query.get("from", ["0"])[0]))
        except ValueError:
            return self.send_json({"error": "from must be an integer"}, 400)

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()

        for frame in simulator.simulate(scenario_id)[start:]:
            self.wfile.write(f"data: {json.dumps(frame)}\n\n".encode())
            self.wfile.flush()
            time.sleep(interval)

    def static(self, path):
        if path == "/":
            path = "/index.html"
        for base in (WEB, ROOT / "docs"):
            candidate = (base / path.lstrip("/")).resolve()
            if str(candidate).startswith(str(base.resolve())) and candidate.is_file():
                break
        else:
            self.send_error(404, "not found")
            return
        body = candidate.read_bytes()
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {
            "application/javascript",
            "application/json",
        }:
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def make_server(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    return server


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    server = make_server(args.host, args.port)
    print(f"AEGIS on http://{args.host}:{server.server_address[1]}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
