import sounddevice as sd
import numpy as np
from pynput import keyboard
from scipy.io import wavfile
import threading
import time
import os

# ===================== CONFIG =====================
FS = 44100
BLOCKSIZE = 256
MEASURE_INTERVAL = 4
MEASURE_FOLDER = "measure_wavs"

# ===================== AUDIO STATE =====================
active_sounds = []
audio_lock = threading.Lock()

# ===================== AUDIO CALLBACK =====================
def audio_callback(outdata, frames, time_info, status):
    outdata[:] = 0

    with audio_lock:
        finished = []
        for i, sound in enumerate(active_sounds):
            data, pos = sound
            remaining = len(data) - pos
            n = min(remaining, frames)

            outdata[:n, 0] += data[pos:pos+n]
            sound[1] += n

            if sound[1] >= len(data):
                finished.append(i)

        for i in reversed(finished):
            active_sounds.pop(i)

# ===================== PLAY FUNCTION =====================
def play(sound):
    with audio_lock:
        active_sounds.append([sound, 0])

# ===================== CLICK GENERATION =====================
def generate_click(freq, ms, amp=0.6):
    t = np.linspace(0, ms / 1000, int(FS * ms / 1000), False)
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)

click_downbeat = generate_click(1500, 25)
click_other = generate_click(1000, 15)

# ===================== LOAD MEASURE WAVS =====================
measure_audio = {}
for i in range(1, 101):
    path = os.path.join(MEASURE_FOLDER, f"measure_{i}.wav")
    if not os.path.exists(path):
        continue
    fs, data = wavfile.read(path)
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    measure_audio[i] = data

# ===================== STATE =====================
last_time = 0
beat = 0

try:
    measure = int(input("Start measure (default 1): ") or 1)
except ValueError:
    measure = 1

start_measure = measure

# ===================== KEY HANDLER =====================
def on_press(key):
    global last_time, beat, measure
    now = time.time()

    if key == keyboard.Key.up:
        play(click_downbeat)
        beat = 1

        if (measure - start_measure) % MEASURE_INTERVAL == 0:
            if measure in measure_audio:
                play(measure_audio[measure])

        measure += 1
        last_time = now

    elif key == keyboard.Key.down:
        if beat == 0:
            return
        play(click_other)
        beat += 1
        last_time = now

    elif key == keyboard.Key.esc:
        return False

# ===================== MAIN =====================
print("Keyboard Conductor")
print("↑ = downbeat | ↓ = other beats | ESC = quit")

with sd.OutputStream(
    samplerate=FS,
    channels=1,
    blocksize=BLOCKSIZE,
    callback=audio_callback
):
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
