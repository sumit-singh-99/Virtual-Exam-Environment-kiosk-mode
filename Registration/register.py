import sys
import os
import sqlite3
import uuid
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
                             QComboBox, QSpinBox, QTextEdit, QCheckBox, 
                             QPushButton, QMessageBox, QDialog, QGroupBox,
                             QGridLayout, QFrame, QSizePolicy, QScrollArea)
from PyQt5.QtGui import QFont, QPixmap, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp

DB_PATH = "students.db"
BASE_FACE_DATA_DIR = "face_data/"

class SuccessDialog(QDialog):
    def __init__(self, reg_no, password, parent=None):
        super().__init__(parent)
        self.reg_no = reg_no
        self.password = password
        self.setWindowTitle("Registration Successful")
        self.setFixedSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        icon_label = QLabel()
        pixmap = QPixmap(":/icons/success.png")
        if pixmap.isNull():
            icon_label.setText("✓")
            icon_label.setStyleSheet("font-size: 48px; color: #10B981;")
        else:
            icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        title = QLabel("Registration Successful!")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #111827;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        cred_frame = QFrame()
        cred_frame.setFrameShape(QFrame.StyledPanel)
        cred_frame.setStyleSheet("background-color: #F9FAFB; border-radius: 8px;")
        cred_layout = QFormLayout(cred_frame)
        cred_layout.setContentsMargins(20, 15, 20, 15)

        reg_label = QLabel("Registration Number:")
        reg_value = QLabel(self.reg_no)
        reg_value.setStyleSheet("font-weight: bold;")

        pass_label = QLabel("Password:")
        pass_value = QLabel(self.password)
        pass_value.setStyleSheet("font-weight: bold;")

        cred_layout.addRow(reg_label, reg_value)
        cred_layout.addRow(pass_label, pass_value)
        layout.addWidget(cred_frame)

        note = QLabel("Please save these credentials for future login.")
        note.setStyleSheet("color: #6B7280; font-size: 12px;")
        note.setAlignment(Qt.AlignCenter)
        layout.addWidget(note)

        self.capture_btn = QPushButton("Start Face Capture")
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        self.capture_btn.clicked.connect(self.accept)
        layout.addWidget(self.capture_btn)

        layout.setSpacing(15)
        self.setLayout(layout)

class StudentRegistrationForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Registration")
        self.setMinimumSize(800, 600)
        self.showMaximized()
        self.setup_ui()
        self.setup_db()

    def setup_db(self):
        os.makedirs(BASE_FACE_DATA_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reg_no TEXT UNIQUE,
                name TEXT NOT NULL,
                father_name TEXT NOT NULL,
                aadhaar TEXT UNIQUE,
                phone TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                program TEXT,
                face_data_dir TEXT,
                password TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def setup_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F3F4F6;
            }
            QLabel {
                color: #374151;
            }
            QLineEdit, QComboBox, QSpinBox, QTextEdit {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid #3B82F6;
            }
            QPushButton {
                border-radius: 6px;
                padding: 10px 15px;
            }
        """)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #1D4ED8);
                border-radius: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        icon_label = QLabel("👤")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background-color: white; border-radius: 20px; padding: 5px;")
        header_text = QVBoxLayout()
        title = QLabel("Student Registration")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        subtitle = QLabel("Complete the form to register and capture face data")
        subtitle.setStyleSheet("color: #BFDBFE; font-size: 12px;")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_layout.addWidget(icon_label)
        header_layout.addLayout(header_text)
        header_layout.addStretch()
        main_layout.addWidget(header_frame)

        # Scrollable form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        form_container = QFrame()
        form_container.setStyleSheet("QFrame { background-color: white; border-radius: 10px; }")
        form_layout = QVBoxLayout(form_container)

        personal_group = QGroupBox("Personal Details")
        personal_layout = QGridLayout()

        self.name_input = QLineEdit()
        self.father_input = QLineEdit()
        self.aadhaar_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.age_input = QSpinBox()
        self.gender_input = QComboBox()
        self.program_input = QComboBox()

        self.name_input.setPlaceholderText("Enter your full name")
        self.father_input.setPlaceholderText("Enter your father's name")
        self.aadhaar_input.setPlaceholderText("XXXX XXXX XXXX")
        self.phone_input.setPlaceholderText("+91 XXXXX XXXXX")
        self.age_input.setRange(15, 100)
        self.age_input.setValue(18)
        self.gender_input.addItems(["Select", "Male", "Female", "Other"])
        self.program_input.addItems(["Select", "B.Tech", "BBA", "BCA", "MCA", "M.Tech"])

        # Validators
        aadhaar_regex = QRegExp("^[0-9]{4}\\s?[0-9]{4}\\s?[0-9]{4}$")
        phone_regex = QRegExp("^(\\+\\d{1,3}\\s?)?\\d{10}$")
        self.aadhaar_input.setValidator(QRegExpValidator(aadhaar_regex))
        self.phone_input.setValidator(QRegExpValidator(phone_regex))

        # Set max widths
        for widget in [self.name_input, self.father_input, self.aadhaar_input,
                       self.phone_input, self.gender_input, self.program_input]:
            widget.setMaximumWidth(400)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        personal_layout.addWidget(QLabel("Full Name:"), 0, 0)
        personal_layout.addWidget(self.name_input, 0, 1)
        personal_layout.addWidget(QLabel("Father's Name:"), 0, 2)
        personal_layout.addWidget(self.father_input, 0, 3)

        personal_layout.addWidget(QLabel("Aadhaar Number:"), 1, 0)
        personal_layout.addWidget(self.aadhaar_input, 1, 1)
        personal_layout.addWidget(QLabel("Phone Number:"), 1, 2)
        personal_layout.addWidget(self.phone_input, 1, 3)

        personal_layout.addWidget(QLabel("Age:"), 2, 0)
        personal_layout.addWidget(self.age_input, 2, 1)
        personal_layout.addWidget(QLabel("Gender:"), 2, 2)
        personal_layout.addWidget(self.gender_input, 2, 3)

        personal_layout.addWidget(QLabel("Program:"), 3, 0)
        personal_layout.addWidget(self.program_input, 3, 1)

        personal_group.setLayout(personal_layout)
        form_layout.addWidget(personal_group)

        self.terms_checkbox = QCheckBox("I agree to the terms and conditions")
        form_layout.addWidget(self.terms_checkbox)

        buttons_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Form")
        self.submit_btn = QPushButton("Register & Capture Face")

        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #D1D5DB;
                color: #4B5563;
            }
            QPushButton:hover {
                background-color: #F9FAFB;
            }
        """)

        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:disabled {
                background-color: #93C5FD;
            }
        """)

        self.clear_btn.clicked.connect(self.clear_form)
        self.submit_btn.clicked.connect(self.on_submit)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.submit_btn)

        form_layout.addLayout(buttons_layout)
        scroll_layout.addWidget(form_container)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        self.setCentralWidget(central_widget)

    def clear_form(self):
        self.name_input.clear()
        self.father_input.clear()
        self.aadhaar_input.clear()
        self.phone_input.clear()
        self.age_input.setValue(18)
        self.gender_input.setCurrentIndex(0)
        self.program_input.setCurrentIndex(0)
        self.terms_checkbox.setChecked(False)

    def generate_registration_number(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        while True:
            reg_no = "REG" + str(random.randint(1000000000, 9999999999))
            cursor.execute("SELECT COUNT(*) FROM students WHERE reg_no = ?", (reg_no,))
            if cursor.fetchone()[0] == 0:
                conn.close()
                return reg_no

    def generate_password(self):
        return str(uuid.uuid4())[:8]

    def save_to_db(self, data):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO students (reg_no, name, father_name, aadhaar, phone, age, gender, program,
                                      face_data_dir, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            QMessageBox.critical(self, "Database Error", f"Aadhaar or Registration Number already exists.\n{e}")
            return False
        finally:
            conn.close()

    def validate_form(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter your full name.")
            return False
        if not self.father_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter your father's name.")
            return False
        if not self.aadhaar_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter your Aadhaar number.")
            return False
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter your phone number.")
            return False
        if self.gender_input.currentText() == "Select":
            QMessageBox.warning(self, "Missing Information", "Please select your gender.")
            return False
        if self.program_input.currentText() == "Select":
            QMessageBox.warning(self, "Missing Information", "Please select your program.")
            return False
        if not self.terms_checkbox.isChecked():
            QMessageBox.warning(self, "Terms & Conditions", "Please agree to the terms and conditions.")
            return False
        return True

    def on_submit(self):
        if not self.validate_form():
            return
        reg_no = self.generate_registration_number()
        password = self.generate_password()
        face_data_path = os.path.join(BASE_FACE_DATA_DIR, reg_no)
        os.makedirs(face_data_path, exist_ok=True)

        data = (
            reg_no,
            self.name_input.text().strip(),
            self.father_input.text().strip(),
            self.aadhaar_input.text().strip().replace(" ", ""),
            self.phone_input.text().strip(),
            self.age_input.value(),
            self.gender_input.currentText(),
            self.program_input.currentText(),
            face_data_path,
            password
        )

        if self.save_to_db(data):
            dialog = SuccessDialog(reg_no, password, self)
            if dialog.exec_() == QDialog.Accepted:
                self.start_face_capture(reg_no)

    def start_face_capture(self, reg_no):
        try:
            import face_capture
            face_capture.start_face_capture(reg_no)
            self.close()
        except ImportError:
            QMessageBox.warning(self, "Module Error", "Face capture module not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start face capture: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")
    window = StudentRegistrationForm()
    sys.exit(app.exec_())
