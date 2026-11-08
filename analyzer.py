"""
Smart Posture Guard — Posture Analyzer
Uses temporal smoothing and ear-shoulder-hip geometry for robust posture detection.
"""
import math
from collections import deque
from dataclasses import dataclass, field

from config import (
    NECK_RATIO_THRESHOLD,
    SHOULDER_TILT_THRESHOLD,
    SMOOTHING_WINDOW,
)

# MediaPipe Pose landmark indices used for posture analysis
_L_EAR      = 7
_R_EAR      = 8
_L_SHOULDER = 11
_R_SHOULDER = 12
_L_HIP      = 23
_R_HIP      = 24


@dataclass
class PostureResult:
    """Structured result returned by PostureAnalyzer.analyze()."""

    present: bool           # True if a person is detected
    status: str             # "GOOD" | "POOR" | "NO_PERSON"
    details: dict = field(default_factory=dict)
    confidence: float = 1.0


class PostureAnalyzer:
    """
    Analyses posture from MediaPipe landmark dicts.

    Uses a sliding window (deque) of the last ``SMOOTHING_WINDOW`` frames
    to produce a majority-vote status, preventing single-frame flickering.

    Neck posture uses the gold-standard ear-shoulder distance ratio:
        neck_ratio = (avg_shoulder_y − avg_ear_y) / shoulder_width
    A ratio below NECK_RATIO_THRESHOLD → forward head / slouch detected.
    """

    def __init__(self) -> None:
        self._history: deque[str] = deque(maxlen=SMOOTHING_WINDOW)

    # ── Public API ───────────────────────────────────────────────────────────

    def analyze(self, landmarks: dict) -> PostureResult:
        """Return a smoothed PostureResult for the given landmark dict."""
        if not self._has_required_landmarks(landmarks):
            self._history.clear()
            return PostureResult(present=False, status="NO_PERSON")

        raw_status, details = self._raw_analysis(landmarks)
        self._history.append(raw_status)
        smoothed_status = self._majority_vote()

        confidence = self._history.count(smoothed_status) / len(self._history)

        return PostureResult(
            present=True,
            status=smoothed_status,
            details=details,
            confidence=round(confidence, 2),
        )

    # ── Internal helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _has_required_landmarks(landmarks: dict) -> bool:
        """Require both shoulders to be visible at minimum."""
        return _L_SHOULDER in landmarks and _R_SHOULDER in landmarks

    def _raw_analysis(self, landmarks: dict) -> tuple[str, dict]:
        """Compute raw (un-smoothed) posture status and diagnostic details."""
        l_sh = landmarks[_L_SHOULDER]
        r_sh = landmarks[_R_SHOULDER]

        shoulder_width = math.hypot(l_sh[0] - r_sh[0], l_sh[1] - r_sh[1])
        shoulder_tilt = self._line_angle(l_sh, r_sh)

        bad_posture = False
        neck_ratio: float | None = None

        # ── Neck / forward-head check (ear-shoulder distance ratio) ─────────
        l_ear = landmarks.get(_L_EAR)
        r_ear = landmarks.get(_R_EAR)

        if l_ear is not None and r_ear is not None and shoulder_width > 0:
            avg_ear_y = (l_ear[1] + r_ear[1]) / 2.0
            avg_shoulder_y = (l_sh[1] + r_sh[1]) / 2.0
            neck_distance = avg_shoulder_y - avg_ear_y

            neck_ratio = round(neck_distance / shoulder_width, 3)
            if neck_ratio < NECK_RATIO_THRESHOLD:
                bad_posture = True  # head too close to shoulders → slouching

        # ── Shoulder tilt / asymmetry check ─────────────────────────────────
        tilt_bad = shoulder_tilt > SHOULDER_TILT_THRESHOLD
        if tilt_bad:
            bad_posture = True

        status = "POOR" if bad_posture else "GOOD"

        details = {
            "shoulder_width": round(shoulder_width, 1),
            "shoulder_tilt": round(shoulder_tilt, 1),
            "tilt_bad": tilt_bad,
        }
        if neck_ratio is not None:
            details["neck_ratio"] = neck_ratio
            details["neck_bad"] = neck_ratio < NECK_RATIO_THRESHOLD

        return status, details

    def _majority_vote(self) -> str:
        """Return the most common status in the recent history window."""
        if not self._history:
            return "NO_PERSON"
        return max(set(self._history), key=self._history.count)

    @staticmethod
    def _line_angle(p1: tuple, p2: tuple) -> float:
        """Absolute angle of the line p1→p2 relative to the horizontal axis (degrees)."""
        return abs(math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0])))
