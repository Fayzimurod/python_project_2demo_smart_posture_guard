"""
Smart Posture Guard — Pose Detector
Wraps MediaPipe Pose with proper resource management and visibility filtering.
"""
import cv2
import mediapipe as mp

from config import MIN_DETECTION_CONF, MIN_TRACKING_CONF, MIN_VISIBILITY

# Use the public API — not the fragile internal path
_mp_pose = mp.solutions.pose
_mp_draw = mp.solutions.drawing_utils


class PoseDetector:
    """
    Detects human body pose landmarks from a BGR frame.

    Supports context manager usage::

        with PoseDetector() as detector:
            frame, landmarks = detector.find_pose(frame)

    Returns landmarks as ``dict[int, tuple[int, int, float]]``
    where each value is ``(x_px, y_px, z_norm)``.
    Landmarks whose MediaPipe visibility score falls below
    ``MIN_VISIBILITY`` are omitted to avoid bad data.
    """

    def __init__(
        self,
        min_detection_confidence: float = MIN_DETECTION_CONF,
        min_tracking_confidence: float = MIN_TRACKING_CONF,
    ) -> None:
        self._pose = _mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    # ── Context manager ──────────────────────────────────────────────────────

    def __enter__(self) -> "PoseDetector":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def close(self) -> None:
        """Release the underlying MediaPipe Pose graph."""
        self._pose.close()

    # ── Core API ─────────────────────────────────────────────────────────────

    def find_pose(
        self, img, draw: bool = True
    ) -> tuple:
        """
        Process a BGR frame and return the annotated frame plus filtered landmarks.

        Parameters
        ----------
        img  : BGR numpy array (H × W × 3)
        draw : whether to draw skeleton overlay on the returned frame

        Returns
        -------
        (img, landmarks)
            img       — same frame, optionally annotated
            landmarks — dict[int, (x_px, y_px, z_norm)] for visible landmarks only
        """
        try:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self._pose.process(img_rgb)
        except Exception as exc:
            print(f"[PoseDetector] Processing error: {exc}")
            return img, {}

        landmarks: dict[int, tuple[int, int, float]] = {}

        if results.pose_landmarks:
            if draw:
                _mp_draw.draw_landmarks(
                    img, results.pose_landmarks, _mp_pose.POSE_CONNECTIONS
                )

            h, w = img.shape[:2]
            for idx, lm in enumerate(results.pose_landmarks.landmark):
                if lm.visibility < MIN_VISIBILITY:
                    continue  # skip low-confidence landmarks
                landmarks[idx] = (int(lm.x * w), int(lm.y * h), lm.z)

        return img, landmarks
