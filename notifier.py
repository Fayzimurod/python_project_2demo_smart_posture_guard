"""
Alert manager — plays a system beep on Windows when posture is critical.
No external services. No data leaves the process.
"""
import time
import threading


class AlertNotifier:
    """Thread-safe notifier that fires a beep sound with cooldown protection."""

    def __init__(self, cooldown: float = 10.0):
        self._cooldown = cooldown
        self._last_alert_time = 0.0
        self._lock = threading.Lock()

    def notify(self) -> bool:
        """Fire an alert if cooldown has passed. Returns True if alert was fired."""
        with self._lock:
            now = time.time()
            if now - self._last_alert_time >= self._cooldown:
                self._last_alert_time = now
                threading.Thread(target=self._beep, daemon=True).start()
                return True
            return False

    @staticmethod
    def _beep() -> None:
        """Play a double-beep. Falls back to ASCII bell on non-Windows systems."""
        try:
            import winsound
            winsound.Beep(880, 400)
            time.sleep(0.15)
            winsound.Beep(880, 400)
        except Exception:
            print("\a", end="", flush=True)  # ASCII bell fallback
