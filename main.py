import cv2
import time
from detector import PoseDetector
from analyzer import PostureAnalyzer

def main():
    cap = cv2.VideoCapture(0)
    
    # Настройки разрешения
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = PoseDetector()
    analyzer = PostureAnalyzer()

    bad_posture_start = None
    alert_triggered = False
    
    print("[INFO] Запуск системы мониторинга. Нажмите 'q' для выхода.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("[ERROR] Не удалось получить кадр с веб-камеры.")
            break

        # Отражаем кадр для эффекта зеркала
        frame = cv2.flip(frame, 1)
        
        # Детекция и анализ
        frame, landmarks = detector.find_pose(frame, draw=True)
        result = analyzer.analyze(landmarks)

        # Логика предупреждений
        if result["present"]:
            if result["status"] == "POOR":
                if bad_posture_start is None:
                    bad_posture_start = time.time()
                else:
                    elapsed = time.time() - bad_posture_start
                    if elapsed > 3.0:  # Если сутулость длится более 3 секунд
                        alert_triggered = True
            else:
                bad_posture_start = None
                alert_triggered = False

            # Отрисовка UI
            color = (0, 0, 255) if alert_triggered else ((0, 255, 255) if result["status"] == "POOR" else (0, 255, 0))
            status_text = "CRITICAL: SLOUCHING!" if alert_triggered else f"Posture: {result['status']}"

            cv2.rectangle(frame, (20, 20), (450, 120), (30, 30, 30), -1)
            cv2.putText(frame, status_text, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            
            if "shoulder_tilt" in result["details"]:
                tilt_text = f"Tilt: {result['details']['shoulder_tilt']} deg"
                cv2.putText(frame, tilt_text, (30, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        else:
            bad_posture_start = None
            alert_triggered = False
            cv2.rectangle(frame, (20, 20), (350, 80), (30, 30, 30), -1)
            cv2.putText(frame, "Status: AWAY", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (128, 128, 128), 2)

        cv2.imshow("Smart Workspace Guard", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
