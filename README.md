# 🧍 Smart Posture Guard

Real-time webcam posture monitor powered by **MediaPipe Pose** + **OpenCV**.  
Detects slouching and asymmetric shoulder tilt, fires an audible alert, and tracks session statistics — all locally, with zero data leaving your machine.

---

## Architecture

```
smart_posture_guard/
├── config.py      ← All thresholds & constants (edit here, not in code)
├── detector.py    ← PoseDetector — MediaPipe wrapper with context manager & visibility filter
├── analyzer.py    ← PostureAnalyzer — geometry checks + deque smoothing (majority vote)
├── notifier.py    ← AlertNotifier — threaded winsound beep with cooldown
├── stats.py       ← SessionStats — thread-safe per-status time accumulator
├── ui.py          ← draw_status_panel() — all cv2 HUD drawing in one place
├── main.py        ← Thin orchestrator: camera loop, keyboard, try/finally cleanup
├── requirements.txt
├── run.bat        ← One-click launcher (portable Python, auto-installs deps)
└── index.html     ← Personal manifesto page (unrelated to the app)
```

### Data Flow

```
Camera → PoseDetector → PostureAnalyzer → AlertNotifier
                    ↓               ↓             ↓
               landmarks       PostureResult   beep()
                    ↓               ↓
                  ui.py ← SessionStats.tick()
                    ↓
               cv2.imshow()
```

---

## Quick Start

### Option A — One-click (Windows, no Python required)
```
run.bat
```
Downloads a portable Python 3.11, installs dependencies, and launches the app automatically.

### Option B — System Python
```bash
pip install -r requirements.txt
python main.py
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit and print session summary |
| `s` | Print session summary to stdout (while running) |

---

## HUD Overlay

```
┌─────────────────────────────────────────┐  FPS: 28
│  Posture: GOOD                          │
│  Shoulder tilt :  3.2 deg              │
│  Neck ratio    : 0.412 (min 0.35)      │
│  Confidence    : 100%                   │
└─────────────────────────────────────────┘

[Session 4.2 min  |  Good 78.0%  Poor 12.0%  |  Alerts: 1]
```

- **Red border flash** — critical alert (slouching > 3 seconds)
- **Yellow** — POOR posture (within grace period)
- **Green** — GOOD posture
- **Gray** — person not detected (AWAY)

---

## Configuration (`config.py`)

| Constant | Default | Description |
|---|---|---|
| `CAMERA_INDEX` | `0` | Webcam index |
| `FRAME_WIDTH/HEIGHT` | `1280×720` | Capture resolution |
| `MIN_DETECTION_CONF` | `0.65` | MediaPipe detection confidence |
| `MIN_TRACKING_CONF` | `0.65` | MediaPipe tracking confidence |
| `MIN_VISIBILITY` | `0.50` | Landmarks below this are ignored |
| `SHOULDER_TILT_THRESHOLD` | `12.0°` | Max allowed shoulder asymmetry |
| `NECK_RATIO_THRESHOLD` | `0.35` | Min ear-shoulder distance / shoulder width |
| `SMOOTHING_WINDOW` | `8` | Frames for majority-vote smoothing |
| `BAD_POSTURE_GRACE_PERIOD` | `3.0 s` | Seconds before alert fires |
| `ALERT_COOLDOWN` | `10.0 s` | Min seconds between beeps |

---

## Security & Privacy

- **Zero network access** — no frames, no landmarks, no telemetry ever leave the process
- **No disk writes** — frames are processed in RAM only
- All OS resources (camera, MediaPipe graph) released in `finally` blocks
- Landmark data validated before processing; low-visibility landmarks filtered out
- No external URLs or secrets in Python code

---

## Requirements

- Python ≥ 3.10
- opencv-python ≥ 4.8.0
- mediapipe ≥ 0.10.14
- numpy ≥ 1.24.0
- Webcam
- Windows (for `winsound` beep; ASCII bell fallback on other platforms)
