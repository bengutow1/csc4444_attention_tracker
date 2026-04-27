# Main module for the attention tracker.
# Uses all the other modules and runs the main loop.

import cv2
import mediapipe as mp
from src.camera import Camera
from src.head_pose import HeadPose
from src.gaze import Gaze
from src.tracker import Tracker
from src.alert import Alert

#default head angle thresholds (in degrees)
YAW_THRESHOLD = 40
PITCH_THRESHOLD = 30

def main():
    
    camera = Camera()
    head_pose = HeadPose()
    gaze = Gaze(threshold=0.46)
    tracker = Tracker(count_threshold=1, dur_threshold=2.0)
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
            left_ratio, right_ratio = gaze.get_gaze_ratio(landmarks, frame_width, frame_height)
            gaze_not_locked = gaze.is_looking_away(left_ratio, right_ratio)
            #passing info to tracker
            tracker.update(gaze_not_locked, head_not_locked)

            #final score debug msg
            final_score, gaze_score, head_score = tracker.get_score()
            cv2.putText(frame, f"Score: {final_score:.2f}",
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

