from dataclasses import dataclass, field
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import time

@dataclass
class SessionStats:
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = None
    alert_count: int = 0
    away_from_camera_seconds: float = 0.0
    locked_sec: float = 0.0
    unlocked_sec: float = 0.0
    _last_time: float = field(default_factory=time.perf_counter, init=False, repr=False)

    # Updates every frame with the stats.
    def update_stats(self, dt, face_detected, gaze_not_locked, head_not_locked): 
        if not face_detected:
            self.away_from_camera_seconds += dt
        if gaze_not_locked:
            self.unlocked_sec += dt
        else:
            self.locked_sec += dt

    def set_end_time_now(self):
        self.end_time = datetime.now()
    
    # reset button for stats
    def reset_stats(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.alert_count = 0
        self.away_from_camera_seconds = 0.0
        self.locked_sec = 0.0
        self.unlocked_sec = 0.0
    
    def frame_update(self, face_detected, gaze_not_locked, head_not_locked):
        now = time.perf_counter()
        dt = now - self._last_time
        self._last_time = now
        self.update_stats(dt, face_detected, gaze_not_locked, head_not_locked)
    
    def record_alert(self):
        self.alert_count += 1

    def handle_key(self, key):
        if key == ord('s'):
            self.end_time = datetime.now() 
            self.stats_popup()

    # stats window popup
    def stats_popup(self):
        if not self.end_time:
            self.end_time = datetime.now()
        total_time = (self.end_time - self.start_time).total_seconds() if self.end_time else 0

        # Ensure a root window exists for Tkinter
        root = None
        try:
            root = tk._default_root
        except Exception:
            root = None
        if not root:
            root = tk.Tk()
            root.withdraw()  # Hide the root window
        window = tk.Toplevel(root)
        window.title("Session Stats")
        window.geometry("400x500")
        window.resizable(False, False)

        # Stats summary
        stats_message = (
            f"Session Duration: {total_time:.2f} seconds\n"
            f"Total Alerts: {self.alert_count}\n"
            f"Time Away from Camera: {self.away_from_camera_seconds:.2f} seconds\n"
            f"Time Unlocked: {self.unlocked_sec:.2f} seconds\n"
            f"Time Locked: {self.locked_sec:.2f} seconds"
        )
        tk.Label(window, text=stats_message, justify="left", font=("Arial", 11)).pack(pady=10)

        # buttons
        btn_frame = tk.Frame(window)
        btn_frame.pack(pady=10)
        def do_reset():
            self.reset_stats()
            window.destroy()
            messagebox.showinfo("Stats Reset", "Session stats resetted.")
        tk.Button(btn_frame, text="Reset Stats", command=do_reset, bg="#f0ad4e").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Close", command=window.destroy, bg="#5bc0de").pack(side="left", padx=10)

        # Run the popup's event loop and pause OpenCV until closed
        window.grab_set()  # Make popup modal
        window.wait_window()  # Pause until closed
