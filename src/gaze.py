"""This module handles iris/gaze tracking using MediaPipe landmarks.
    Calculates iris pos relative to eye corners to determine gaze direction
"""

import numpy as np

#index numbers for MediaPipe's facial landmarks
LEFT_EYE_INNER = 133
LEFT_EYE_OUTER = 33
RIGHT_EYE_INNER = 362
RIGHT_EYE_OUTER = 263
LEFT_IRIS = 468
RIGHT_IRIS = 473

class Gaze:
    
    #0.5 threshold is center, playing around w/ thresholds still
    def __init__(self, threshold=0.45):
        self.left_eye_ind = [LEFT_EYE_INNER, LEFT_EYE_OUTER]
        self.right_eye_ind = [RIGHT_EYE_INNER, RIGHT_EYE_OUTER]
        self.left_iris = LEFT_IRIS
        self.right_iris = RIGHT_IRIS
        self.threshold = threshold
    
    """returns left_ratio, right_ratio of how far from
        the center the iris's are
    """
    def get_gaze_ratio(self, landmarks, frame_width, frame_height):
        
        #translate landmark decimals into np arrays of pixel coords
        left_inner = np.array(
            [landmarks[LEFT_EYE_INNER].x * frame_width,
            landmarks[LEFT_EYE_INNER].y * frame_height])
        left_outer = np.array(
            [landmarks[LEFT_EYE_OUTER].x * frame_width,
            landmarks[LEFT_EYE_OUTER].y * frame_height])
        left_iris = np.array(
            [landmarks[LEFT_IRIS].x * frame_width,
            landmarks[LEFT_IRIS].y * frame_height])
        
        right_inner = np.array(
            [landmarks[RIGHT_EYE_INNER].x * frame_width,
            landmarks[RIGHT_EYE_INNER].y * frame_height])
        right_outer = np.array(
            [landmarks[RIGHT_EYE_OUTER].x * frame_width,
            landmarks[RIGHT_EYE_OUTER].y * frame_height])
        right_iris = np.array(
            [landmarks[RIGHT_IRIS].x * frame_width,
            landmarks[RIGHT_IRIS].y * frame_height])
        
        """for the ratios, calculates distance between iris &
            outer corner, divided by total eye width.
            Ratio is between 0 and 1
        """
        left_ratio = np.linalg.norm(left_iris - left_outer) / np.linalg.norm(left_inner - left_outer)
        right_ratio = np.linalg.norm(right_iris - right_outer) / np.linalg.norm(right_inner - right_outer)
        
        return left_ratio, right_ratio

    #compares ratios to determine if eyes are looking away
    def is_looking_away(self, left_ratio, right_ratio):
        avg = (left_ratio + right_ratio) / 2
        if avg < self.threshold or avg > (1 - self.threshold):
            return True
        return False

