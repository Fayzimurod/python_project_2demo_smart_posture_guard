import cv2
import mediapipe as mp
# Явный импорт подмодулей для устранения ошибки AttributeError
import mediapipe.python.solutions.pose as mp_pose
import mediapipe.python.solutions.drawing_utils as mp_drawing

class PoseDetector:
    def __init__(self, min_detection_confidence=0.6, min_tracking_confidence=0.6):
        self.mp_pose = mp_pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp_drawing

    def find_pose(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.pose.process(img_rgb)
        
        landmarks = {}
        if results.pose_landmarks:
            if draw:
                self.mp_draw.draw_landmarks(
                    img, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                )
            
            h, w, _ = img.shape
            for idx, lm in enumerate(results.pose_landmarks.landmark):
                landmarks[idx] = (int(lm.x * w), int(lm.y * h), lm.z)
                
        return img, landmarks
        