"""Every number the engine uses, with the source that justifies it.

Values marked ``PENDING`` are being verified against the primary literature
before the demo; the source string is shown to the user either way.
"""

# --- Radiation -------------------------------------------------------------

# Career effective dose limit used by NASA for low Earth orbit missions.
CAREER_LIMIT_MSV = 600.0
CAREER_LIMIT_SOURCE = (
    "NASA-STD-3001 Vol 1, NASA Space Flight Human-System Standard: career "
    "effective dose limit 600 mSv (3% risk of exposure-induced death)"
)

# Galactic cosmic radiation dose rate measured by MSL/RAD on the cruise to Mars.
GCR_TRANSIT_MSV_DAY = 1.84
GCR_TRANSIT_SOURCE = "Hassler et al. 2014, Science 343: radiation environment during cruise"

# Same instrument on the Martian surface, where the planet shields half the sky.
GCR_SURFACE_MSV_DAY = 0.64
GCR_SURFACE_SOURCE = "Hassler et al. 2014, Science 343: radiation environment on the surface"

# Simplified contribution of one solar energetic particle event day behind the
# nominal shielding. This is a declared approximation, not dosimetry.
SEP_DOSE_MSV_PER_EVENT_DAY = 2.5
SEP_SOURCE_PREFIX = "DONKI SEP event"

# --- Physiology ------------------------------------------------------------

# Bone mineral density loss per month in microgravity, with exercise countermeasures.
BMD_LOSS_PCT_MONTH = 1.0
BMD_SOURCE = "LeBlanc et al. 2007, JBMR: bone mineral density loss in long-duration spaceflight"

# Martian gravity reduces mechanical unloading relative to free fall.
BMD_SURFACE_FACTOR = 0.5

# Muscle loss per month without effective countermeasures.
MUSCLE_LOSS_PCT_MONTH = 1.5
MUSCLE_SOURCE = "NASA HRP Evidence Book, Risk of Impaired Performance due to muscle loss"

# Average sleep per 24 h on long-duration ISS missions.
SLEEP_BASELINE_H = 6.0
SLEEP_SOURCE = "Barger et al. 2014, Lancet Neurology: prevalence and patterns of sleep deficiency in ISS crew"

SLEEP_WARNING_H = 5.5
SLEEP_THRESHOLD_SOURCE = "Barger et al. 2014: crew averaged under 6 h per night; 5.5 h marks sustained restriction"

# --- Alerts ----------------------------------------------------------------

STRESS_WARNING = 0.75
STRESS_SOURCE = "Composite behavioural indicator; declared as a proxy, not a clinical scale"

BMD_WARNING_PCT = -6.0
BMD_THRESHOLD_SOURCE = "LeBlanc et al. 2007: losses beyond 6% approach the fracture-risk range"
