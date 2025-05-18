# integration/exam_submission.py

import random

def submit_exam(student_id):
    """
    Simulate exam evaluation and return a score.

    Args:
        student_id (str): ID of the student submitting the exam

    Returns:
        int: A randomly generated exam score (for testing purposes)
    """
    print(f"[INFO] Submitting exam for: {student_id}")

    # For now, we simulate grading with a random score
    score = random.randint(60, 100)
    print(f"[INFO] Assigned score: {score}")

    # You can add more logic here to evaluate real answers in future
    return score
