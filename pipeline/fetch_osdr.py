"""Fetch spaceflight physiology studies from NASA OSDR into a versioned sample.

The OSDR search API returns study metadata as JSON: which organism was flown,
which measurement technique was used and for how long. The engine uses this as
the published evidence behind its physiological thresholds.

Usage:
    python3 pipeline/fetch_osdr.py
"""

import argparse
import json
import pathlib
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://osdr.nasa.gov/osdr/data/search"
TERMS = ["bone loss", "muscle atrophy", "cardiovascular", "immune", "radiation", "sleep deprivation", "circadian", "behavioral"]
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "osdr-bone-studies.json"
SPLIT = re.compile(r"\s{2,}")


def split_techniques(raw):
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    return [part.strip() for part in SPLIT.split(str(raw)) if part.strip()]


def search(term, size=40, insecure=False):
    query = urllib.parse.urlencode({"term": term, "type": "alsda", "size": size})
    request = urllib.request.Request(
        f"{ENDPOINT}?{query}", headers={"Accept": "application/json"}
    )
    context = ssl._create_unverified_context() if insecure else None
    with urllib.request.urlopen(request, timeout=90, context=context) as response:
        return json.loads(response.read().decode("utf-8"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--insecure", action="store_true")
    args = parser.parse_args(argv)

    studies = {}
    for term in TERMS:
        try:
            payload = search(term, insecure=args.insecure)
        except urllib.error.URLError as error:
            if "CERTIFICATE_VERIFY_FAILED" in str(error):
                sys.exit("TLS verification failed; retry with --insecure on a corporate CA.")
            raise
        hits = payload["hits"]["hits"]
        for hit in hits:
            source = hit["_source"]
            accession = source.get("Accession")
            if not accession or accession in studies:
                continue
            studies[accession] = {
                "accession": accession,
                "title": (source.get("Study Title") or "").strip(),
                "organism": source.get("Study Organism") or "",
                "techniques": split_techniques(source.get("Study Assay Technology Type")),
                "matched_terms": [term],
            }
        print(f"{term!r}: {payload['hits']['total']} studies, {len(hits)} returned")

    ordered = [studies[key] for key in sorted(studies)]
    document = {
        "source": "NASA Open Science Data Repository (ALSDA)",
        "endpoint": ENDPOINT,
        "terms": TERMS,
        "count": len(ordered),
        "studies": ordered,
    }
    pathlib.Path(args.out).write_text(json.dumps(document, indent=1) + "\n")
    print(f"wrote {len(ordered)} studies to {args.out}")


if __name__ == "__main__":
    main()
