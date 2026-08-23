import cv2
import numpy as np

def detect_face_center_x(video_path: str, sample_frames: int = 10) -> float:
    """Detect main face center X ratio (0.0 to 1.0) using OpenCV Haar cascade."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0.5

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    if width <= 0:
        cap.release()
        return 0.5

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    x_centers = []

    step = max(1, total_frames // sample_frames)
    for i in range(0, total_frames, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            x_centers.append((x + w / 2.0) / width)

    cap.release()

    if x_centers:
        return float(np.median(x_centers))
    return 0.5

def get_crop_filter(aspect_ratio: str, face_center_x: float = 0.5) -> str:
    """Generate FFmpeg crop filter for target aspect ratio based on detected face position."""
    if aspect_ratio == "9:16":
        # Target crop 9:16 vertical (e.g. ih*9/16 : ih)
        # crop=w=ih*9/16:h=ih:x='min(max(0, iw*face_center - w/2), iw-w)':y=0
        return f"crop=w='ih*9/16':h='ih':x='min(max(0, iw*{face_center_x:.2f} - ih*9/32), iw-ih*9/16)':y=0,scale=1080:1920"
    elif aspect_ratio == "1:1":
        return f"crop=w='ih':h='ih':x='min(max(0, iw*{face_center_x:.2f} - ih/2), iw-ih)':y=0,scale=1080:1080"
    else: # "16:9"
        return "scale=1920:1080"
