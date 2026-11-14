"""Every number the engine uses, with the source that justifies it.

Values are taken from NASA-STD-3001 Rev C (2023) and the primary spaceflight
physiology literature. Where no published standard exists, the constant says so
instead of inventing a threshold.
"""

# --- Radiation -------------------------------------------------------------

# Career effective dose limit. Universal for all ages and sexes since Rev C.
CAREER_LIMIT_MSV = 600.0
CAREER_LIMIT_SOURCE = (
    "NASA-STD-3001 Vol 1 Rev C (2023), section 4.8.2: career effective dose "
    "below 600 mSv, universal for all ages and sexes (3% REID basis)"
)

# Acute limit for a design-reference solar particle event.
ACUTE_EVENT_LIMIT_MSV = 250.0
ACUTE_EVENT_SOURCE = (
    "NASA-STD-3001 Vol 1 Rev C (2023), section 4.8.3: effective dose from a "
    "design-reference solar particle event below 250 mSv"
)

# Crew design dose rates. These are the shielded, in-vehicle rates the standard
# uses; RAD's 1.84 and 0.64 mSv/day are the measured ambient environment outside
# the hull, and are quoted in the docs as evidence, not used as crew dose.
GCR_TRANSIT_MSV_DAY = 1.3
GCR_TRANSIT_SOURCE = (
    "NASA-STD-3001 Vol 1 Rev C (2023), section 4.8.5: design rate of 1.3 mSv/day "
    "in free space"
)

GCR_SURFACE_MSV_DAY = 0.9
GCR_SURFACE_SOURCE = (
    "NASA-STD-3001 Vol 1 Rev C (2023), section 4.8.5: design rate of 0.9 mSv/day "
    "on planetary surfaces"
)

# Measured ambient rates from MSL/RAD, shown to the user as context.
RAD_MEASURED_CRUISE_MSV_DAY = 1.84
RAD_MEASURED_SURFACE_MSV_DAY = 0.64
RAD_MEASURED_SOURCE = (
    "Zeitlin et al. 2013, Science 343:1080 (cruise) and Hassler et al. 2014, "
    "Science 343:1244797 (surface): ambient dose equivalent outside shielding"
)

# Dose equivalent contributed by one solar particle event day behind the nominal
# shielding. Published per-event values in deep space span 1.2 to 19.5 mSv; the
# low end is used because the design GCR rate already carries the average solar
# contribution. No pfu-to-mSv conversion is published: DONKI's single integral
# proton flux omits the spectral shape that transport codes require.
SEP_DOSE_MSV_PER_EVENT_DAY = 2.0
SEP_DOSE_RANGE_MSV = (1.2, 19.5)
SEP_SOURCE = (
    "Per-event dose equivalents behind stated shielding, 1.2-19.5 mSv (NASEM "
    "2024 summary of MSL/RAD cruise data); no published pfu-to-mSv conversion"
)
SEP_SOURCE_PREFIX = "DONKI SEP event"

# --- Physiology ------------------------------------------------------------

# Bone mineral density loss per month in microgravity without effective
# countermeasures, femoral neck range 1.0-1.5 %/month.
BMD_LOSS_PCT_MONTH = 1.0
BMD_SOURCE = (
    "LeBlanc et al. 2000, J Musculoskelet Neuronal Interact 1(2):157; Sibonga "
    "et al. 2007: averaged monthly hip loss of 1-1.5% long duration"
)

# Martian gravity reduces mechanical unloading relative to free fall.
BMD_SURFACE_FACTOR = 0.5

# Muscle volume loss without countermeasures: 5-17% over 16-28 weeks.
MUSCLE_LOSS_PCT_MONTH = 1.5
MUSCLE_SOURCE = (
    "LeBlanc et al. 2000, J Appl Physiol 89:2158: 5-17% muscle volume decrease "
    "across shuttle and Mir missions"
)

# Aerobic capacity decline. The NASA design assumption is an average 15% decline
# across a six-month mission, which this rate reproduces.
AEROBIC_LOSS_PCT_MONTH = 2.5
AEROBIC_LOSS_CAP_PCT = 25.0
AEROBIC_SOURCE = (
    "NASA-STD-3001 Vol 1 Rev C Table 4.1-1 and rationale: average 15% in-mission "
    "VO2max decline across six months"
)

# Average sleep per 24 h in flight, 6.09 +/- 0.67 h.
SLEEP_BASELINE_H = 6.1
SLEEP_SOURCE = (
    "Barger et al. 2014, Lancet Neurology 13(9):904: crew averaged 6.09 h in "
    "flight, 75% used sleep-promoting medication"
)

SLEEP_WARNING_H = 5.5
SLEEP_THRESHOLD_SOURCE = (
    "Barger et al. 2014: in-flight mean 6.09 h; 5.5 h marks sustained restriction "
    "against that distribution"
)

# --- Alerts ----------------------------------------------------------------

STRESS_WARNING = 0.75
STRESS_SOURCE = (
    "Composite behavioural load indicator, declared as a proxy, not a clinical scale"
)

BMD_WARNING_PCT = -6.0
BMD_THRESHOLD_SOURCE = (
    "LeBlanc et al. 2000, Sibonga et al. 2007: losses beyond 6% approach the "
    "fracture-risk range in long-duration crew"
)

# Nothing in NASA-STD-3001 sets a resting heart rate or SpO2 requirement for
# crew in flight. The engine reports both as descriptive telemetry and never
# raises an alert on them.
NO_STANDARD_SOURCE = (
    "No published reference standard exists; NASA-STD-3001 Rev C sets no resting "
    "heart rate or SpO2 requirement. Shown as descriptive telemetry only."
)
