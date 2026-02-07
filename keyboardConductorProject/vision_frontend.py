# vision_frontend.py
import cv2
import numpy as np
import time
import requests

ALPHA = 0.3
DEBOUNCE_TIME = 0.25
VEL_THRESH = 18
BEATS_PER_MEASURE = 4
BACKEND_URL = "http://127.0.0.1:8001/click/"

class LowPassFilter:
    def __init__(self, alpha):
        self.alpha = alpha
        self.state = None
    def apply(self, val):
        if self.state is None:
            self.state = val
        else:
            self.state = self.alpha*val + (1-self.alpha)*self.state
        return self.state
    def reset(self):
        self.state = None

class BeatTracker:
    def __init__(self):
        self.beat = 0
        self.measure = 1
    def is_downbeat(self):
        return self.beat==0
    def advance(self):
        self.beat += 1
        if self.beat >= BEATS_PER_MEASURE:
            self.beat = 0
            self.measure += 1

def send_beat(accent):
    try:
        requests.post(BACKEND_URL + str(accent))
    except:
        pass  # ignore failures for now

def main():
    cap = cv2.VideoCapture(0)
    fx = LowPassFilter(ALPHA)
    fy = LowPassFilter(ALPHA)
    tracker = BeatTracker()
    prev_pos, prev_time, prev_vel = None, None, np.zeros(2)
    last_trigger = 0

    lower1 = np.array([0,120,70])
    upper1 = np.array([10,255,255])
    lower2 = np.array([170,120,70])
    upper2 = np.array([180,255,255])

    while True:
        ok, frame = cap.read()
        if not ok:
            continue
        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)
        contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"]!=0:
                cx = fx.apply(int(M["m10"]/M["m00"]))
                cy = fy.apply(int(M["m01"]/M["m00"]))
                pos = np.array([cx,cy])
                now = time.time()
                vel = np.zeros(2)
                if prev_pos is not None and prev_time is not None:
                    dt = now - prev_time
                    if dt>0:
                        vel = (pos - prev_pos)/dt
                    if prev_vel[1] < -VEL_THRESH and vel[1] > VEL_THRESH:
                        if now - last_trigger > DEBOUNCE_TIME:
                            send_beat(tracker.is_downbeat())
                            tracker.advance()
                            last_trigger = now
                prev_pos, prev_time, prev_vel = pos, now, vel

        else:
            fx.reset()
            fy.reset()
            prev_pos = None
            prev_time = None
            prev_vel[:] = 0

        cv2.imshow("Conductor Frontend", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    main()
