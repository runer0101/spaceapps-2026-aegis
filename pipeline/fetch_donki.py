"""Fetch Solar Energetic Particle events from NASA DONKI into a versioned sample.

The DONKI API rejects queries wider than 60 days, so a long range is walked in
contiguous chunks and de-duplicated by event id.

Usage:
    python3 pipeline/fetch_donki.py --start 2024-01-01 --end 2026-11-14
"""

import argparse
import json
import pathlib
import ssl
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta

ENDPOINT = "https://ccmc.gsfc.nasa.gov/DONKI-API/get/SEP"
MAX_WINDOW_DAYS = 60
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "donki-sep.json"


def parse_day(value):
    return date.fromisoformat(value)


def validate_window(start, end):
    """DONKI accepts at most a 60-day difference between the two dates."""
    span = (parse_day(end) - parse_day(start)).days
    if span <= 0:
        raise ValueError(f"window must end after it starts: {start}..{end}")
    if span > MAX_WINDOW_DAYS:
        raise ValueError(
            f"window is {span} days, DONKI allows at most {MAX_WINDOW_DAYS}: {start}..{end}"
        )
    return span


def window_chunks(start, end):
    """Split a range into contiguous windows that share their boundary day."""
    if parse_day(end) <= parse_day(start):
        raise ValueError(f"range must end after it starts: {start}..{end}")
    chunks = []
    cursor = parse_day(start)
    last = parse_day(end)
    while cursor < last:
        stop = min(cursor + timedelta(days=MAX_WINDOW_DAYS), last)
        chunks.append((cursor.isoformat(), stop.isoformat()))
        cursor = stop
    return chunks


def fetch_window(start, end, insecure=False):
    validate_window(start, end)
    url = f"{ENDPOINT}?startDate={start}&endDate={end}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    context = ssl._create_unverified_context() if insecure else None
    with urllib.request.urlopen(request, timeout=60, context=context) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload or []


def normalise(event):
    instruments = event.get("instruments") or []
    return {
        "sepID": event.get("sepID"),
        "eventTime": event.get("eventTime"),
        "instruments": [i.get("displayName", "") for i in instruments],
        "linkedEvents": [e.get("activityID") for e in (event.get("linkedEvents") or [])],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default=date.today().isoformat())
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="skip TLS verification (only for machines behind a corporate CA)",
    )
    args = parser.parse_args(argv)

    seen = {}
    chunks = window_chunks(args.start, args.end)
    for index, (start, end) in enumerate(chunks, 1):
        try:
            events = fetch_window(start, end, insecure=args.insecure)
        except urllib.error.URLError as error:
            if "CERTIFICATE_VERIFY_FAILED" in str(error):
                sys.exit(
                    "TLS verification failed. On a machine with a corporate CA run again "
                    "with --insecure; the published data itself needs no key."
                )
            raise
        fresh = 0
        for event in events:
            record = normalise(event)
            if record["sepID"] and record["sepID"] not in seen:
                seen[record["sepID"]] = record
                fresh += 1
        print(f"[{index}/{len(chunks)}] {start}..{end}: {len(events)} events, {fresh} new")

    events = sorted(seen.values(), key=lambda e: e["eventTime"] or "")
    document = {
        "source": "NASA DONKI SEP API",
        "endpoint": ENDPOINT,
        "range": {"start": args.start, "end": args.end},
        "count": len(events),
        "events": events,
    }
    pathlib.Path(args.out).write_text(json.dumps(document, indent=1) + "\n")
    print(f"wrote {len(events)} events to {args.out}")


if __name__ == "__main__":
    main()
