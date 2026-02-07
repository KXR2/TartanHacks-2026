import cv2
import numpy as np
from ultralytics import YOLO
import sounddevice as sd
import time

# ---------------- CONFIG ----------------
FS = 44100
CLICK_DURATION = 0.02  # 20ms click
CLICK_FREQ = 1500
SMOOTHING = 5          # frames moving average
MIN_FRAMES_BETWEEN_CLICKS = 5

# ---------------- CLICK SOUND ----------------
t = np.linspace(0, CLICK_DURATION, int(FS * CLICK_DURATION), False)
click_sound = (0.5 * np.sin(2 * np.pi * CLICK_FREQ * t)).astype(np.float32)

def play_click():
    sd.play(click_sound, FS, blocking=False)

# ---------------- YOLO ----------------
model = YOLO("yolov8n.pt")  # Pretrained COCO

# ---------------- STATE ----------------
y_history = []
x_history = []
measure_number = 1
current_beat = 0
last_click_frame = -MIN_FRAMES_BETWEEN_CLICKS
frame_counter = 0
frame_width = 640  # default, updated later

# ---------------- VIDEO ----------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot open camera")

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
x_center_range = (frame_width * 0.4, frame_width * 0.6)  # horizontal center

print("Conductor tracker (phone as baton). Press ESC to quit.")

def is_relative_extrema(history, idx):
    # Simple check: previous < current > next or previous > current < next
    if len(history) < 3:
        return False
    prev, curr, nxt = history[idx-1], history[idx], history[idx+1]
    return (curr > prev and curr > nxt) or (curr < prev and curr < nxt)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_counter += 1

    results = model(frame, stream=False)
    boxes = results[0].boxes.xyxy.cpu().numpy() if results else []
    classes = results[0].boxes.cls.cpu().numpy() if results else []

    # Track only cell phone (COCO class 67)
    phone_boxes = [b for i, b in enumerate(boxes) if int(classes[i]) == 67]

    if phone_boxes:
        b = max(phone_boxes, key=lambda bb: (bb[2]-bb[0])*(bb[3]-bb[1]))
        x1, y1, x2, y2 = b
        baton_x = (x1 + x2)/2
        baton_y = (y1 + y2)/2

        # Smooth
        x_history.append(baton_x)
        y_history.append(baton_y)
        if len(x_history) > SMOOTHING:
            x_history.pop(0)
        if len(y_history) > SMOOTHING:
            y_history.pop(0)
        smooth_x = sum(x_history)/len(x_history)
        smooth_y = sum(y_history)/len(y_history)

        # Detect relative extrema
        if frame_counter > 2 + last_click_frame:
            # Need at least 3 points
            y_ext = is_relative_extrema(y_history, -2)  # -2 = middle of last 3
            x_ext = is_relative_extrema(x_history, -2)
            if y_ext or x_ext:
                play_click()
                last_click_frame = frame_counter
                current_beat += 1

                # Check if downbeat (new measure)
                # Relative minimum y + horizontal near center
                if y_history[-2] == min(y_history[-3:]) and x_center_range[0] < smooth_x < x_center_range[1]:
                    print(f"Downbeat (new measure) {measure_number}")
                    measure_number += 1
                    current_beat = 1
                else:
                    print(f"Beat {current_beat}")

        # Draw visuals
        x1, y1, x2, y2 = map(int, b)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.circle(frame, (int(smooth_x), int(smooth_y)), 5, (0,0,255), -1)

    cv2.imshow("Conductor Tracker (Phone)", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
