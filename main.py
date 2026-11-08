"""
Smart Posture Guard — Main Entry Point
Thin orchestrator: camera loop, keyboard handling, resource cleanup.

Keyboard shortcuts
------------------
  q  — quit
  s  — print session summary to stdout
"""
import time

import cv2

import config
from analyzer import PostureAnalyzer
from detector import PoseDetector
from notifier import AlertNotifier
from stats import SessionStats
from ui import draw_status_panel


def main() -> None:
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    print("[INFO] Smart Posture Guard started. Press 'q' to quit, 's' for stats.")

    stats    = SessionStats()
    notifier = AlertNotifier(cooldown=config.ALERT_COOLDOWN)
    analyzer = PostureAnalyzer()

    bad_posture_start: float | None = None
    alert_active      = False

    # FPS tracking
    fps_prev_time = time.time()
    fps           = 0.0

    try:
        with PoseDetector() as detector:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    print("[ERROR] Failed to read frame from camera.")
                    break

                # Mirror effect
                frame = cv2.flip(frame, 1)

                # ── Pose detection & analysis ────────────────────────────────
                frame, landmarks = detector.find_pose(frame, draw=True)
                result = analyzer.analyze(landmarks)

                # ── Alert logic ──────────────────────────────────────────────
                if result.present and result.status == "POOR":
                    if bad_posture_start is None:
                        bad_posture_start = time.time()
                    elif time.time() - bad_posture_start >= config.BAD_POSTURE_GRACE_PERIOD:
                        alert_active = True
                        if notifier.notify():
                            stats.record_alert()
                else:
                    bad_posture_start = None
                    alert_active      = False

                # ── Session stats ────────────────────────────────────────────
                stats.tick(result.status if result.present else "AWAY")

                # ── FPS counter ──────────────────────────────────────────────
                now        = time.time()
                fps        = 1.0 / max(now - fps_prev_time, 1e-6)
                fps_prev_time = now

                # ── HUD overlay ──────────────────────────────────────────────
                draw_status_panel(frame, result, alert_active, fps, stats)

                cv2.imshow("Smart Posture Guard", frame)

                # ── Keyboard shortcuts ───────────────────────────────────────
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("s"):
                    summary = stats.summary()
                    print(
                        f"\n[STATS] Session: {summary['total_min']} min | "
                        f"Good: {summary['good_pct']}% | "
                        f"Poor: {summary['poor_pct']}% | "
                        f"Alerts: {summary['alerts']}\n"
                    )

    finally:
        cap.release()
        cv2.destroyAllWindows()
        summary = stats.summary()
        print(
            f"\n[SESSION END] Duration: {summary['total_min']} min | "
            f"Good: {summary['good_pct']}% | "
            f"Poor: {summary['poor_pct']}% | "
            f"Alerts fired: {summary['alerts']}"
        )


if __name__ == "__main__":
    main()
