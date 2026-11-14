"""Radiation environment: real solar events plus a measured GCR background."""

import json
import pathlib
from datetime import date, timedelta

from . import citations as C

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_DATASET = ROOT / "data" / "donki-sep.json"


def load_events(path=None):
    """Group the versioned DONKI sample by calendar day."""
    document = json.loads(pathlib.Path(path or DEFAULT_DATASET).read_text())
    by_day = {}
    for event in document["events"]:
        day = event["eventTime"][:10]
        by_day.setdefault(day, []).append(event)
    return by_day


class Radiation:
    def __init__(self, events_by_day):
        self.events_by_day = events_by_day

    def environment(self, day_index, epoch, phase, shield_g_cm2, forced_msv=0.0):
        """One day of the mission's radiation environment."""
        calendar_day = date.fromisoformat(epoch) + timedelta(days=day_index)
        todays_events = self.events_by_day.get(calendar_day.isoformat(), [])
        gcr = C.GCR_TRANSIT_MSV_DAY if phase != "surface" else C.GCR_SURFACE_MSV_DAY
        # DONKI files one row per instrument that detected the event, not one row
        # per physical event, so the dose is per event day and never per row.
        sep_rate = (C.SEP_DOSE_MSV_PER_EVENT_DAY if todays_events else 0.0) + forced_msv
        return {
            "calendar_day": calendar_day.isoformat(),
            "sep_active": bool(todays_events) or forced_msv > 0,
            "sep_flux_pfu": float(len(todays_events) * 100),
            "sep_event_id": (
                todays_events[0]["eventTime"]
                if todays_events
                else (f"design-reference {calendar_day.isoformat()}" if forced_msv else None)
            ),
            "sep_events": [event["sepID"] for event in todays_events],
            "gcr_msv_day": gcr,
            "shield_g_cm2": shield_g_cm2,
            "dose_rate_msv_day": gcr + sep_rate,
        }
