import sys
import sqlite3
import subprocess
import cv2
import numpy as np
import os
import face_recognition
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame, QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

DB_PATH = os.path.join(os.path.dirname(__file__), "students.db")
HAAR_CASCADE_FACE = os.path.join(os.path.dirname(__file__), "haarcascades/haarcascade_frontalface_default.xml")

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def verify_credentials(reg_no, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE reg_no = ? AND password = ?", (reg_no, password))
    user = cursor.fetchone()
    conn.close()
    return user

def recognize_face(reg_no):
    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_FACE)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        QMessageBox.critical(None, "Error", "Webcam not detected!")
        return False

    recognized = False
    match_threshold = 0.38

    face_data_path = os.path.join(os.path.dirname(__file__), "face_data", reg_no)
    if not os.path.exists(face_data_path):
        QMessageBox.critical(None, "Error", f"No face data found for Registration No: {reg_no}")
        cap.release()
        return False

    known_encodings = []
    for filename in os.listdir(face_data_path):
        img_path = os.path.join(face_data_path, filename)
        img = cv2.imread(img_path)
        if img is not None:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(img_rgb)
            if encodings:
                known_encodings.append(encodings[0])

    if not known_encodings:
        QMessageBox.critical(None, "Error", "No valid face images found!")
        cap.release()
        return False

    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding in face_encodings:
            face_distances = face_recognition.face_distance(known_encodings, encoding)
            best_distance = np.min(face_distances)
            if best_distance < match_threshold:
                recognized = True
                break

        cv2.imshow("Face Recognition", frame)
        if recognized or cv2.waitKey(1) & 0xFF == ord('q') or time.time() - start_time > 8:
            break

    cap.release()
    cv2.destroyAllWindows()

    if not recognized:
        QMessageBox.warning(None, "Face Not Recognized", "Face didn't match.")
    return recognized

def show_login(callback_on_success):
    class LoginWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.init_ui()

        def init_ui(self):
            self.setWindowTitle("Exam Portal Login")
            self.setMinimumSize(1100, 650)
            self.setStyleSheet("background-color: #f3f4f6;")

            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(40, 30, 40, 30)

            center_layout = QHBoxLayout()
            center_layout.setAlignment(Qt.AlignCenter)

            content_frame = QFrame()
            content_frame.setMaximumWidth(1000)
            content_frame.setMinimumHeight(550)
            content_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 12px;
                }
            """)
            content_layout = QHBoxLayout(content_frame)
            content_layout.setContentsMargins(0, 0, 0, 0)

            # Instructions Panel
            instructions_panel = QFrame()
            instructions_panel.setMinimumWidth(400)
            instructions_panel.setStyleSheet("""
                background-color: #2563eb;
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            """)
            instructions_layout = QVBoxLayout(instructions_panel)
            instructions_layout.setContentsMargins(30, 25, 30, 25)

            title = QLabel("📝 Exam Instructions")
            title.setFont(QFont("Arial", 18, QFont.Bold))
            title.setStyleSheet("color: white;")
            instructions_layout.addWidget(title)

            instructions = [
                "Login using your student ID and access key.",
                "Ensure your webcam and internet are working properly.",
                "Avoid switching tabs or minimizing the screen.",
                "Do not refresh or exit during the exam.",
                "You will have 120 minutes to complete the test."
            ]

            for instr in instructions:
                label = QLabel(f"• {instr}")
                label.setWordWrap(True)
                label.setStyleSheet("color: white; font-size: 13px; margin-top: 10px;")
                instructions_layout.addWidget(label)

            instructions_layout.addStretch()
            support = QLabel("Need help?\nsupport@examportal.edu")
            support.setStyleSheet("color: white; font-size: 11px; font-style: italic;")
            instructions_layout.addWidget(support)

            # Login Panel
            login_panel = QFrame()
            login_panel.setStyleSheet("""
                background-color: white;
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            """)
            login_layout = QVBoxLayout(login_panel)
            login_layout.setContentsMargins(40, 30, 40, 30)

            heading_icon = QLabel("📘")
            heading_icon.setFont(QFont("Arial", 36))
            heading_icon.setAlignment(Qt.AlignHCenter)
            login_layout.addWidget(heading_icon)

            heading = QLabel("Exam Portal")
            heading.setFont(QFont("Arial", 22, QFont.Bold))
            heading.setAlignment(Qt.AlignHCenter)
            login_layout.addWidget(heading)

            subtext = QLabel("Please login to access your exam")
            subtext.setStyleSheet("color: gray; font-size: 13px;")
            subtext.setAlignment(Qt.AlignHCenter)
            login_layout.addWidget(subtext)

            login_layout.addSpacing(10)

            self.reg_input = self.create_form_input("Student ID")
            self.pass_input = self.create_form_input("Access Key", is_password=True)

            login_layout.addWidget(self.reg_input[0])
            login_layout.addWidget(self.pass_input[0])

            login_btn = QPushButton("Login & Start Exam")
            login_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                    padding: 10px;
                    font-weight: bold;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #1e40af;
                }
            """)
            login_btn.clicked.connect(self.handle_login)
            login_layout.addWidget(login_btn)

            # Register link
            register_link = QLabel('<a href="#">Not registered? Register here.</a>')
            register_link.setAlignment(Qt.AlignHCenter)
            register_link.setStyleSheet("font-size: 11px; margin-top: 6px;")
            register_link.setOpenExternalLinks(False)
            register_link.linkActivated.connect(self.open_register_window)
            login_layout.addWidget(register_link)


            help = QLabel("Having trouble logging in? Get Help")
            help.setAlignment(Qt.AlignHCenter)
            help.setStyleSheet("color: #2563eb; font-size: 11px; margin-top: 10px;")
            login_layout.addWidget(help)
            login_layout.addStretch()

            content_layout.addWidget(instructions_panel)
            content_layout.addWidget(login_panel)

            center_layout.addWidget(content_frame)
            main_layout.addLayout(center_layout)

        def open_register_window(self):
            register_script = os.path.join(os.path.dirname(__file__), "register.py")
            try:
                subprocess.Popen(["python", register_script])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open registration window:\n{str(e)}")

        def create_form_input(self, label_text, is_password=False):
            container = QVBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            input_field = QLineEdit()
            if is_password:
                input_field.setEchoMode(QLineEdit.Password)
            input_field.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 5px;")
            container.addWidget(label)
            container.addWidget(input_field)
            frame = QFrame()
            frame.setLayout(container)
            return frame, input_field

        def handle_login(self):
            reg_no = self.reg_input[1].text().strip()
            password = self.pass_input[1].text().strip()

            if not reg_no or not password:
                QMessageBox.critical(self, "Error", "Please enter both Student ID and Access Key.")
                return

            user = verify_credentials(reg_no, password)
            if not user:
                QMessageBox.critical(self, "Error", "Invalid Student ID or Password.")
                return

            QMessageBox.information(self, "Info", "Credentials verified! Now verifying face...")
            if recognize_face(reg_no):
                QMessageBox.information(self, "Success", "Login Successful!")
                self.close()
                callback_on_success({"reg_no": user[1], "name": user[2]})
            else:
                QMessageBox.critical(self, "Error", "Face Authentication Failed!")

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.showMaximized()
    app.exec_()
