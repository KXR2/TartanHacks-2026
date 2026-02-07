# TartanHacks-2026: Flowstate – Problem Solvers

Footage of program working with a musician: https://uwprod-my.sharepoint.com/personal/jding95_wisc_edu/_layouts/15/stream.aspx?id=%2Fpersonal%2Fjding95%5Fwisc%5Fedu%2FDocuments%2FAttachments%2FIMG%5F1672%2Emov&ga=1&LOF=1&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2E63ebb144%2De329%2D4e52%2Dbecf%2D2f7665fc044c 

Zachary Diringer, Kade Rolfe, Eleanor Ding, Marysol Alape Toro
Project Overview

Flowstate addresses a common problem in concert band and orchestra settings: ensemble members often fall out of sync with the conductor. Miscounted rests, rushing ahead, or falling behind can disrupt performance. Musicians may also focus more on their sheet music than the conductor’s motions.  This product is also for blind & people that have vision issues.

Our solution is a human-adaptive metronome that allows ensemble members to follow the conductor accurately, keeping the group synchronized without needing to constantly watch the conductor.

Proposed Solution

We developed two main systems:

Vision-Based Conductor Tracker

Tracks the conductor’s arm motion using computer vision and region segmentation.

Detects downbeats and measure numbers in real time.

Produces clicking sounds on beats.

Every four measures, a verbal cue announces the current measure number.

Keyboard-Based Metronome

Users press the up arrow to indicate a new measure and the down arrow to add additional beats to a measure.

Produces clicking sounds on beats and announces measure numbers every four measures.

Supports custom time signatures and tempos.

Optional Exploratory Models:

YOLO-based phone tracking generates clicks when the phone reaches relative extrema.

Hand gesture tracking creates clicks on relative extrema of hand motion.

Next Steps

Refine camera and computer vision parameters for more accurate conductor tracking.

Develop a single unified UI to host all metronomic devices and models.

Setup Instructions
Prerequisites

Python 3.11

Dependencies:

opencv-python
numpy
keyboard
scipy
sounddevice
uvicorn
fastapi
ultralytics

Keyboard Metronomic Device

Navigate to keyboardConductorProject.

Run:

uvicorn backend:app --host 127.0.0.1 --port 8000


Open your browser to http://localhost:8000
.

Controls:

Up Arrow → create a new measure

Down Arrow → add a beat to the current measure

Measure Number Gesture Tracker

Navigate to measureDetectorProject.

Run:

uvicorn measureDetectorWebSocket:app --host 127.0.0.1 --port 8001


Open your browser to http://localhost:8001
.

Controls:

Start Button → initialize the camera

Use a red glove or object as a tracking reference

Moving the red object to the bottom half of the frame triggers a click for a new measure

Stop Button → pause and reset the system

Miscellaneous Gesture Tracking

YOLO Phone Tracking:

Navigate to backend/backend and run:

python yoloIdea.py


Hand Gesture Click Tracking:

Navigate to backend/backend and run:

python conductor_metronome.py

Testing

Performed with a test musician (clarinetist).

The musician relied solely on the metronome systems without looking at the conductor.

Videos demonstrate that the systems maintained accurate timing for the exercises.
