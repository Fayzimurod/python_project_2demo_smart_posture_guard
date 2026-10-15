import math

class PostureAnalyzer:
    def __init__(self):
        # Индексы MediaPipe Pose:
        # 0 - нос, 11 - левое плечо, 12 - правое плечо, 7 - левое ухо, 8 - правое ухо
        self.NOSE = 0
        self.L_EAR = 7
        self.R_EAR = 8
        self.L_SHOULDER = 11
        self.R_SHOULDER = 12

    def _calculate_angle(self, p1, p2):
        """Вычисляет угол наклона линии между двумя точками относительно горизонтали."""
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        return abs(angle)

    def analyze(self, landmarks):
        if not landmarks or self.L_SHOULDER not in landmarks or self.R_SHOULDER not in landmarks:
            return {"present": False, "status": "NO_PERSON", "details": {}}

        l_sh = landmarks[self.L_SHOULDER]
        r_sh = landmarks[self.R_SHOULDER]
        l_ear = landmarks.get(self.L_EAR)
        r_ear = landmarks.get(self.R_EAR)
        nose = landmarks.get(self.NOSE)

        # 1. Расстояние между плечами (прокси для близости к экрану)
        shoulder_width = math.hypot(l_sh[0] - r_sh[0], l_sh[1] - r_sh[1])

        # 2. Перекос плеч (наклон)
        shoulder_tilt = self._calculate_angle(l_sh, r_sh)

        # 3. Наклон головы / сутулость (вертикальное смещение ушей относительно плеч)
        bad_posture = False
        if l_ear and r_ear:
            avg_ear_y = (l_ear[1] + r_ear[1]) / 2
            avg_shoulder_y = (l_sh[1] + r_sh[1]) / 2
            neck_distance = avg_shoulder_y - avg_ear_y

            # Если расстояние слишком мало — голова опущена / человек сутулится
            if neck_distance < shoulder_width * 0.35:
                bad_posture = True

        if shoulder_tilt > 12.0:
            bad_posture = True

        status = "POOR" if bad_posture else "GOOD"

        return {
            "present": True,
            "status": status,
            "details": {
                "shoulder_width": round(shoulder_width, 1),
                "shoulder_tilt": round(shoulder_tilt, 1)
            }
        }
        