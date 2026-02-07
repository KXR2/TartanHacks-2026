# generate_measure_wavs.py
import pyttsx3
import os

# ---------------- CONFIG ----------------
MEASURE_FOLDER = "measure_wavs"
os.makedirs(MEASURE_FOLDER, exist_ok=True)

# ---------------- INIT TTS ----------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # speaking rate

# ---------------- GENERATE WAV FILES ----------------
for measure in range(101, 301):
    filename = os.path.join(MEASURE_FOLDER, f"measure_{measure}.wav")
    print(f"Generating {filename}...")
    engine.save_to_file(f"Measure {measure}", filename)
    
engine.runAndWait()
print("All measure files generated!")
