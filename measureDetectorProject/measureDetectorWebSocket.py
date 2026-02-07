import os
import threading
import time
import numpy as np
import cv2
import base64
from collections import deque
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sounddevice as sd
from scipy.io import wavfile
import asyncio

# ================= CONFIG =================
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 10
BOTTOM_REGION_HEIGHT = 250
MIN_TIME_BETWEEN_CLICKS = 0.3
SMOOTHING_FRAMES = 5
BLOCKSIZE = 256
FS = 44100

BASE_DIR = os.path.dirname(__file__)
MEASURE_WAV_PATH = os.path.join(BASE_DIR, "measure_wavs")
FRONTEND_PATH = BASE_DIR

# ================= GLOBAL STATE =================
pipeline_running = False
pipeline_thread = None
clients = set()
active_sounds = []
audio_lock = threading.Lock()

# ================= FASTAPI =================
app = FastAPI()

# Serve frontend and WAVs
app.mount("/frontend", StaticFiles(directory=FRONTEND_PATH), name="frontend")
app.mount("/measure_wavs", StaticFiles(directory=MEASURE_WAV_PATH), name="measure_wavs")

@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))

# ================= AUDIO FUNCTIONS =================
def play_sound(sound):
    with audio_lock:
        active_sounds.append([sound, 0])

def audio_callback(outdata, frames, time_info, status):
    outdata[:] = 0
    with audio_lock:
        finished = []
        for i, sound in enumerate(active_sounds):
            data, pos = sound
            n = min(len(data)-pos, frames)
            outdata[:n, 0] += data[pos:pos+n]
            sound[1] += n
            if sound[1] >= len(data):
                finished.append(i)
        for i in reversed(finished):
            active_sounds.pop(i)

# Start audio stream
stream = sd.OutputStream(
    samplerate=FS,
    channels=1,
    blocksize=BLOCKSIZE,
    callback=audio_callback
)
stream.start()

# ================= LOAD MEASURE AUDIO =================
measure_audio = {}
for file_name in os.listdir(MEASURE_WAV_PATH):
    if file_name.startswith("measure_") and file_name.endswith(".wav"):
        measure_num = int(file_name.split("_")[1].split(".")[0])
        path = os.path.join(MEASURE_WAV_PATH, file_name)
        fs_data, data = wavfile.read(path)
        if data.dtype == np.int16:
            data = data.astype(np.float32) / 32768.0
        if data.ndim > 1:
            data = data[:,0]  # stereo -> mono
        measure_audio[measure_num] = data
print(f"Loaded measure audio files: {list(measure_audio.keys())}")

# ================= HELPER FUNCTIONS =================
def encode_frame(frame) -> str:
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")

async def broadcast_state(measure_count, downbeat_triggered, frame_encoded):
    """Send state to all WebSocket clients"""
    to_remove = set()
    for ws in clients:
        try:
            await ws.send_json({
                "type": "frame",
                "measure_count": measure_count,
                "downbeat": downbeat_triggered,
                "frame": frame_encoded
            })
        except:
            to_remove.add(ws)
    for ws in to_remove:
        clients.remove(ws)

# ---------------- CAMERA OPEN ----------------
def open_camera():
    for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            print(f"Camera opened using backend {backend}")
            return cap
        cap.release()
    return None

# ================= METRONOME PIPELINE =================
def metronome_pipeline(loop):
    global pipeline_running

    cap = open_camera()
    if cap is None:
        for ws in clients:
            asyncio.run_coroutine_threadsafe(
                ws.send_json({"type": "error", "message": "Could not open webcam"}),
                loop
            )
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
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            downbeat_triggered = False

            # RED DETECTION
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_red1 = np.array([0,120,70])
            upper_red1 = np.array([10,255,255])
            lower_red2 = np.array([170,120,70])
            upper_red2 = np.array([180,255,255])
            mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.GaussianBlur(mask, (5,5), 0)

            contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                cnt = max(contours, key=cv2.contourArea)
                if cv2.contourArea(cnt) > 200:
                    hull = cv2.convexHull(cnt)
                    bottommost = tuple(hull[hull[:,:,1].argmax()][0])
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
                                prev_time = now
                                measure_count += 1

                                # Play measure audio every 4 measures
                                if (measure_count - 1) % 4 == 0 and measure_count in measure_audio:
                                    play_sound(measure_audio[measure_count])
                                    print(f"Playing measure audio for measure {measure_count}")

            # Overlay
            cv2.rectangle(frame, (0, FRAME_HEIGHT - BOTTOM_REGION_HEIGHT),
                          (FRAME_WIDTH, FRAME_HEIGHT), (200,200,200), 2)
            cv2.putText(frame, f"Measures: {measure_count}", (10,40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

            # Broadcast via main loop safely
            asyncio.run_coroutine_threadsafe(
                broadcast_state(measure_count, downbeat_triggered, encode_frame(frame)),
                loop
            )
            time.sleep(1/FPS)

    finally:
        cap.release()

# ================= WEBSOCKET =================
@app.websocket("/ws/metronome")
async def websocket_endpoint(ws: WebSocket):
    global pipeline_running, pipeline_thread
    await ws.accept()
    clients.add(ws)
    print("WebSocket connected")

    # Pass main loop to pipeline thread
    main_loop = asyncio.get_running_loop()

    try:
        while True:
            msg = await ws.receive_text()
            if msg == "start" and not pipeline_running:
                pipeline_running = True
                pipeline_thread = threading.Thread(target=metronome_pipeline, args=(main_loop,), daemon=True)
                pipeline_thread.start()
                await ws.send_json({"type":"status", "running":True})
            elif msg == "stop" and pipeline_running:
                pipeline_running = False
                if pipeline_thread:
                    pipeline_thread.join()
                await ws.send_json({"type":"status", "running":False})

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        pipeline_running = False
        if pipeline_thread:
            pipeline_thread.join()

    except Exception as e:
        print("WebSocket error:", e)
        pipeline_running = False
        if pipeline_thread:
            pipeline_thread.join()
        await ws.send_json({"type":"error","message":str(e)})

# ================= RUN =================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8001)
