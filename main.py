# Main module for the attention tracker.
# Uses all the other modules and runs the main loop.

import cv2
import mediapipe as mp
from src.camera import Camera
from src.head_pose import HeadPose
from src.gaze import Gaze
from src.tracker import Tracker
from src.alert import Alert
from src.menu import Menu

from src.head_pose import NOSE_TIP, CHIN, LEFT_EYE_CORNER, RIGHT_EYE_CORNER, LEFT_MOUTH_CORNER, RIGHT_MOUTH_CORNER
from src.gaze import LEFT_EYE_INNER, LEFT_EYE_OUTER, RIGHT_EYE_INNER, RIGHT_EYE_OUTER, LEFT_EYE_TOP, LEFT_EYE_BOTTOM, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM, RIGHT_IRIS, LEFT_IRIS

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
GAZE_H_THRESHOLD = 0.25 #increase -> more horiz. leniency
GAZE_V_THRESHOLD = 0.25 #increase -> more vertical leniency
#Gaze Offsets. helps adjust for natural eye resting position
#   while locked in.
#for horizontal offset: + = right, - = left
#for vertical offset:   + = down,  - = up
GAZE_H_OFFSET = 0.0
GAZE_V_OFFSET = 0.1     #offset b/c webcam usually above screen
#score parameters!
SCORE_LIMIT = 1000      #score needed for alert
SCORE_INCREMENT = 150   #score increment per sec not locked
DECAY_RATE = 20         #how much score decays per second
GAZE_WEIGHT = 1.0       #weight parameter for gaze incremnts
HEAD_WEIGHT = 1.0       #weight parameter for head incremnts
#This parameter is used when the gaze is locked but the head
#   is not. For example, if you don't want much pt gain when
#   your head is turned away but your eyes are locked, lower
#   this value so the score gain gets weighted (downwards).
#   This setting should be between 0 and 1
GAZE_DROWNOUT_FACTOR = 0.5  # decrease -> higher gaze priority    

WIN_NAME = "IT'S TIME TO LOCK IN"
BTN_X1, BTN_X2 = 5, 120   # left/right edges shared by both buttons
BTN_H  = 25                # height of each button
BTN_PAD = 10               # gap from bottom of frame
BTN_GAP = 3                # gap between the two buttons

def draw_buttons(frame, is_open, menu_bounds):
    """Draws [M] Menu and [Q] Quit in the bottom-left corner.
        Writes the menu button's bounding box into menu_bounds[0]
        so the mouse callback always has the current position.
    """
    h = frame.shape[0]
    x1, x2 = BTN_X1, BTN_X2

    # quit button at the very bottom
    qy2 = h - BTN_PAD
    qy1 = qy2 - BTN_H
    # menu button sits just above quit
    my2 = qy1 - BTN_GAP
    my1 = my2 - BTN_H

    # store menu bounds so on_mouse can hit-test against them
    menu_bounds[0] = (x1, my1, x2, my2)

    fill = (80, 80, 80) if is_open else (40, 40, 40)
    cv2.rectangle(frame, (x1, my1), (x2, my2), fill, -1)
    cv2.rectangle(frame, (x1, my1), (x2, my2), (180, 180, 180), 1)
    cv2.putText(frame, "[M] Menu", (x1 + 6, my2 - 7),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

    cv2.rectangle(frame, (x1, qy1), (x2, qy2), (40, 40, 40), -1)
    cv2.rectangle(frame, (x1, qy1), (x2, qy2), (180, 180, 180), 1)
    cv2.putText(frame, "[Q] Quit", (x1 + 6, qy2 - 7),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

def main():

    camera = Camera()
    head_pose = HeadPose()
    gaze = Gaze(h_threshold=GAZE_H_THRESHOLD,
        v_threshold=GAZE_V_THRESHOLD,
        h_offset=GAZE_H_OFFSET, v_offset=GAZE_V_OFFSET)
    tracker = Tracker(limit=SCORE_LIMIT,
        increment=SCORE_INCREMENT, gaze_weight=GAZE_WEIGHT,
        head_weight=HEAD_WEIGHT, decay_rate=DECAY_RATE,
        gaze_drownout=GAZE_DROWNOUT_FACTOR)
    alert = Alert()

    # changeable config for values that live in main rather than in an object
    config = {
        'yaw_threshold': YAW_THRESHOLD,
        'pitch_threshold': PITCH_THRESHOLD,
    }
    menu = Menu(tracker, gaze, config)

    #setting up mediapipe stuff
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,   #req for iris tracking
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    cv2.namedWindow(WIN_NAME)

    menu_bounds = [(0, 0, 0, 0)]  # updated each frame by draw_buttons

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            bx1, by1, bx2, by2 = menu_bounds[0]
            if bx1 <= x <= bx2 and by1 <= y <= by2:
                menu.toggle()
                if not menu.is_open:
                    tracker.reset()

    cv2.setMouseCallback(WIN_NAME, on_mouse)
    menu.open() #open settings on startup

    while True:
        #track whether menu just closed this frame so we can reset the tracker
        was_open = menu.is_open
        menu.update()
        if was_open and not menu.is_open:
            tracker.reset()

        #reading camera frame
        success, frame = camera.read_frame()
        if not success:  #couldnt read frame, break loop
            break

        frame_height, frame_width = frame.shape[0:2]

        #mediapipe needs RGB input but opencv gives BGR so we found we gotta convert it:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        #when mediapipe picks up landmarks
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            #getting head angles :>
            pitch, yaw, roll = head_pose.get_angles(landmarks, frame_width, frame_height)
            head_not_locked = abs(yaw) > config['yaw_threshold'] or abs(pitch) > config['pitch_threshold']

            #getting gaze ratios :o
            h_ratio, v_ratio = gaze.get_gaze_ratio(landmarks, frame_width, frame_height)
            gaze_not_locked = gaze.is_looking_away(h_ratio, v_ratio, yaw, pitch)

            if not menu.is_open:
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
            cv2.putText(frame, f"LOCKED OUT: {int(score)} / {int(tracker.limit)} ({int(pct)}%) ",
                (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0), 2)

            #ARE THEY LOCKED?
            if not menu.is_open and tracker.should_alert():
                alert.trigger(tracker.alert_reason)
                tracker.reset()

            #display tracking info on camera frame
            cv2.putText(frame, f"Yaw: {yaw:.1f} Pitch: {pitch:.1f}",
                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0), 2)
            
            cv2.putText(frame, f"Gaze: {'Away' if gaze_not_locked else 'Locked'}",
                (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0), 2)

        draw_buttons(frame, menu.is_open, menu_bounds)

        #showing frame
        cv2.imshow(WIN_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('m'):
            menu.toggle()
            if not menu.is_open:
                tracker.reset()

    camera.release()
    face_mesh.close()

if __name__ == "__main__":
    main()
