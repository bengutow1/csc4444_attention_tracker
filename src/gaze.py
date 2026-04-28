"""This module handles iris/gaze tracking using MediaPipe
    landmarks. Calculates iris pos relative to eye corners 
    and eyelids to determine gaze direction
"""

import numpy as np

#index numbers for MediaPipe's facial landmarks
LEFT_EYE_INNER = 133
LEFT_EYE_OUTER = 33
RIGHT_EYE_INNER = 362
RIGHT_EYE_OUTER = 263
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374
LEFT_IRIS = 468
RIGHT_IRIS = 473

class Gaze:
    
    #0.5 threshold is center.
    #still playing around, h_thresh is horizontal threshold
    #v_thresh is vertical threshold
    def __init__(self, h_threshold=0.45, v_threshold=0.35):
        
        self.h_threshold = h_threshold
        self.v_threshold = v_threshold
    
    def get_gaze_ratio(self, landmarks, frame_width, frame_height):
        """returns h_ratio, v_ratio of how far from
            the center the iris's are
        """
        
        #helper function for converting landmark vals into
        #   pixel coordinates
        def to_px(idx):
            return np.array([
                landmarks[idx].x * frame_width,
                landmarks[idx].y * frame_height])

        #points for measuring horizontal ratio
        left_inner = to_px(LEFT_EYE_INNER)
        left_outer = to_px(LEFT_EYE_OUTER)
        right_inner = to_px(RIGHT_EYE_INNER)
        right_outer = to_px(RIGHT_EYE_OUTER)

        #pts for measuring vert ratio
        left_top = to_px(LEFT_EYE_TOP)
        left_bottom = to_px(LEFT_EYE_BOTTOM)
        right_top = to_px(RIGHT_EYE_TOP)
        right_bottom = to_px(RIGHT_EYE_BOTTOM)

        #iris points
        left_iris = to_px(LEFT_IRIS)
        right_iris = to_px(RIGHT_IRIS)

        """for the ratios, calculates distance between
            iris & both a horizontal + vertical landmark,
            divided by total distance between that landmark
            and its counterpart (for ex: inner eye corner &
            outer eye corner. Ratio is between 0 and 1
        """
        #horizontal ratios
        l_h_ratio = np.linalg.norm(left_iris - left_outer) / np.linalg.norm(left_inner - left_outer)
        r_h_ratio = np.linalg.norm(right_iris - right_outer) / np.linalg.norm(right_inner - right_outer)

        #vert ratios
        l_v_ratio = np.linalg.norm(left_iris - left_top) / np.linalg.norm(left_bottom - left_top)
        r_v_ratio = np.linalg.norm(right_iris - right_top) / np.linalg.norm(right_bottom - right_top)

        #avging out ratios
        h_ratio = (l_h_ratio + r_h_ratio) / 2
        v_ratio = (l_v_ratio + r_v_ratio) / 2

        return h_ratio, v_ratio
    
    #compares ratios to determine if eyes are looking away
    def is_looking_away(self, h_ratio, v_ratio):
        h_not_locked = h_ratio < self.h_threshold or h_ratio > (1 - self.h_threshold)
        v_not_locked = v_ratio < self.v_threshold or v_ratio > (1- self.v_threshold)
        return h_not_locked or v_not_locked

