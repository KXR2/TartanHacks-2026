import os
import threading
import time
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from scipy.io import wavfile
import sounddevice as sd
import uvicorn
import asyncio

# ================= CONFIG =================
FS = 44100
BLOCKSIZE = 256
BASE_DIR = os.path.dirname(__file__)
MEASURE_FOLDER = os.path.join(BASE_DIR, "measure_wavs")
FRONTEND_FILE = os.path.join(BASE_DIR, "index.html")

# ================= STATE =================
active_sounds = []
audio_lock = threading.Lock()
measure_audio = {}
beat = 0
measure = 1

# ================= LOAD MEASURE WAVS =================
for file_name in os.listdir(MEASURE_FOLDER):
    if file_name.startswith("measure_") and file_name.endswith(".wav"):
        measure_num = int(file_name.split("_")[1].split(".")[0])
        path = os.path.join(MEASURE_FOLDER, file_name)
        fs_data, data = wavfile.read(path)
        if data.dtype == np.int16:
            data = data.astype(np.float32) / 32768.0
        # Convert stereo to mono if necessary
        if data.ndim > 1:
            data = data[:,0]
        measure_audio[measure_num] = data
print(f"Loaded measure audio files: {list(measure_audio.keys())}")

# ================= CLICK SOUNDS =================
def generate_click(freq, ms, amp=0.6):
    t = np.linspace(0, ms/1000, int(FS*ms/1000), False)
    return (amp * np.sin(2*np.pi*freq*t)).astype(np.float32)

click_downbeat = generate_click(1500, 25)
click_other = generate_click(1000, 15)

# ================= AUDIO CALLBACK =================
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

def play(sound):
    with audio_lock:
        active_sounds.append([sound, 0])

# ================= START AUDIO STREAM =================
def start_audio_stream():
    sd.OutputStream(
        samplerate=FS,
        channels=1,
        blocksize=BLOCKSIZE,
        callback=audio_callback
    ).start()
    print("Audio stream started")

threading.Thread(target=start_audio_stream, daemon=True).start()

# ================= FASTAPI =================
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

clients = set()

async def broadcast_state():
    to_remove = set()
    for ws in clients:
        try:
            await ws.send_json({
                "measure": measure,
                "beat": beat,
                "timestamp": time.time()
            })
        except:
            to_remove.add(ws)
    for ws in to_remove:
        clients.remove(ws)

# ================= FRONTEND =================
@app.get("/")
def get_frontend():
    return FileResponse(FRONTEND_FILE)

# ================= WEBSOCKET =================
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await ws.receive_text()  # keep connection alive
    except:
        pass
    finally:
        clients.remove(ws)

# ================= BEAT ENDPOINTS =================
@app.post("/beat/downbeat")
async def downbeat():
    global beat, measure
    play(click_downbeat)
    beat = 1

    # Play measure audio every 4 measures: 1,5,9,...
    if (measure) % 4 == 0 and measure in measure_audio:
        play(measure_audio[measure + 1])
        print(f"Playing measure audio for measure {measure}")

    # Broadcast current state
    asyncio.create_task(broadcast_state())

    # Increment measure after broadcasting
    measure += 1
    return {"status": "ok"}

@app.post("/beat/other")
async def other_beat():
    global beat
    if beat == 0:
        return {"status": "ignored"}
    play(click_other)
    beat += 1
    asyncio.create_task(broadcast_state())
    return {"status": "ok"}

# ================= RUN SERVER =================
if __name__ == "__main__":
    print("Server running on http://127.0.0.1:8000")
    uvicorn.run("backend:app", host="127.0.0.1", port=8000)
