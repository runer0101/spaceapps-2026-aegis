"""Declared physiological model, one crew member, one day at a time.

These are published rates applied to a simulated crew, never a medical model.
The dashboard shows the source next to every threshold for that reason.
"""

import random

from . import citations as C

DAYS_PER_MONTH = 30.4


class CrewMember:
    def __init__(self, crew_id, role, seed):
        self.crew_id = crew_id
        self.role = role
        self.rng = random.Random(seed)
        self.bmd_pct = 0.0
        self.muscle_pct = 0.0
        self.dose_msv = 0.0
        self.aerobic_pct = 0.0
        self.base_hr = 62.0 + self.rng.uniform(0.0, 12.0)
        self.sleep_debt_h = 0.0

    def step(self, phase, environment):
        surface = phase == "surface"
        gravity_factor = C.BMD_SURFACE_FACTOR if surface else 1.0

        self.bmd_pct -= (
            C.BMD_LOSS_PCT_MONTH / DAYS_PER_MONTH * gravity_factor
        )
        self.muscle_pct -= C.MUSCLE_LOSS_PCT_MONTH / DAYS_PER_MONTH * gravity_factor
        self.aerobic_pct = max(
            -C.AEROBIC_LOSS_CAP_PCT,
            self.aerobic_pct - C.AEROBIC_LOSS_PCT_MONTH / DAYS_PER_MONTH * gravity_factor,
        )
        self.dose_msv += environment["dose_rate_msv_day"]

        storm = environment["sep_active"]
        sleep = C.SLEEP_BASELINE_H + self.rng.gauss(0.0, 0.7)
        if storm:
            sleep -= 0.8
        sleep = max(0.0, min(14.0, sleep))
        self.sleep_debt_h = max(0.0, self.sleep_debt_h + (7.5 - sleep))

        stress = 0.20 + (0.35 if storm else 0.0) + min(0.25, self.sleep_debt_h / 60.0)
        stress = max(0.0, min(1.0, stress + self.rng.gauss(0.0, 0.03)))

        deconditioning = min(12.0, self.dose_msv / 90.0)
        heart_rate = self.base_hr + deconditioning + (8.0 if storm else 0.0)
        heart_rate = max(40.0, min(200.0, heart_rate + self.rng.gauss(0.0, 3.0)))

        spo2 = 97.0 - (0.4 if storm else 0.0) + self.rng.gauss(0.0, 0.6)
        spo2 = max(80.0, min(100.0, spo2))

        return {
            "id": self.crew_id,
            "role": self.role,
            "hr_bpm": round(heart_rate, 1),
            "spo2_pct": round(spo2, 1),
            "sleep_h": round(sleep, 1),
            "stress_index": round(stress, 2),
            "bmd_pct": round(self.bmd_pct, 2),
            "muscle_pct": round(self.muscle_pct, 2),
            "aerobic_pct": round(self.aerobic_pct, 1),
            "dose_msv": round(self.dose_msv, 1),
            "dose_rate_msv_day": round(environment["dose_rate_msv_day"], 2),
        }
