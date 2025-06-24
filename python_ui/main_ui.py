import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QRadioButton, QVBoxLayout,
    QHBoxLayout, QButtonGroup, QGroupBox, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QFont


class ExamWindow(QWidget):
    def __init__(self, student_info, on_submit_callback=None):
        super().__init__()
        self.setWindowTitle("Examination Portal")
        self.showFullScreen()

        # Force window focus and raise
        self.raise_()
        self.activateWindow()
        self.setFocus()

        self.total_exam_minutes = 2
        self.remaining_time = QTime(0, self.total_exam_minutes, 0)

        self.current_question = 0
        self.user_info = student_info
        self.questions = [
            {"question": "What is the capital of France?", "options": ["Berlin", "Madrid", "Paris", "Rome"], "answer": 2},
            {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "answer": 1},
            {"question": "Which planet is known as the Red Planet?", "options": ["Earth", "Mars", "Jupiter", "Saturn"], "answer": 1}
        ]
        self.selected_answers = [None] * len(self.questions)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.on_submit_callback = on_submit_callback

        self.initUI()

    def initUI(self):
        outer_layout = QVBoxLayout()

        # === Title ===
        title = QLabel("📘 Final Semester Examination")
        title.setFont(QFont('Arial', 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white; background-color: #003366; padding: 20px;")
        outer_layout.addWidget(title)

        # === Timer ===
        self.timer_label = QLabel("Time Left:")
        self.timer_label.setFont(QFont('Arial', 18))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("margin: 10px;")
        outer_layout.addWidget(self.timer_label)

        # === Main Layout ===
        main_layout = QHBoxLayout()

        # LEFT PANEL
        self.question_panel = QVBoxLayout()
        self.question_panel.setSpacing(6)  # minimal spacing

        # Question Label
        self.question_label = QLabel()
        self.question_label.setFont(QFont('Arial', 14))
        self.question_label.setWordWrap(True)
        self.question_label.setMaximumHeight(60)
        self.question_label.setAlignment(Qt.AlignTop)
        self.question_label.setStyleSheet("margin: 0px; padding: 0px;")

        # Options Box
        self.radio_group = QButtonGroup(self)
        self.options_box = QGroupBox()
        self.options_box.setFont(QFont('Arial', 16))
        self.options_box.setContentsMargins(0, 0, 0, 0)
        self.options_box.setMaximumHeight(170)

        self.options_layout = QVBoxLayout()
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.options_layout.setSpacing(2)
        self.options_box.setLayout(self.options_layout)

        # Combine Question and Options
        question_area = QVBoxLayout()
        question_area.setSpacing(4)
        question_area.addWidget(self.question_label)
        question_area.addWidget(self.options_box)

        self.question_panel.addLayout(question_area)

        # Navigation Buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.setFont(QFont('Arial', 14))
        self.prev_btn.clicked.connect(self.prev_question)

        self.next_btn = QPushButton("Next →")
        self.next_btn.setFont(QFont('Arial', 14))
        self.next_btn.clicked.connect(self.next_question)

        self.submit_btn = QPushButton("Submit Exam")
        self.submit_btn.setFont(QFont('Arial', 14))
        self.submit_btn.clicked.connect(self.submit_exam)
        self.submit_btn.setVisible(False)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.submit_btn)
        self.question_panel.addLayout(nav_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #888888;")

        # RIGHT PANEL
        right_panel = QVBoxLayout()

        user_info_label = QLabel(f"👤 {self.user_info['name']}\n🆔 Reg: {self.user_info['reg_no']}")
        user_info_label.setFont(QFont('Arial', 14))
        user_info_label.setAlignment(Qt.AlignTop)
        user_info_label.setStyleSheet("margin: 20px;")
        right_panel.addWidget(user_info_label)

        self.grid_layout = QGridLayout()
        self.grid_buttons = []

        for i in range(len(self.questions)):
            btn = QPushButton(str(i + 1))
            btn.setFont(QFont('Arial', 12))
            btn.setFixedSize(40, 40)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, index=i: self.go_to_question(index))
            self.grid_buttons.append(btn)
            self.grid_layout.addWidget(btn, i // 3, i % 3)

        right_panel.addLayout(self.grid_layout)
        right_panel.addStretch(1)

        main_layout.addLayout(self.question_panel, stretch=8)
        main_layout.addWidget(line)
        main_layout.addLayout(right_panel, stretch=2)

        outer_layout.addLayout(main_layout)
        self.setLayout(outer_layout)

        self.load_question()

    def update_timer(self):
        self.remaining_time = self.remaining_time.addSecs(-1)
        self.timer_label.setText(f"⏱ Time Left: {self.remaining_time.toString('mm:ss')}")
        if self.remaining_time == QTime(0, 0, 0):
            self.timer.stop()
            self.submit_exam()

    def load_question(self):
        question = self.questions[self.current_question]
        self.question_label.setText(f"Q{self.current_question + 1}: {question['question']}")

        # Clear previous options
        for btn in self.radio_group.buttons():
            self.radio_group.removeButton(btn)
            btn.deleteLater()

        for i, opt in enumerate(question["options"]):
            radio = QRadioButton(opt)
            radio.setFont(QFont("Arial", 12))
            radio.setStyleSheet("margin-top: 0px; margin-bottom: 2px; padding: 0px;")
            radio.toggled.connect(self.option_selected)
            self.radio_group.addButton(radio, i)
            self.options_layout.addWidget(radio)

        selected = self.selected_answers[self.current_question]
        if selected is not None and self.radio_group.button(selected) is not None:
            self.radio_group.button(selected).setChecked(True)

        self.prev_btn.setEnabled(self.current_question > 0)
        self.next_btn.setVisible(self.current_question < len(self.questions) - 1)
        self.submit_btn.setVisible(self.current_question == len(self.questions) - 1)

        self.update_answer_grid()

    def save_answer(self):
        selected_id = self.radio_group.checkedId()
        if selected_id != -1:
            self.selected_answers[self.current_question] = selected_id

    def option_selected(self):
        self.save_answer()
        self.update_answer_grid()

    def next_question(self):
        self.save_answer()
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.load_question()

    def prev_question(self):
        self.save_answer()
        if self.current_question > 0:
            self.current_question -= 1
            self.load_question()

    def go_to_question(self, index):
        self.save_answer()
        self.current_question = index
        self.load_question()

    def update_answer_grid(self):
        for i, btn in enumerate(self.grid_buttons):
            if self.selected_answers[i] is not None:
                btn.setStyleSheet("background-color: #90EE90; color: white;")
            else:
                btn.setStyleSheet("")

    def submit_exam(self):
        self.save_answer()
        score = 0
        for i, q in enumerate(self.questions):
            if self.selected_answers[i] == q['answer']:
                score += 1
        total = len(self.questions)

        self.question_label.setText(f"✔ Exam Submitted!\nScore: {score}/{total}")
        self.options_box.hide()
        self.prev_btn.hide()
        self.next_btn.hide()
        self.submit_btn.hide()
        self.timer_label.hide()

        if self.on_submit_callback:
            self.on_submit_callback(score, total)


def run_exam_ui(student_info, on_submit_callback=None):
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = ExamWindow(student_info, on_submit_callback)
    window.showFullScreen()
    window.raise_()
    window.activateWindow()
    window.setFocus()
    
    # Do NOT call sys.exit() — just exec if you created the QApplication
    if QApplication.instance() == app:
        app.exec_()

