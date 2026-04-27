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
pip install -r requirements.txt
```

3. Run the program:
```
python main.py
```

## Usage
- A webcam window will open showing your face with landmark overlays
- The program tracks eye gaze and head orientation in real-time
- An alert will be issued if you look away too frequently or for too long
- Press `Q` to quit
