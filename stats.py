"""
Session statistics — tracks good/poor/away posture durations.
Thread-safe, no I/O.
"""
import time
import threading
from dataclasses import dataclass, field


@dataclass
class SessionStats:
    """Accumulates per-status time and alert counts for the current session."""

    good_seconds: float = 0.0
    poor_seconds: float = 0.0
    away_seconds: float = 0.0
    alert_count: int = 0

    # Private fields — excluded from repr and comparison
    _lock: threading.Lock = field(
        default_factory=threading.Lock, repr=False, compare=False
    )
    _last_tick: float = field(
        default_factory=time.time, repr=False, compare=False
    )
    _last_status: str = field(default="", repr=False, compare=False)

    def tick(self, status: str) -> None:
        """Call once per frame with the current posture status string."""
        with self._lock:
            now = time.time()
            dt = now - self._last_tick
            self._last_tick = now
            if self._last_status == "GOOD":
                self.good_seconds += dt
            elif self._last_status == "POOR":
                self.poor_seconds += dt
            else:
                self.away_seconds += dt
            self._last_status = status

    def record_alert(self) -> None:
        """Increment the alert counter (call whenever a beep is fired)."""
        with self._lock:
            self.alert_count += 1

    def summary(self) -> dict:
        """Return a snapshot summary dict suitable for display or logging."""
        with self._lock:
            total = self.good_seconds + self.poor_seconds + self.away_seconds
            return {
                "good_pct": round(100 * self.good_seconds / total, 1) if total else 0.0,
                "poor_pct": round(100 * self.poor_seconds / total, 1) if total else 0.0,
                "alerts": self.alert_count,
                "total_min": round(total / 60, 1),
            }
