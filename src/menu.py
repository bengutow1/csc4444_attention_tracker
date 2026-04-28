

#This file is for the settings menu
# Opens a tkinter window like we do in main with sliders with text entries for every editable parameter

import tkinter as tk

# reusable colors for making the menu
BG = "#1e1e1e"
FG = "white"

# each entry: (key, display label, min value, max value, slider step size)
# 'key' matches the attribute names on tracker/gaze so _apply() can write them back
PARAMS = [
    ('yaw_threshold',    'Yaw Threshold (deg)',    0,    90,   1   ),
    ('pitch_threshold',  'Pitch Threshold (deg)',  0,    90,   1   ),
    ('gaze_h_threshold', 'Gaze H Threshold',       0.0,  0.5,  0.01),
    ('gaze_v_threshold', 'Gaze V Threshold',       0.0,  0.5,  0.01),
    ('gaze_h_offset',    'Gaze H Offset',         -0.5,  0.5,  0.01),
    ('gaze_v_offset',    'Gaze V Offset',         -0.5,  0.5,  0.01),
    ('score_limit',      'Score Limit',            100,  3000, 10  ),
    ('score_increment',  'Score Increment',        10,   500,  5   ),
    ('decay_rate',       'Decay Rate',             1,    100,  1   ),
    ('gaze_weight',      'Gaze Weight',            0.0,  2.0,  0.05),
    ('head_weight',      'Head Weight',            0.0,  2.0,  0.05),
]

class Menu:
    def __init__(self, tracker, gaze, config):
        #These vlaues below are references to the live objects that run in main.py so when we use them and edit them it will live update
        self.tracker = tracker
        self.gaze = gaze
        

        self.config = config #this stores the yaw and the pitch threshold values

        self.is_open = False
        self.window = None #the tkinter Tk window we need
        self._vars = {}  #dictionary of key -> tk.DoubleVar, one per parameter


    def open(self):# opens/makes the menu window
        if self.is_open:
            return
        self.is_open = True
        self._build()   

    def close(self): #closes the menu window and applies changes made
        if not self.is_open:
            return
        self._apply()  
        self.is_open = False
        if self.window:
            self.window.destroy()
            self.window = None

    def toggle(self): #toggle open and closed
        if self.is_open:
            self.close()
        else:
            self.open()

    def update(self):
        """Called once per OpenCV frame to process tkinter events.
            Without this, the menu window would freeze because tkinter
            normally runs its own blocking mainloop(). By calling
            window.update() ourselves each frame, both OpenCV and tkinter
            stay responsive at the same time.
        """
        if self.is_open and self.window:
            try:
                self.window.update()
            except tk.TclError:
                # window was closed externally (e.g. alt-F4)
                self.is_open = False
                self.window = None

   
    #helper methods for building the menu

    def _current_values(self):
        """Reads the current parameter values from tracker, gaze, and config
            so the sliders start at the right positions when the menu opens.
        """
        return {
            'yaw_threshold':    self.config['yaw_threshold'],
            'pitch_threshold':  self.config['pitch_threshold'],
            'gaze_h_threshold': self.gaze.h_threshold,
            'gaze_v_threshold': self.gaze.v_threshold,
            'gaze_h_offset':    self.gaze.h_offset,
            'gaze_v_offset':    self.gaze.v_offset,
            'score_limit':      self.tracker.limit,
            'score_increment':  self.tracker.increment,
            'decay_rate':       self.tracker.decay_rate,
            'gaze_weight':      self.tracker.gaze_weight,
            'head_weight':      self.tracker.head_weight,
        }

    def _apply(self):
        """Writes every slider's current value back to the live objects.
            Called automatically when the menu closes.
        """
        v = self._vars
        self.config['yaw_threshold']   = v['yaw_threshold'].get()
        self.config['pitch_threshold'] = v['pitch_threshold'].get()
        self.gaze.h_threshold          = v['gaze_h_threshold'].get()
        self.gaze.v_threshold          = v['gaze_v_threshold'].get()
        self.gaze.h_offset             = v['gaze_h_offset'].get()
        self.gaze.v_offset             = v['gaze_v_offset'].get()
        self.tracker.limit             = v['score_limit'].get()
        self.tracker.increment         = v['score_increment'].get()
        self.tracker.decay_rate        = v['decay_rate'].get()
        self.tracker.gaze_weight       = v['gaze_weight'].get()
        self.tracker.head_weight       = v['head_weight'].get()

    def _build(self):
        """Creates the tkinter window and populates it with a row of
            widgets for each parameter, plus the Apply & Close button.
        """
        self.window = tk.Tk()
        self.window.title("Settings")
        self.window.configure(bg=BG)
        self.window.resizable(False, False)
        # make the X button call our close() so _apply() still runs
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        # read current values so sliders start in the right position
        current = self._current_values()

        # create one row of widgets per parameter
        for row, (key, label, lo, hi, res) in enumerate(PARAMS):
            # DoubleVar is a tkinter variable that the slider and entry
            # both share — when one changes, the other updates automatically
            var = tk.DoubleVar(value=current[key])
            self._vars[key] = var
            self._add_row(row, label, lo, hi, res, var)

        # single button at the bottom that applies and closes
        tk.Button(
            self.window, text="Apply & Close",
            command=self.close,
            bg="#333", fg=FG,
            font=("Arial", 11, "bold"),
            padx=10, pady=6
        ).grid(row=len(PARAMS), column=0, columnspan=3, pady=12)

    def _add_row(self, row, label, lo, hi, res, var):
        """Builds one parameter row: [label | slider | text entry]
            The slider and entry are linked to the same DoubleVar so they
            always show the same value.
        """

        # column 0 — parameter name label
        tk.Label(
            self.window, text=label, fg=FG, bg=BG,
            font=("Arial", 10), width=20, anchor='w'
        ).grid(row=row, column=0, padx=12, pady=4, sticky='w')

        # column 1 — slider (tk.Scale)
        # resolution sets the step size; showvalue=False hides the
        # built-in number display since the entry box already shows it
        tk.Scale(
            self.window, variable=var,
            from_=lo, to=hi, orient='horizontal',
            resolution=res, length=260,
            bg=BG, fg=FG, highlightthickness=0,
            troughcolor="#444", showvalue=False
        ).grid(row=row, column=1, padx=6)

        # column 2 — text entry box
        # textvariable=var links it to the same DoubleVar as the slider
        entry = tk.Entry(
            self.window, textvariable=var,
            width=7, bg="#333", fg=FG,
            insertbackground=FG, font=("Arial", 10)
        )
        entry.grid(row=row, column=2, padx=12)

        # validate what the user typed: clamp it to [lo, hi]
        # triggers when the user presses Enter or clicks away from the box
        def validate(event, v=var, lo=lo, hi=hi):
            try:
                val = float(entry.get())
                v.set(round(max(lo, min(hi, val)), 4))
            except ValueError:
                pass    # if they typed something non-numeric, just leave it

        entry.bind('<Return>', validate)
        entry.bind('<FocusOut>', validate)
