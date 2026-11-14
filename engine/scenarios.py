"""Scenario definitions: a mission timeline plus the crew roster."""

CREW_ROLES = [
    ("CDR", "Commander"),
    ("PLT", "Pilot"),
    ("FSR", "Mission Specialist, flight surgeon"),
    ("ENG", "Mission Specialist, engineer"),
]

SCENARIOS = {
    "mars_storm_2024": {
        "title": "Mars transit, May 2024 storm series",
        "epoch": "2024-04-15",
        "days": 90,
        # (start day, phase) in mission-order; last open ended.
        "phases": [(0, "transit_out"), (30, "surface"), (90, "surface")],
        "shield_g_cm2": 20.0,
        "summary": (
            "A 90-day window that deliberately crosses the May 2024 solar storm series, "
            "the strongest of solar cycle 25."
        ),
    },
    "mars_full_transit": {
        "title": "Full Mars mission, real solar activity 2024-2026",
        "epoch": "2024-01-01",
        "days": 900,
        "phases": [(0, "transit_out"), (210, "surface"), (690, "transit_return")],
        "shield_g_cm2": 20.0,
        "summary": (
            "Outbound transit, a surface stay and the return leg, driven by every SEP event "
            "DONKI recorded between January 2024 and November 2026."
        ),
    },
    "quiet_cruise": {
        "title": "Quiet cruise, low solar activity",
        "epoch": "2025-04-01",
        "days": 30,
        "phases": [(0, "transit_out")],
        "shield_g_cm2": 20.0,
        "summary": "A control run: no storm expected, so the crew should stay nominal.",
    },
}


def default_scenario():
    return "mars_storm_2024"
