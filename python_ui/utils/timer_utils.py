# python_ui/utils/timer_utils.py

import threading
import time

class ExamTimer:
    def __init__(self, duration_minutes, update_callback=None, end_callback=None):
        """
        Initializes the timer.
        :param duration_minutes: Duration of the exam in minutes
        :param update_callback: Function to call every second with remaining time
        :param end_callback: Function to call when time is up
        """
        self.total_seconds = duration_minutes * 60
        self.update_callback = update_callback
        self.end_callback = end_callback
        self._running = False
        self._thread = None

    def _run_timer(self):
        remaining = self.total_seconds
        while self._running and remaining > 0:
            mins, secs = divmod(remaining, 60)
            if self.update_callback:
                self.update_callback(f"{mins:02d}:{secs:02d}")
            time.sleep(1)
            remaining -= 1

        if self._running:
            if self.end_callback:
                self.end_callback()
        self._running = False

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run_timer)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()

# Example usage for testing
if __name__ == "__main__":
    def on_update(time_str):
        print("⏱️ Time left:", time_str)

    def on_end():
        print("✅ Time's up! Submit the exam.")

    timer = ExamTimer(duration_minutes=1, update_callback=on_update, end_callback=on_end)
    timer.start()
