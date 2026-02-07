import cv2
from datetime import datetime

def warmup_camera(cap):
    # Warm up the camera
    for _ in range(3):
        cap.read()

def take_photo():

    photoPath = ""
    # Open the default webcam (0 = built-in camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")
    warmup_camera(cap)
    ret, frame = cap.read()
    if ret:
        try:
            # Get current local date and time
            now = datetime.now()
            
            # Format it as a readable string
            formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error getting current datetime: {e}")
            return None, None

        cv2.imwrite("photo.jpg", frame)
        print("Photo saved as photo.jpg")
    else:
        print("Failed to capture image")
    

    cap.release()
take_photo()