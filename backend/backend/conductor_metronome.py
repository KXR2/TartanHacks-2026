import cv2
import numpy as np
import time
import platform

# --- Config ---
ALPHA = 0.3             # Low-pass filter smoothing
DEBOUNCE_TIME = 0.4    # Seconds between beats
VEL_THRESH = 18         # Minimum velocity to consider a beat

# --- Audio ---
def play_click(accent=False):
    if platform.system() == "Windows":
        import winsound
        freq = 880 if accent else 440
        winsound.Beep(freq, 25)  # 50 ms beep
    else:
        # fallback for macOS/Linux
        print("Click!" if not accent else "Accent Click!")

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
    if not cap.isOpened():
        print("Cannot open camera")
        return

    # Filters for smoothing
    filter_x, filter_y = LowPassFilter(ALPHA), LowPassFilter(ALPHA)
    prev_pos, prev_time, prev_vel = None, None, np.zeros(2)
    beat_machine = BeatStateMachine()
    last_trigger_time = 0

    # HSV color range for red glove
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    print("Starting conductor metronome. Press ESC to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            continue

        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Mask red glove
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        # Find largest contour
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                x, y = filter_x.filter(cx), filter_y.filter(cy)
                pos = np.array([x, y])
                curr_time = time.time()

                # Initialize velocity to zero first
                vel = np.zeros(2)

                if prev_pos is not None and prev_time is not None:
                    dt = curr_time - prev_time
                    if dt > 0:
                        vel = (pos - prev_pos) / dt
                    expected = beat_machine.get_expected()

                    # Beat detection logic
                    if expected == 0 and prev_vel[1] < -VEL_THRESH and vel[1] > VEL_THRESH:
                        if curr_time - last_trigger_time > DEBOUNCE_TIME:
                            play_click(accent=True)
                            print("Beat 1 (Downbeat)")
                            beat_machine.next()
                            last_trigger_time = curr_time
                    elif expected == 1 and prev_vel[0] > VEL_THRESH and vel[0] < -VEL_THRESH:
                        if curr_time - last_trigger_time > DEBOUNCE_TIME:
                            play_click()
                            print("Beat 2 (Left)")
                            beat_machine.next()
                            last_trigger_time = curr_time
                    elif expected == 2 and prev_vel[0] < -VEL_THRESH and vel[0] > VEL_THRESH:
                        if curr_time - last_trigger_time > DEBOUNCE_TIME:
                            play_click()
                            print("Beat 3 (Right)")
                            beat_machine.next()
                            last_trigger_time = curr_time
                    elif expected == 3 and prev_vel[1] > VEL_THRESH and vel[1] < -VEL_THRESH:
                        if curr_time - last_trigger_time > DEBOUNCE_TIME:
                            play_click()
                            print("Beat 4 (Upbeat)")
                            beat_machine.next()
                            last_trigger_time = curr_time

                    prev_vel = vel

                prev_pos, prev_time = pos, curr_time

                # Draw palm center
                cv2.circle(frame, (int(x), int(y)), 10, (0, 0, 255), -1)
                cv2.putText(frame, f"Beat: {beat_machine.state+1}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,0,0), 3)
                cv2.putText(frame, f"Vel: {int(vel[0])}, {int(vel[1])}", (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

        else:
            # Reset filters and positions when no hand detected
            filter_x.state = None
            filter_y.state = None
            prev_pos = None
            prev_time = None
            prev_vel = np.zeros(2)

        cv2.imshow('Conductor Metronome', frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
