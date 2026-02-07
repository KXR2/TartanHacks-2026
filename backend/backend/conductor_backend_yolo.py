# conductor_backend_yolo.py
import cv2
import numpy as np
from ultralytics import YOLO
import sounddevice as sd
import asyncio
import threading
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import uvicorn
import time

# ---------------- CONFIG ----------------
FS = 44100
CLICK_DURATION = 0.02
CLICK_FREQ = 1500
SMOOTHING = 5
MIN_FRAMES_BETWEEN_CLICKS = 5

# ---------------- CLICK SOUND ----------------
t = np.linspace(0, CLICK_DURATION, int(FS * CLICK_DURATION), False)
click_sound = (0.5 * np.sin(2 * np.pi * CLICK_FREQ * t)).astype(np.float32)
def play_click():
    sd.play(click_sound, FS, blocking=False)

# ---------------- FastAPI + WebSocket ----------------
app = FastAPI()
clients = set()
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await asyncio.sleep(0.1)
    except:
        pass
    finally:
        clients.remove(ws)

async def broadcast(message: str):
    remove = set()
    for ws in clients:
        try:
            await ws.send_text(message)
        except:
            remove.add(ws)
    clients.difference_update(remove)

def emit_message(message):
    threading.Thread(target=lambda: asyncio.run(broadcast(message)), daemon=True).start()

# ---------------- Serve HTML dashboard ----------------
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# ---------------- YOLO Tracker ----------------
def run_yolo_tracker():
    model = YOLO("yolov8n.pt")
    y_history = []
    x_history = []
    measure_number = 1
    current_beat = 0
    last_click_frame = -MIN_FRAMES_BETWEEN_CLICKS
    frame_counter = 0

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    x_center_range = (frame_width*0.4, frame_width*0.6)

    def is_relative_extrema(history, idx):
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

        phone_boxes = [b for i, b in enumerate(boxes) if int(classes[i]) == 67]

        if phone_boxes:
            b = max(phone_boxes, key=lambda bb: (bb[2]-bb[0])*(bb[3]-bb[1]))
            x1, y1, x2, y2 = b
            baton_x = (x1+x2)/2
            baton_y = (y1+y2)/2

            x_history.append(baton_x)
            y_history.append(baton_y)
            if len(x_history) > SMOOTHING: x_history.pop(0)
            if len(y_history) > SMOOTHING: y_history.pop(0)
            smooth_x = sum(x_history)/len(x_history)
            smooth_y = sum(y_history)/len(y_history)

            if frame_counter > 2 + last_click_frame:
                y_ext = is_relative_extrema(y_history, -2)
                x_ext = is_relative_extrema(x_history, -2)
                if y_ext or x_ext:
                    play_click()
                    last_click_frame = frame_counter
                    current_beat += 1

                    if y_history[-2] == min(y_history[-3:]) and x_center_range[0] < smooth_x < x_center_range[1]:
                        print(f"Downbeat (new measure) {measure_number}")
                        emit_message(f"downbeat:{measure_number}")
                        measure_number += 1
                        current_beat = 1
                    else:
                        print(f"Beat {current_beat}")
                        emit_message(f"beat:{current_beat}")

            # Draw visuals
            x1, y1, x2, y2 = map(int, b)
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
            cv2.circle(frame, (int(smooth_x), int(smooth_y)), 5, (0,0,255), -1)

        cv2.imshow("Conductor Tracker", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

# ---------------- Run YOLO tracker in a thread ----------------
threading.Thread(target=run_yolo_tracker, daemon=True).start()

# ---------------- Run FastAPI ----------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
