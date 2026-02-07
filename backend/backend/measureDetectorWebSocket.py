import cv2
import numpy as np
import time
import base64
import threading
from collections import deque
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
app = FastAPI()
# Path to WAV files
measure_wavs_path = os.path.join(os.path.dirname(__file__), "measure_wavs")

# Serve /measure_wavs/* over HTTP
app.mount("/measure_wavs", StaticFiles(directory=measure_wavs_path), name="measure_wavs")

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))
# -------------------- CONFIG --------------------
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 10
BOTTOM_REGION_HEIGHT = 250
MIN_TIME_BETWEEN_CLICKS = 0.3
SMOOTHING_FRAMES = 5

# -------------------- GLOBAL STATE --------------------
pipeline_running = False
pipeline_thread = None

# -------------------- HELPERS --------------------
def encode_frame(frame) -> str:
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")

def open_camera():
    """Try multiple backends to open camera safely"""
    for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            print(f"Camera opened using backend {backend}")
            return cap
        else:
            cap.release()
    return None

# -------------------- PIPELINE --------------------
def metronome_pipeline(send_json):
    global pipeline_running

    cap = open_camera()
    if cap is None:
        # Send error to frontend and stop pipeline
        send_json({
            "type": "error",
            "message": "Could not open webcam. Check camera permissions or other apps using it."
        })
        pipeline_running = False
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    wrist_history = deque(maxlen=SMOOTHING_FRAMES)
    prev_time = None
    in_bottom_region = False
    measure_count = 1

    try:
        while pipeline_running:
            ret, frame = cap.read()
            if not ret:
                # If camera fails mid-loop
                send_json({
                    "type": "error",
                    "message": "Camera read failed."
                })
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)

            # ---------------- RED OBJECT DETECTION ----------------
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_red1 = np.array([0, 120, 70])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 120, 70])
            upper_red2 = np.array([180, 255, 255])
            mask = cv2.inRange(hsv, lower_red1, upper_red1) | \
                   cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.GaussianBlur(mask, (5, 5), 0)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            downbeat_triggered = False

            if contours:
                cnt = max(contours, key=cv2.contourArea)
                if cv2.contourArea(cnt) > 200:
                    hull = cv2.convexHull(cnt)
                    bottommost = tuple(hull[hull[:, :, 1].argmax()][0])
                    wrist_history.append(bottommost)

                    if len(wrist_history) >= 2:
                        smoothed_y = int(np.mean([p[1] for p in wrist_history]))
                        prev_y = int(np.mean([p[1] for p in list(wrist_history)[:-1]]))
                        dy = smoothed_y - prev_y

                        now_in_bottom = smoothed_y > FRAME_HEIGHT - BOTTOM_REGION_HEIGHT
                        new_downbeat = now_in_bottom and not in_bottom_region and dy > 0
                        in_bottom_region = now_in_bottom

                        if new_downbeat:
                            now = time.perf_counter()
                            if prev_time is None or (now - prev_time) > MIN_TIME_BETWEEN_CLICKS:
                                downbeat_triggered = True
                                measure_count += 1
                                prev_time = now

            # ---------------- OVERLAY ----------------
            cv2.rectangle(
                frame,
                (0, FRAME_HEIGHT - BOTTOM_REGION_HEIGHT),
                (FRAME_WIDTH, FRAME_HEIGHT),
                (200, 200, 200),
                2
            )

            cv2.putText(
                frame,
                f"Measures: {measure_count}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2
            )

            # ---------------- SEND FRAME ----------------
            send_json({
                "type": "frame",
                "frame": encode_frame(frame),
                "measure_count": measure_count,
                "downbeat": downbeat_triggered
            })

            time.sleep(1 / FPS)

    finally:
        cap.release()

# -------------------- WEBSOCKET --------------------
@app.websocket("/ws/metronome")
async def websocket_endpoint(ws: WebSocket):
    global pipeline_running, pipeline_thread

    await ws.accept()
    print("WebSocket connected")

    # helper to send JSON safely from threads
    def send_json_threadsafe(data):
        import asyncio
        asyncio.run(ws.send_json(data))

    try:
        while True:
            msg = await ws.receive_text()

            if msg == "start" and not pipeline_running:
                print("Starting pipeline")
                pipeline_running = True
                pipeline_thread = threading.Thread(
                    target=metronome_pipeline,
                    args=(send_json_threadsafe,),
                    daemon=True
                )
                pipeline_thread.start()
                await ws.send_json({"type": "status", "running": True})

            elif msg == "stop" and pipeline_running:
                print("Stopping pipeline")
                pipeline_running = False
                if pipeline_thread:
                    pipeline_thread.join()
                await ws.send_json({"type": "status", "running": False})

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        pipeline_running = False

    except Exception as e:
        print("WebSocket error:", e)
        pipeline_running = False
        await ws.send_json({"type": "error", "message": str(e)})
