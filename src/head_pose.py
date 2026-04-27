# This module estimates head orientation (pitch, yaw, roll) from MediaPipe face landmarks.
# Uses anchor points (nose, chin, eye corners) to calculate :D

import cv2
import numpy as np

#index numbers for facial feature locations from MediaPipe
NOSE_TIP = 1
CHIN = 152
LEFT_EYE_CORNER = 263
RIGHT_EYE_CORNER = 33
LEFT_MOUTH_CORNER = 287
RIGHT_MOUTH_CORNER = 57

ANCHOR_INDICES = [NOSE_TIP, CHIN, LEFT_EYE_CORNER,
    RIGHT_EYE_CORNER, LEFT_MOUTH_CORNER, RIGHT_MOUTH_CORNER]

"""standardized avg human face model measured in mm,
    nose tip is origin. corresponds w/ ANCHOR_INDICES
"""
MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),
    (0.0, -63.6, -12.5),
    (-43.3, 32.7, -26.0),
    (43.3, 32.7, -26.0),
    (-28.9, -28.9, -24.1),
    (28.9, -28.9, -24.1),
], dtype=np.float64)

class HeadPose:

    def __init__(self):
        self.anchor_indices = ANCHOR_INDICES
        self.model_points = MODEL_POINTS

    def get_angles(self, landmarks, frame_width, frame_height):
        """returns the pitch, yaw, and roll given 
            MediaPipe's landmarks
        """
        image_points = np.array([
            (landmarks[i].x * frame_width,
            landmarks[i].y * frame_height)
            for i in self.anchor_indices
        ], dtype=np.float64)
    
        #approx of webcam's focal length
        focal_length = frame_width
        center = (frame_width / 2, frame_height / 2)
        #approx of how camera's lens maps 3D space to 2D
        cam_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        #lens distortion coeffs; for modern day cams, we assume no distortion
        distrn_coeffs = np.zeros((4, 1))
        
        """determines rotation vector needed to align 3d 
            and 2d points; gives a representation of the 
            head's rotation in 3d space)
        """
        _, rotation_vec, _ = cv2.solvePnP(
            self.model_points,
            image_points,
            cam_matrix,
            distrn_coeffs
        )
        
        #convertion of rotation_vec into a matrix
        rotation_mat, _ = cv2.Rodrigues(rotation_vec)
        #gets readable angles from the rotation matrix
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_mat)
         
        pitch, yaw, roll = angles[0], angles[1], angles[2]
        return pitch, yaw, roll


