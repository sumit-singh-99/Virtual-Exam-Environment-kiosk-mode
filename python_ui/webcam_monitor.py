# python_ui/webcam_monitor.py

import cv2
import datetime

# Load Haar cascade
face_cascade = cv2.CascadeClassifier("Registration/haarcascades/haarcascades_frontalface_default.xml")

def monitor_webcam(duration=10, output_log="reports/suspicious_activity_report.csv"):
    cap = cv2.VideoCapture(0)
    start_time = datetime.datetime.now()

    print("📹 Webcam monitoring started...")

    while (datetime.datetime.now() - start_time).seconds < duration:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) > 1:
            print("⚠️  Multiple faces detected!")
            log_suspicious_activity(output_log)

    cap.release()
    cv2.destroyAllWindows()

def log_suspicious_activity(log_path):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a") as f:
        f.write(f"{timestamp},Multiple faces detected\n")


if __name__ == "__main__":
    monitor_webcam(duration=10)  # Run for 10 seconds as a test
