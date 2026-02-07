import cv2
import numpy as np
import simpleaudio as sa
import time
from collections import deque
import threading
import os

# ------------------- CONFIG -------------------
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TARGET_FPS = 6
MIN_TIME_BETWEEN_CLICKS = 0.3
SMOOTHING_FRAMES = 5

BOTTOM_REGION_HEIGHT = 200    # Bottom 200 px for measure detection

MEASURE_WAV_FOLDER = "measure_wavs"  # Folder with measure1.wav, measure2.wav, etc.

# ------------------- AUDIO -------------------
def generate_click(frequency=1000, duration_ms=50):
    fs = 44100
    t = np.linspace(0, duration_ms/1000, int(fs*duration_ms/1000), False)
    return (np.sin(frequency*2*np.pi*t)*32767).astype(np.int16)

click_downbeat = generate_click(1500, 30)

audio_queue = deque()
def play_click(audio):
    audio_queue.append(audio)

def play_wav(filename):
    try:
        wave_obj = sa.WaveObject.from_wave_file(filename)
        audio_queue.append(wave_obj)
    except Exception as e:
        print(f"Failed to play {filename}: {e}")

def audio_thread():
    while True:
        if audio_queue:
            obj = audio_queue.popleft()
            if isinstance(obj, sa.WaveObject):
                obj.play()
            else:
                sa.play_buffer(obj, 1, 2, 44100)
        time.sleep(0.001)

threading.Thread(target=audio_thread, daemon=True).start()

# ------------------- CAMERA -------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# Wrist smoothing
wrist_history = deque(maxlen=SMOOTHING_FRAMES)
prev_time = None
measure_count = input("Enter the number of the first measure (default 1): ")
try:
    measure_count = int(measure_count) if measure_count.strip() else 1
except ValueError:
    measure_count = 1
in_bottom_region = False  # Track whether hand is currently in bottom region
downbeat_times = []

# ------------------- MAIN LOOP -------------------
while True:
    ret, frame = cap.read()
    if not ret:
        continue
    frame = cv2.flip(frame, 1)

    # ------------------- RED STICK DETECTION -------------------
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.GaussianBlur(mask, (5,5), 0)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    wrist_point = None

    if contours:
        cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(cnt) > 200:
            hull = cv2.convexHull(cnt)
            bottommost = tuple(hull[hull[:,:,1].argmax()][0])
            wrist_point = (int(bottommost[0]), int(bottommost[1]))
            wrist_history.append(wrist_point)
            cv2.circle(frame, wrist_point, 6, (0,0,255), -1)

    # ------------------- SMOOTHING -------------------
    if len(wrist_history) >= 2:
        smoothed_x = int(np.mean([p[0] for p in wrist_history]))
        smoothed_y = int(np.mean([p[1] for p in wrist_history]))
        smoothed_point = (smoothed_x, smoothed_y)

        prev_smoothed = (int(np.mean([p[0] for p in list(wrist_history)[:-1]])),
                         int(np.mean([p[1] for p in list(wrist_history)[:-1]])))
        dy = smoothed_point[1] - prev_smoothed[1]

        # ------------------- MEASURE DETECTION -------------------
        now_in_bottom = smoothed_point[1] > FRAME_HEIGHT - BOTTOM_REGION_HEIGHT
        new_measure_trigger = now_in_bottom and not in_bottom_region and dy > 0
        in_bottom_region = now_in_bottom

        if new_measure_trigger:
            now = time.perf_counter()
            if prev_time is None or (now - prev_time) > MIN_TIME_BETWEEN_CLICKS:
                play_click(click_downbeat)
                downbeat_times.append(now)
                measure_count += 1
                # Voiceover WAV playback from folder
                wav_file = os.path.join(MEASURE_WAV_FOLDER, f"measure_{measure_count}.wav")
                if os.path.exists(wav_file):
                    threading.Thread(target=play_wav, args=(wav_file,), daemon=True).start()
                prev_time = now

    # ------------------- DISPLAY -------------------
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, FRAME_HEIGHT-BOTTOM_REGION_HEIGHT), (FRAME_WIDTH, FRAME_HEIGHT), (200,200,200), 2)
    cv2.putText(overlay, f"Measures: {measure_count}", (10,50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,128,0),2)
    cv2.imshow("Measure Tracker", overlay)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

# ------------------- SAVE MEASURE TIMES -------------------
with open("measure_times.csv", "w") as f:
    for t in downbeat_times:
        f.write(f"{t}\n")
print(f"Detected {len(downbeat_times)} measures.")
