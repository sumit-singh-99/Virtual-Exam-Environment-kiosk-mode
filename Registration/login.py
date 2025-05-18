import sqlite3
import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
import os
import face_recognition
import time

DB_PATH = os.path.join(os.path.dirname(__file__), "students.db")  # Ensure dynamic path
HAAR_CASCADE_FACE = os.path.join(os.path.dirname(__file__), "haarcascades/haarcascade_frontalface_default.xml")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

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
        messagebox.showerror("Error", "Webcam not detected!")
        return False

    recognized = False
    match_threshold = 0.38

    face_data_path = os.path.join(os.path.dirname(__file__), "face_data", reg_no)

    if not os.path.exists(face_data_path):
        messagebox.showerror("Error", f"No face data found for Registration No: {reg_no}")
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
        messagebox.showerror("Error", "No valid face images found!")
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

        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            face_distances = face_recognition.face_distance(known_encodings, encoding)
            best_distance = np.min(face_distances)

            if best_distance < match_threshold:
                recognized = True
                break

        cv2.imshow("Face Recognition", frame)
        if recognized or cv2.waitKey(1) & 0xFF == ord('q') or time.time() - start_time > 20:
            break

    cap.release()
    cv2.destroyAllWindows()

    if not recognized:
        messagebox.showwarning("Face Not Recognized", "Face didn't match.")
    return recognized

def show_login(callback_on_success):
    def login():
        reg_no = entry_regno.get().strip()
        password = entry_password.get().strip()

        if not reg_no or not password:
            messagebox.showerror("Error", "Please enter both Registration No. and Password.")
            return

        user = verify_credentials(reg_no, password)
        if not user:
            messagebox.showerror("Error", "Invalid Registration No. or Password.")
            return

        messagebox.showinfo("Info", "Credentials verified! Now verifying face...")

        if recognize_face(reg_no):
            messagebox.showinfo("Success", "Login Successful!")
            root.destroy()
            callback_on_success({"reg_no": user[0], "name": user[1]})
        else:
            messagebox.showerror("Error", "Face Authentication Failed!")

    root = tk.Tk()
    root.title("Student Login")
    root.geometry("400x300")

    tk.Label(root, text="Student Login", font=("Helvetica", 18, "bold")).pack(pady=20)
    tk.Label(root, text="Registration No:", font=("Helvetica", 12)).pack()
    entry_regno = tk.Entry(root, font=("Helvetica", 12))
    entry_regno.pack(pady=5)
    tk.Label(root, text="Password:", font=("Helvetica", 12)).pack()
    entry_password = tk.Entry(root, font=("Helvetica", 12), show="*")
    entry_password.pack(pady=5)

    tk.Button(root, text="Login", font=("Helvetica", 12), bg="#4CAF50", fg="white", width=15, command=login).pack(pady=20)
    root.mainloop()
