import os
import sys
import subprocess
import win32gui
import win32con
import win32process
import winreg  # For Task Manager registry modification

# Ensure parent directory (project root) is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from python_ui.main_ui import run_exam_ui
from Registration.login import show_login

KIOSK_EXECUTABLE = os.path.join(project_root, "system_controls", "main.exe")
KIOSK_TIME_LIMIT_MIN = 2  # Adjust or make dynamic if needed

kiosk_process = None  # Global reference


def stop_kiosk_process(score=None, total=None):
    global kiosk_process
    if kiosk_process and kiosk_process.poll() is None:
        try:
            pid = kiosk_process.pid

            def enum_handler(hwnd, hwnds):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    hwnds.append(hwnd)
                return True

            hwnds = []
            win32gui.EnumWindows(enum_handler, hwnds)

            if hwnds:
                for hwnd in hwnds:
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    print(f"[INFO] Sent WM_CLOSE to HWND: {hwnd}")
            else:
                print("[WARNING] No HWNDs found. Attempting forced termination.")

            kiosk_process.wait(timeout=5)

        except Exception as e:
            print(f"[ERROR] Graceful shutdown failed: {e}")
            try:
                kiosk_process.terminate()
                kiosk_process.wait()
            except Exception as e2:
                print(f"[ERROR] Forced termination also failed: {e2}")

        print("[INFO] Kiosk process terminated.")
    else:
        print("[INFO] Kiosk process not running or already exited.")


def start_exam(student_info):
    global kiosk_process
    try:
        kiosk_process = subprocess.Popen([KIOSK_EXECUTABLE, str(KIOSK_TIME_LIMIT_MIN)])
        print(f"[INFO] Kiosk process started (PID: {kiosk_process.pid})")
        run_exam_ui(student_info, on_submit_callback=stop_kiosk_process)
    except Exception as e:
        print(f"[ERROR] Failed to start kiosk process: {e}")
        stop_kiosk_process()


if __name__ == "__main__":
    show_login(start_exam)
