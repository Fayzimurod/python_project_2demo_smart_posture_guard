"""
Smart Posture Guard — Central Configuration
All thresholds and constants in one place.
"""

# ── Camera ──────────────────────────────────────────────────────────────────
CAMERA_INDEX   = 0
FRAME_WIDTH    = 1280
FRAME_HEIGHT   = 720

# ── Pose Detection ───────────────────────────────────────────────────────────
MIN_DETECTION_CONF = 0.65
MIN_TRACKING_CONF  = 0.65
MIN_VISIBILITY     = 0.50   # Landmarks below this visibility score are ignored

# ── Posture Analysis ─────────────────────────────────────────────────────────
SHOULDER_TILT_THRESHOLD = 12.0  # degrees — asymmetric shoulder tilt
NECK_RATIO_THRESHOLD    = 0.35  # ear-shoulder distance / shoulder width
SMOOTHING_WINDOW        = 8     # frames for temporal smoothing (majority vote)

# ── Alert Timing ─────────────────────────────────────────────────────────────
BAD_POSTURE_GRACE_PERIOD = 3.0   # seconds before alert fires
ALERT_COOLDOWN           = 10.0  # seconds between repeated alerts

# ── UI ───────────────────────────────────────────────────────────────────────
UI_BOX_COLOR   = (30, 30, 30)
COLOR_GOOD     = (0, 220, 100)
COLOR_WARN     = (0, 220, 255)
COLOR_CRITICAL = (0, 60, 255)
COLOR_AWAY     = (120, 120, 120)
FONT           = 0  # cv2.FONT_HERSHEY_SIMPLEX
