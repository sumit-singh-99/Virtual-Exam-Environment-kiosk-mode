from main_ui import run_exam_ui

def dummy_submit_callback(score, total):
    print(f"Exam completed. Final Score: {score}/{total}")

if __name__ == "__main__":
    # Simulated student info as would be passed from login
    test_student_info = {
        "reg_no": "123456",
        "name": "Test Student"
    }

    run_exam_ui(test_student_info, on_submit_callback=dummy_submit_callback)
