# backend/app.py
import cv2
import threading
import numpy as np
import queue
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
camera_thread = None
pipeline_running = False
audio_queue = queue.Queue()

def start_camera_pipeline():
    global pipeline_running
    pipeline_running = True

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("ERROR: Cannot open camera!")
        return

    fx, fy = 0.3, 0.3
    while pipeline_running:
        ret, frame = cap.read()
        if not ret:
            continue
        # Simple red object detection (for demo)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0,120,70]), np.array([10,255,255])) | \
               cv2.inRange(hsv, np.array([170,120,70]), np.array([180,255,255]))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"]/M["m00"])
                cy = int(M["m01"]/M["m00"])
                cv2.circle(frame, (cx, cy), 10, (0,0,255), -1)
        cv2.imshow("Camera Pipeline", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    pipeline_running = False

@app.post("/start")
def start_pipeline():
    global camera_thread
    if camera_thread is None or not camera_thread.is_alive():
        camera_thread = threading.Thread(target=start_camera_pipeline, daemon=True)
        camera_thread.start()
        return {"status": "pipeline started"}
    return {"status": "already running"}

@app.post("/stop")
def stop_pipeline():
    global pipeline_running
    pipeline_running = False
    return {"status": "stopping"}
