# This module handles counters & determines when to alert.
# Applies user-adjustable weights and leniency thresholds.

import time

class Tracker:
    
    def __init__(self, limit=1000, decay_rate=10,
        increment=100, gaze_weight=1.0,
        head_weight=1.0, gaze_drownout=0.5):
        """limit: score needed to trigger an alert
            decay_rate: score lost per second
            increment: base score gained per qualifying look
            gaze_weight: how much gaze contributes (1.0 default)
            head_weight: how much head contributes (1.0 default)
        """
        
        self.limit = limit
        self.decay_rate = decay_rate
        self.increment = increment
        self.gaze_weight = gaze_weight
        self.head_weight = head_weight
        self.gaze_drownout = gaze_drownout

        self.score = 0.0
        self.alert_reason = None
        self.last_update = time.time()

    def update(self, gaze_not_locked, head_not_locked):
        """updates score based on gaze + head lookaway
            status. Score also decays over time
        """

        cur_time = time.time()
        time_diff = cur_time - self.last_update
        self.last_update = cur_time

        #score decay
        self.score = max(0.0, self.score - (self.decay_rate * time_diff))

        #incrementing the score and setting the alert_reason
        if gaze_not_locked and head_not_locked:
            self.score = min(self.limit,
                self.score + (self.increment * max(self.gaze_weight, self.head_weight) * time_diff))
            self.alert_reason = "both"
        elif gaze_not_locked:
            self.score = min(self.limit,
                self.score + (self.increment * self.gaze_weight * time_diff))
            self.alert_reason = "gaze"
        elif head_not_locked:
            self.score = min(self.limit,
                self.score + (self.increment * self.head_weight * time_diff * self.gaze_drownout))
            self.alert_reason = "head"

    def get_score(self):
        """returns current score, percentage
        """

        pct = (self.score / self.limit) * 100
        return self.score, pct

    def should_alert(self):
        """returns True if the score has hit the limit
        """

        return self.score >= self.limit

    def reset(self):
        """resets score
        """
        self.score = 0.0
        self.alert_reason = None
        self.last_update = time.time()

