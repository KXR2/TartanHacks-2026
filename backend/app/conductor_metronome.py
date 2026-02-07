import sys
import time

try:
    from cvzone.HandTrackingModule import HandDetector
except ImportError:
    print("Error: cvzone is not installed. Please run 'pip install cvzone' and try again.")
    sys.exit(1)

import cv2
import numpy as np
import simpleaudio as sa

# --- Config ---
ALPHA = 0.3  # Low-pass filter smoothing factor
DEBOUNCE_TIME = 0.18  # seconds
VEL_THRESH = 15  # Minimum velocity (pixels/sec) to consider extremum

# --- Audio ---
def play_click(accent=False):
    freq = 880 if accent else 440
    fs = 44100
    duration = 0.05
    t = np.linspace(0, duration, int(fs * duration), False)
    tone = np.sin(freq * 2 * np.pi * t)
    envelope = np.exp(-40 * t)
    audio = (tone * envelope * (0.5 if accent else 0.3))
    audio = (audio * 32767).astype(np.int16)
    sa.play_buffer(audio, 1, 2, fs)

# --- Smoothing ---
class LowPassFilter:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.state = None
    def filter(self, value):
        if self.state is None:
            self.state = value
        else:
            self.state = self.alpha * value + (1 - self.alpha) * self.state
        return self.state

# --- Beat State Machine ---
class BeatStateMachine:
    def __init__(self):
        self.state = 0  # 0: down, 1: left, 2: right, 3: up
    def next(self):
        self.state = (self.state + 1) % 4
    def get_expected(self):
        return self.state

# --- Main Loop ---
def main():
    cap = cv2.VideoCapture(0)
    retry_count = 0
    while not cap.isOpened() and retry_count < 10:
        print("Waiting for camera access... (check macOS Privacy & Security > Camera)")
        time.sleep(1)
        cap = cv2.VideoCapture(0)
        retry_count += 1
    if not cap.isOpened():
        print("Error: Could not open webcam.\n"
              "On macOS, go to System Settings > Privacy & Security > Camera and allow access for your terminal or Python app.")
        sys.exit(1)
    detector = HandDetector(maxHands=1, detectionCon=0.7)
    filter_x, filter_y = LowPassFilter(ALPHA), LowPassFilter(ALPHA)
    prev_pos, prev_time, prev_vel = None, None, np.zeros(2)
    beat_machine = BeatStateMachine()
    last_trigger_time = 0
    print("Starting real-time conductor metronome. Press ESC to exit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Lost connection to the camera.\n"
                  "If you are on macOS, ensure camera permissions are granted for your terminal or Python app.")
            time.sleep(2)
            continue
        frame = cv2.flip(frame, 1)
        hands, frame = detector.findHands(frame, draw=True)
        curr_time = time.time()
        if hands:
            hand = hands[0]
            cx, cy = hand["center"]
            x, y = filter_x.filter(cx), filter_y.filter(cy)
            pos = np.array([x, y])
            if prev_pos is not None:
                dt = curr_time - prev_time if prev_time else 1e-3
                vel = (pos - prev_pos) / dt
                expected = beat_machine.get_expected()
                # Downbeat (min y, strong downward motion)
                if expected == 0 and prev_vel[1] < -VEL_THRESH and vel[1] > VEL_THRESH:
                    if curr_time - last_trigger_time > DEBOUNCE_TIME:
                        play_click(accent=True)
                        print("Beat 1 (Downbeat)")
                        beat_machine.next()
                        last_trigger_time = curr_time
                # Leftmost (min x, strong left motion)
                elif expected == 1 and prev_vel[0] > VEL_THRESH and vel[0] < -VEL_THRESH:
                    if curr_time - last_trigger_time > DEBOUNCE_TIME:
                        play_click()
                        print("Beat 2 (Left)")
                        beat_machine.next()
                        last_trigger_time = curr_time
                # Rightmost (max x, strong right motion)
                elif expected == 2 and prev_vel[0] < -VEL_THRESH and vel[0] > VEL_THRESH:
                    if curr_time - last_trigger_time > DEBOUNCE_TIME:
                        play_click()
                        print("Beat 3 (Right)")
                        beat_machine.next()
                        last_trigger_time = curr_time
                # Upbeat (max y, strong upward motion)
                elif expected == 3 and prev_vel[1] > VEL_THRESH and vel[1] < -VEL_THRESH:
                    if curr_time - last_trigger_time > DEBOUNCE_TIME:
                        play_click()
                        print("Beat 4 (Upbeat)")
                        beat_machine.next()
                        last_trigger_time = curr_time
                prev_vel = vel
            else:
                prev_vel = np.zeros(2)
            prev_pos, prev_time = pos, curr_time
            # Draw palm center
            cv2.circle(frame, (int(x), int(y)), 10, (0, 0, 255), -1)
            cv2.putText(frame, f"Beat: {beat_machine.state+1}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,0,0), 3)
            cv2.putText(frame, f"Vel: {int(vel[0])}, {int(vel[1])}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
        else:
            filter_x.state = None
            filter_y.state = None
            prev_pos = None
            prev_time = None
            prev_vel = np.zeros(2)
        cv2.imshow('Conductor Metronome', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
