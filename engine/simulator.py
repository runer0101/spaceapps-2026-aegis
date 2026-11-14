"""Turn a scenario into a deterministic stream of telemetry frames."""

from . import citations as C
from . import physiology, radiation, scenarios


def phase_for(scenario, day):
    phases = scenario["phases"]
    current = phases[0][1]
    for start, name in phases:
        if day >= start:
            current = name
    return current


def build_alerts(crew_frames, environment, phase):
    alerts = []
    if environment["dose_rate_msv_day"] >= C.ACUTE_EVENT_LIMIT_MSV:
        alerts.append(
            {
                "indicator": "acute_event_msv",
                "severity": "critical",
                "crew": "crew",
                "value": environment["dose_rate_msv_day"],
                "threshold": C.ACUTE_EVENT_LIMIT_MSV,
                "message": (
                    f"Acute dose today {environment['dose_rate_msv_day']:.0f} mSv exceeds "
                    f"the {C.ACUTE_EVENT_LIMIT_MSV:.0f} mSv design-reference event limit."
                ),
                "source": C.ACUTE_EVENT_SOURCE,
            }
        )

    worst = max(crew_frames, key=lambda member: member["dose_msv"])
    if worst["dose_msv"] >= C.CAREER_LIMIT_MSV:
        alerts.append(
            {
                "indicator": "dose_msv",
                "severity": "critical",
                "crew": worst["id"],
                "value": worst["dose_msv"],
                "threshold": C.CAREER_LIMIT_MSV,
                "message": (
                    f"Cumulative dose {worst['dose_msv']:.0f} mSv passes the career "
                    f"limit of {C.CAREER_LIMIT_MSV:.0f} mSv."
                ),
                "source": C.CAREER_LIMIT_SOURCE,
            }
        )

    if environment["sep_active"]:
        alerts.append(
            {
                "indicator": "sep_active",
                "severity": "warning",
                "crew": "crew",
                "value": environment["sep_flux_pfu"],
                "threshold": 0.0,
                "message": (
                    f"Solar energetic particle event in progress: "
                    f"{len(environment['sep_events'])} recorded event(s) today."
                ),
                "source": f"DONKI SEP {environment['sep_event_id']}",
            }
        )

    for member in crew_frames:
        if member["sleep_h"] < C.SLEEP_WARNING_H:
            alerts.append(
                {
                    "indicator": "sleep_h",
                    "severity": "warning",
                    "crew": member["id"],
                    "value": member["sleep_h"],
                    "threshold": C.SLEEP_WARNING_H,
                    "message": f"{member['id']} slept {member['sleep_h']:.1f} h, under the warning line.",
                    "source": C.SLEEP_SOURCE,
                }
            )
        if member["bmd_pct"] <= C.BMD_WARNING_PCT:
            alerts.append(
                {
                    "indicator": "bmd_pct",
                    "severity": "warning",
                    "crew": member["id"],
                    "value": member["bmd_pct"],
                    "threshold": C.BMD_WARNING_PCT,
                    "message": (
                        f"{member['id']} has lost {abs(member['bmd_pct']):.1f}% bone mineral density."
                    ),
                    "source": C.BMD_SOURCE,
                }
            )
        if member["stress_index"] >= C.STRESS_WARNING:
            alerts.append(
                {
                    "indicator": "stress_index",
                    "severity": "info",
                    "crew": member["id"],
                    "value": member["stress_index"],
                    "threshold": C.STRESS_WARNING,
                    "message": f"{member['id']} shows a behavioural load of {member['stress_index']:.2f}.",
                    "source": C.STRESS_SOURCE,
                }
            )
    return alerts


def simulate(scenario_id, days=None, seed=7):
    scenario = scenarios.SCENARIOS[scenario_id]
    total_days = days if days is not None else scenario["days"]
    radiation_model = radiation.Radiation(radiation.load_events())

    crew = [
        physiology.CrewMember(crew_id, role, seed=seed + index)
        for index, (crew_id, role) in enumerate(scenarios.CREW_ROLES)
    ]

    frames = []
    for day in range(total_days):
        phase = phase_for(scenario, day)
        environment = radiation_model.environment(
            day,
            scenario["epoch"],
            phase,
            scenario["shield_g_cm2"],
            forced_msv=scenario.get("forced_events", {}).get(day, 0.0),
        )
        crew_frames = [member.step(phase, environment) for member in crew]
        alerts = build_alerts(crew_frames, environment, phase)
        frames.append(
            {
                "t_day": float(day),
                "calendar_day": environment["calendar_day"],
                "phase": phase,
                "scenario": scenario_id,
                "environment": {
                    "sep_active": environment["sep_active"],
                    "sep_flux_pfu": environment["sep_flux_pfu"],
                    "sep_event_id": environment["sep_event_id"],
                    "gcr_msv_day": environment["gcr_msv_day"],
                    "shield_g_cm2": environment["shield_g_cm2"],
                },
                "crew": crew_frames,
                "alerts": alerts,
            }
        )
    return frames
