"""
Smart Posture Guard — UI / HUD Overlay
All cv2 drawing logic lives here — keeps main.py clean.
"""
import cv2

import config
from analyzer import PostureResult
from stats import SessionStats


def draw_status_panel(
    frame,
    result: PostureResult,
    alert_active: bool,
    fps: float,
    stats: SessionStats,
) -> None:
    """
    Draw the HUD overlay onto *frame* in-place.

    Layout
    ------
    Top-left panel  : posture status, details, FPS
    Bottom-left strip: session stats (good %, poor %, alerts, total time)
    """
    h, w = frame.shape[:2]

    # ── Choose colour based on current state ────────────────────────────────
    if not result.present:
        color = config.COLOR_AWAY
    elif alert_active:
        color = config.COLOR_CRITICAL
    elif result.status == "POOR":
        color = config.COLOR_WARN
    else:
        color = config.COLOR_GOOD

    # ── Top-left status panel ────────────────────────────────────────────────
    panel_x1, panel_y1 = 15, 15
    panel_x2, panel_y2 = 480, 170
    _filled_rect(frame, panel_x1, panel_y1, panel_x2, panel_y2, config.UI_BOX_COLOR, alpha=0.6)

    # Main status text
    if not result.present:
        status_text = "Status: AWAY"
    elif alert_active:
        status_text = "CRITICAL: SLOUCHING!"
    else:
        status_text = f"Posture: {result.status}"

    cv2.putText(
        frame, status_text, (25, 55),
        config.FONT, 0.9, color, 2, cv2.LINE_AA
    )

    # Detail line 1 — shoulder tilt
    if result.present and "shoulder_tilt" in result.details:
        tilt = result.details["shoulder_tilt"]
        tilt_ok = not result.details.get("tilt_bad", False)
        tilt_color = config.COLOR_GOOD if tilt_ok else config.COLOR_WARN
        cv2.putText(
            frame, f"Shoulder tilt : {tilt:.1f} deg", (25, 90),
            config.FONT, 0.6, tilt_color, 1, cv2.LINE_AA
        )

    # Detail line 2 — neck ratio
    if result.present and "neck_ratio" in result.details:
        ratio = result.details["neck_ratio"]
        neck_ok = not result.details.get("neck_bad", False)
        neck_color = config.COLOR_GOOD if neck_ok else config.COLOR_WARN
        cv2.putText(
            frame, f"Neck ratio    : {ratio:.3f} (min {config.NECK_RATIO_THRESHOLD})", (25, 115),
            config.FONT, 0.6, neck_color, 1, cv2.LINE_AA
        )

    # Confidence / smoothing
    if result.present:
        cv2.putText(
            frame, f"Confidence    : {result.confidence:.0%}", (25, 140),
            config.FONT, 0.55, (180, 180, 180), 1, cv2.LINE_AA
        )

    # FPS (top-right of the status panel)
    fps_text = f"FPS: {fps:.0f}"
    (tw, _), _ = cv2.getTextSize(fps_text, config.FONT, 0.6, 1)
    cv2.putText(
        frame, fps_text, (panel_x2 - tw - 10, 45),
        config.FONT, 0.6, (200, 200, 200), 1, cv2.LINE_AA
    )

    # ── Bottom-left session stats strip ─────────────────────────────────────
    summary = stats.summary()
    stats_y1 = h - 55
    stats_y2 = h - 10
    _filled_rect(frame, 15, stats_y1, 500, stats_y2, config.UI_BOX_COLOR, alpha=0.5)

    stats_text = (
        f"Session {summary['total_min']} min  |  "
        f"Good {summary['good_pct']}%  "
        f"Poor {summary['poor_pct']}%  |  "
        f"Alerts: {summary['alerts']}"
    )
    cv2.putText(
        frame, stats_text, (22, h - 23),
        config.FONT, 0.52, (200, 200, 200), 1, cv2.LINE_AA
    )

    # ── Alert flash border ───────────────────────────────────────────────────
    if alert_active:
        cv2.rectangle(frame, (0, 0), (w - 1, h - 1), config.COLOR_CRITICAL, 6)


# ── Private helpers ──────────────────────────────────────────────────────────

def _filled_rect(frame, x1: int, y1: int, x2: int, y2: int, color: tuple, alpha: float = 0.5) -> None:
    """Draw a semi-transparent filled rectangle on *frame* in-place."""
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
