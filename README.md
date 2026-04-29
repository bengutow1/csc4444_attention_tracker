# CSC4444 - Attention Tracker

Group Members: Vinh Le, Ben Gutowski, Kyle King

## Setup

1. Create a conda environment:
```
conda create -n attention-tracker python=3.10
conda activate attention-tracker
```

2. Install dependencies:
```
make sure you do this through the anaconda cli and not in an ide unless you can get it working correctly. We reccomend keeping all terminal interactions to the anaconda prompt so you do not run into any issues with the interpreter/environment.

pip install -r requirements.txt
```

3. Run the program:
```
python main.py

if running into problems double check requirments.txt file we made and make sure you have the right versions for things like mediapipe. BTW mediapipe we have only works on python 3.10
```

## Usage
- A webcam window will open showing your face with landmark overlays
- The program tracks eye gaze and head orientation in real-time
- An alert will be issued if you look away too frequently or for too long
- Press `Q` to quit
- press `M` to open the menu and adjust parameters as you like to test the responsivness of the software below is a restated description of some of the parameters you can change:

"""PARAMETERS USERS SHOULD BE ABLE TO CHANGE:"""
"""
#default head angle thresholds (in degrees)
YAW_THRESHOLD = 40      #increase -> more horiz. leniency
PITCH_THRESHOLD = 30    #increase -> more vertical leniency
#default eye ratio thresholds eye positioning relative to
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
"""