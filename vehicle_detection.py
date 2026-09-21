import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo11n.pt")

# Video input
video_path = "data/videos/xyz.mp4.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    raise RuntimeError("Could not open the video")

print("WatchX: Processing video...")

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Detect and track vehicles
    results = model.track(
        frame,
        persist=True,
        verbose=False
    )

    # Draw detection results
    annotated_frame = results[0].plot()

    # Display video
    cv2.imshow("WatchX - Vehicle Detection", annotated_frame)

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("WatchX: Processing completed.")