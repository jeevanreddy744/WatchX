from pathlib import Path
import cv2

# Find the first MP4 video inside data/videos
videos = list(Path("data/videos").glob("*.mp4"))

if not videos:
    raise FileNotFoundError("No MP4 video found in data/videos")

video_path = str(videos[0])

print("Loading video:", video_path)

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    raise RuntimeError("Could not open the video")

while True:
    ret, frame = cap.read()

    if not ret:
        break

    cv2.imshow("WatchX - CCTV Video", frame)

    # Press Q to stop the video
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()