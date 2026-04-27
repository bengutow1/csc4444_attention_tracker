# This module handles counters & determines when to alert.
# Applies user-adjustable weights and leniency thresholds.

import time

class Tracker:
    
    def __init__(self, gaze_weight=0.5, head_weight=0.5,
        count_threshold=5, dur_threshold=3.0):

        self.gaze_weight = gaze_weight
        self.head_weight = head_weight

        # number of lookaways/time (secs) before alert
        self.count_threshold = count_threshold
        self.dur_threshold = dur_threshold
        self.alert_reason = None

        #keeping track of gaze/head lookaway durations
        self.gaze_start = None
        self.head_start = None
        
        #for score decay mechanism
        self.window = 20      #only look at the last 20 secs
        self.gaze_events = []   #list of (timestamp, dur)
        self.head_events = []
    
    def update(self, is_gaze_away, is_head_away):
        """Updates the lookaway counters based on booleans 
            given from head_pose.py and gaze.py
        """

        cur_time = time.time()
        
        #updating gaze counters
        if is_gaze_away:
            if self.gaze_start is None:
                self.gaze_start = cur_time
        else:
            if self.gaze_start is not None:
                duration = cur_time - self.gaze_start
                self.gaze_events.append((self.gaze_start, duration))
                self.gaze_start = None

        #updating head counters
        if is_head_away:
            if self.head_start is None:
                self.head_start = cur_time
        else:
            if self.head_start is not None:
                duration = cur_time - self.head_start
                self.head_events.append((self.head_start, duration))
                self.head_start = None

        #remove old events
        self.gaze_events = [(t, d) for t, d in self.gaze_events if cur_time - t < self.window]
        self.head_events = [(t, d) for t, d in self.head_events if cur_time - t < self.window]  

    def get_score(self):
        """Calculates a score based on distraction frequency
            and avg distraction duration. The final score
            determines if the user will get alerted.
            Returns final_score, gaze_score, head_score
        """
        
        #calculating, normalizing count score
        gaze_count = len(self.gaze_events)
        head_count = len(self.head_events)
        gaze_duration = sum(d for _, d in self.gaze_events)
        head_duration = sum(d for _, d in self.head_events)
        #include current ongoing lookaways in score
        cur_time = time.time()
        if self.gaze_start is not None:
            gaze_duration += cur_time - self.gaze_start
        if self.head_start is not None:
            head_duration += cur_time - self.head_start

        gaze_count_score = min(gaze_count / self.count_threshold, 1.0)
        head_count_score = min(head_count / self.count_threshold, 1.0)
        #calculating, normalizing duration score
        gaze_duration_score = min(gaze_duration / self.dur_threshold, 1.0)
        head_duration_score = min(head_duration / self.dur_threshold, 1.0)
        #avg out count and duration scores into one
        gaze_score = (gaze_count_score + gaze_duration_score) / 2
        head_score = (head_count_score + head_duration_score) / 2
        #apply weights
        final_score = (gaze_score * self.gaze_weight) + (head_score * self.head_weight)
        return final_score, gaze_score, head_score

    def should_alert(self, score_threshold=1.0):
        """Determines based on the final score from 
            get_score if an alert should be issued. 
            Returns a boolean and updates self.alert_reason.
        """
        
        final_score, gaze_score, head_score = self.get_score()
        #checking score vs thresholds and determining cause
        if final_score >= score_threshold:
            if gaze_score >= head_score and head_score >= score_threshold:
                self.alert_reason = "both"
            elif gaze_score >= head_score:
                self.alert_reason = "gaze"
            else:
                self.alert_reason = "head"
            return True
        return False

    def reset(self):
        """Resets the counters held by the tracker
        """

        self.gaze_start = None
        self.head_start = None
        self.gaze_events = []
        self.head_events = []
        self.alert_reason = None

 
