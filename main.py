# Main module for the attention tracker.
# Uses all the other modules and runs the main loop.

import cv2
import mediapipe as mp
from src.camera import Camera
from src.head_pose import HeadPose
from src.gaze import Gaze
from src.tracker import Tracker
from src.alert import Alert

from src.head_pose import NOSE_TIP, CHIN, LEFT_EYE_CORNER, RIGHT_EYE_CORNER, LEFT_MOUTH_CORNER, RIGHT_MOUTH_CORNER
from src.gaze import LEFT_EYE_INNER, LEFT_EYE_OUTER, RIGHT_EYE_INNER, RIGHT_EYE_OUTER, LEFT_EYE_TOP, LEFT_EYE_BOTTOM, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM, LEFT_IRIS, RIGHT_IRIS

#landmark index constants
LANDMARKS = [NOSE_TIP, CHIN, LEFT_EYE_CORNER,
    RIGHT_EYE_CORNER, LEFT_MOUTH_CORNER, RIGHT_MOUTH_CORNER,
    LEFT_EYE_INNER, LEFT_EYE_OUTER, RIGHT_EYE_INNER,
    RIGHT_EYE_OUTER, LEFT_EYE_TOP, LEFT_EYE_BOTTOM,
    RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM, RIGHT_IRIS, LEFT_IRIS]

"""PARAMETERS USERS SHOULD BE ABLE TO CHANGE:"""
#default head angle thresholds (in degrees)
YAW_THRESHOLD = 40      #increase -> more horiz. leniency
PITCH_THRESHOLD = 30    #increase -> more vertical leniency
#default eye ratio thresholds (eye positioning relative to
#   eye corners & eyelids. A 0.50 ratio means the eye is in
#   the center.
GAZE_H_THRESHOLD = 0.45 #increase -> more horiz. leniency
GAZE_V_THRESHOLD = 0.40 #increase -> more vertical leniency
#Gaze Offsets. helps adjust for natural eye resting position
#   while locked in.
#for horizontal offset: + = right, - = left
#for vertical offset:   + = down,  - = up
GAZE_H_OFFSET = 0.0
GAZE_V_OFFSET = 0.1     #offset b/c webcam usually above screen
#score parameters!
SCORE_LIMIT = 1000      #score needed for alert
SCORE_INCREMENT = 150   #score increment per sec not locked
DECAY_RATE = 10         #how much score decays per second
GAZE_WEIGHT = 1.0       #weight parameter for gaze incremnts
HEAD_WEIGHT = 1.0       #weight parameter for head incremnts

def main():
    
    camera = Camera()
    head_pose = HeadPose()
    gaze = Gaze(h_threshold=GAZE_H_THRESHOLD,
        v_threshold=GAZE_V_THRESHOLD,
        h_offset=GAZE_H_OFFSET, v_offset=GAZE_V_OFFSET)
    tracker = Tracker(limit=SCORE_LIMIT,
        increment=SCORE_INCREMENT, gaze_weight=GAZE_WEIGHT,
        head_weight=HEAD_WEIGHT, decay_rate=DECAY_RATE)
    alert = Alert()

    #setting up mediapipe stuff
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,   #req for iris tracking
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    while True:
        #reading camera frame
        success, frame = camera.read_frame()
        if not success:     #couldnt read frame, break loop
            break
        
        frame_height, frame_width = frame.shape[0:2]

        #mediapipe needs RGB, converting:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        #when mediapipe picks up landmarks
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            #getting head angles :>
            pitch, yaw, roll = head_pose.get_angles(landmarks, frame_width, frame_height)
            head_not_locked = abs(yaw) > YAW_THRESHOLD or abs(pitch) > PITCH_THRESHOLD
            
            #getting gaze ratios :o
            h_ratio, v_ratio = gaze.get_gaze_ratio(landmarks, frame_width, frame_height)
            gaze_not_locked = gaze.is_looking_away(h_ratio, v_ratio)
            tracker.update(gaze_not_locked, head_not_locked)
            
            #displaying used mediapipe landmarks
            for idx in LANDMARKS:
                landmark = results.multi_face_landmarks[0].landmark[idx]
                #converting landmark locs to pixels
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)
                if (idx == LEFT_IRIS or idx == RIGHT_IRIS):
                    cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
                else:
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            #final score debug msg
            score, pct = tracker.get_score()
            cv2.putText(frame, f"LOCKED OUT: {int(score)} / {int(SCORE_LIMIT)} ({int(pct)}%) ",
                (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0), 2)

            #ARE THEY LOCKED?
            if tracker.should_alert():
                alert.trigger(tracker.alert_reason)
                tracker.reset()
            
            #display tracking info on camera frame
            cv2.putText(frame, f"Yaw: {yaw:.1f} Pitch: {pitch:.1f}",
                (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0), 2)
            cv2.putText(frame, f"Gaze: {'Away' if gaze_not_locked else 'Locked'}",
                (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0), 2)

        #showing frame
        cv2.imshow("IT'S TIME TO LOCK IN", frame)
        
        #for now, quit whenever 'Q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    camera.release()
    face_mesh.close()

if __name__ == "__main__":
    main()

