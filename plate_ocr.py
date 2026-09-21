
import cv2
import re
import time
import sys
import os
import csv
from pathlib import Path
from collections import defaultdict
from ultralytics import YOLO
from fast_plate_ocr import LicensePlateRecognizer

# ============================================================
# WATCHX - ACCURATE VEHICLE + NUMBER PLATE OCR
# ============================================================

# ============================================================
# WATCHX SHARED DATA DIRECTORY
# ============================================================
# Both the OCR engine and dashboard use the same folder.
# The desktop application can override this with WATCHX_DATA_DIR.

BASE_DIR = Path(__file__).resolve().parent

if os.environ.get("WATCHX_DATA_DIR"):
    DATA_DIR = Path(os.environ["WATCHX_DATA_DIR"]).resolve()
else:
    DATA_DIR = BASE_DIR / "watchx_data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_DIR = DATA_DIR / "videos"
EVIDENCE_DIR = DATA_DIR / "evidence"

VEHICLE_EVIDENCE_DIR = EVIDENCE_DIR / "vehicles"
PLATE_EVIDENCE_DIR = EVIDENCE_DIR / "plates"

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
VEHICLE_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
PLATE_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = str(DATA_DIR / "watchx_records.csv")

VIDEO_PATH = (
    sys.argv[1]
    if len(sys.argv) > 1
    else str(VIDEO_DIR / "my_traffic_video.MOV")
)

VEHICLE_MODEL_PATH = str(BASE_DIR / "yolo11n.pt")
PLATE_MODEL_PATH = str(BASE_DIR / "license_plate_detector.pt")

VEHICLE_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
PLATE_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

# Balanced for a laptop: enough plate detail without making
# the whole application unnecessarily slow.
FRAME_SKIP = 3
VEHICLE_IMGSZ = 640
PLATE_IMGSZ = 640
VEHICLE_CONF = 0.30
PLATE_CONF = 0.28
OCR_INTERVAL = 2
OCR_CONF_MIN = 0.20

# Plate geometry filters. These are important because the old
# version sometimes treated wheels/headlights as plates.
MIN_PLATE_W = 14
MIN_PLATE_H = 6
MIN_ASPECT = 1.35
MAX_ASPECT = 7.5
MIN_VEHICLE_OVERLAP = 0.35

# Multi-frame stabilization.
HISTORY_SIZE = 15
MIN_STABLE_VOTES = 2
STABLE_SCORE = 1.00
MAX_EDIT_DISTANCE = 1
STALE_FRAMES = 180

VEHICLE_CLASSES = [2, 3, 5, 7]
VEHICLE_NAMES = {2: "Car", 3: "Motorcycle", 5: "Bus", 7: "Truck"}

print("=" * 64)
print("WATCHX - AI VEHICLE INVESTIGATION")
print("VEHICLE + PLATE DETECTION + OCR + TRACKING")
print("=" * 64)

print("Loading vehicle detector...")
vehicle_model = YOLO(VEHICLE_MODEL_PATH)

print("Loading license plate detector...")
plate_model = YOLO(PLATE_MODEL_PATH)

print("Loading Fast Plate OCR...")
plate_ocr = LicensePlateRecognizer("cct-s-v2-global-model")
print("All models loaded successfully.\n")

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

SOURCE_FPS = cap.get(cv2.CAP_PROP_FPS)
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
TOTAL_FRAMES = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Progress sent to the WatchX desktop application.
last_progress = -1

print("WatchX started.")
print(f"Video: {VIDEO_PATH}")
print(f"Resolution: {WIDTH} x {HEIGHT}")
print(f"Source FPS: {SOURCE_FPS:.2f}")
print("Background processing started.\n", flush=True)

# ============================================================
# CSV RECORDING
# ============================================================

csv_file = open(CSV_PATH, "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
csv_writer.writerow([
    "time_seconds",
    "frame",
    "vehicle_id",
    "vehicle_type",
    "plate",
    "ocr_confidence",
    "votes"
])
csv_file.flush()

vehicle_records = defaultdict(lambda: {
    "readings": [],
    "best_plate": "",
    "best_conf": 0.0,
    "votes": 0,
    "score": 0.0,
    "last_seen": 0,
    "recorded_plate": "",
    "best_plate_box": None
})

frame_number = 0
processed_frames = 0
start_time = time.time()


# ============================================================
# TEXT HELPERS
# ============================================================

def clean_text(text):
    if text is None:
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(text).upper())


def normalize_plate(text):
    """
    Position-aware correction for common OCR confusions.
    Supports the common 9/10 character Indian registration pattern.
    """
    text = clean_text(text)

    if len(text) not in (9, 10):
        return text

    chars = list(text)

    digit_map = {
        "O": "0",
        "Q": "0",
        "D": "0",
        "I": "1",
        "L": "1",
        "Z": "2",
        "S": "5",
        "G": "6",
        "B": "8"
    }

    letter_map = {
        "0": "O",
        "1": "I",
        "2": "Z",
        "5": "S",
        "6": "G",
        "8": "B"
    }

    # First two characters should be letters.
    for i in (0, 1):
        if chars[i] in letter_map:
            chars[i] = letter_map[chars[i]]

    # Next two should be digits.
    for i in (2, 3):
        if chars[i] in digit_map:
            chars[i] = digit_map[chars[i]]

    # Last four should be digits.
    for i in range(len(chars) - 4, len(chars)):
        if chars[i] in digit_map:
            chars[i] = digit_map[chars[i]]

    return "".join(chars)


def valid_indian_plate(text):
    text = clean_text(text)

    if not (9 <= len(text) <= 10):
        return False

    return bool(
        re.fullmatch(
            r"[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}",
            text
        )
    )


def edit_distance(a, b):
    if a == b:
        return 0

    if not a:
        return len(b)

    if not b:
        return len(a)

    previous = list(range(len(b) + 1))

    for i, ca in enumerate(a, 1):
        current = [i]

        for j, cb in enumerate(b, 1):
            current.append(
                min(
                    current[j - 1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (ca != cb)
                )
            )

        previous = current

    return previous[-1]


# ============================================================
# BOX HELPERS
# ============================================================

def clamp_box(box, frame):
    h, w = frame.shape[:2]

    x1, y1, x2, y2 = [
        int(v) for v in box
    ]

    x1 = max(0, min(x1, w - 1))
    y1 = max(0, min(y1, h - 1))
    x2 = max(0, min(x2, w - 1))
    y2 = max(0, min(y2, h - 1))

    return x1, y1, x2, y2


def center(box):
    x1, y1, x2, y2 = box
    return (
        (x1 + x2) // 2,
        (y1 + y2) // 2
    )


def intersection_over_plate(plate_box, vehicle_box):
    px1, py1, px2, py2 = plate_box
    vx1, vy1, vx2, vy2 = vehicle_box

    ix1 = max(px1, vx1)
    iy1 = max(py1, vy1)
    ix2 = min(px2, vx2)
    iy2 = min(py2, vy2)

    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0

    intersection = (
        (ix2 - ix1) *
        (iy2 - iy1)
    )

    plate_area = max(
        1,
        (px2 - px1) *
        (py2 - py1)
    )

    return intersection / plate_area


# ============================================================
# PLATE CROP / IMAGE PREPARATION
# ============================================================

def crop_plate(frame, box):
    x1, y1, x2, y2 = box

    h, w = frame.shape[:2]

    plate_width = x2 - x1
    plate_height = y2 - y1

    # Small padding only.
    # Too much background makes OCR worse.
    pad_x = max(
        2,
        int(plate_width * 0.08)
    )

    pad_y = max(
        2,
        int(plate_height * 0.12)
    )

    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x)
    y2 = min(h, y2 + pad_y)

    crop = frame[y1:y2, x1:x2]

    if crop.size == 0:
        return None

    return crop


def prepare_ocr_image(crop):
    if crop is None or crop.size == 0:
        return None

    h, w = crop.shape[:2]

    if w < 12 or h < 6:
        return None

    # Enlarge small number plates.
    crop = cv2.resize(
        crop,
        None,
        fx=4.0,
        fy=4.0,
        interpolation=cv2.INTER_CUBIC
    )

    # Mild sharpening.
    blurred = cv2.GaussianBlur(
        crop,
        (0, 0),
        1.0
    )

    sharpened = cv2.addWeighted(
        crop,
        1.25,
        blurred,
        -0.25,
        0
    )

    # Mild local contrast enhancement.
    lab = cv2.cvtColor(
        sharpened,
        cv2.COLOR_BGR2LAB
    )

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=1.2,
        tileGridSize=(8, 8)
    )

    l = clahe.apply(l)

    enhanced = cv2.merge(
        (l, a, b)
    )

    enhanced = cv2.cvtColor(
        enhanced,
        cv2.COLOR_LAB2BGR
    )

    # Fast Plate OCR expects RGB.
    return cv2.cvtColor(
        enhanced,
        cv2.COLOR_BGR2RGB
    )


# ============================================================
# OCR
# ============================================================

def run_ocr(crop):
    rgb = prepare_ocr_image(crop)

    if rgb is None:
        return "", 0.0

    try:
        predictions = plate_ocr.run(
            [rgb],
            return_confidence=True
        )
    except Exception as e:
        print("OCR error:", e)
        return "", 0.0

    if not predictions:
        return "", 0.0

    prediction = predictions[0]

    text = clean_text(
        getattr(
            prediction,
            "plate",
            ""
        )
    )

    confidence = 0.0

    char_probs = getattr(
        prediction,
        "char_probs",
        None
    )

    if char_probs is not None:
        try:
            values = [
                float(v)
                for v in char_probs
            ]

            if values:
                confidence = (
                    sum(values) /
                    len(values)
                )

        except Exception:
            pass

    if confidence <= 0:
        try:
            confidence = float(
                getattr(
                    prediction,
                    "confidence",
                    0.0
                )
            )
        except Exception:
            confidence = 0.0

    text = normalize_plate(text)

    if not valid_indian_plate(text):
        return "", confidence

    if confidence < OCR_CONF_MIN:
        return "", confidence

    return text, confidence


# ============================================================
# MULTI-FRAME OCR VOTING
# ============================================================

def add_reading(
    vehicle_id,
    text,
    confidence,
    frame_no
):
    record = vehicle_records[
        vehicle_id
    ]

    record["last_seen"] = frame_no

    # Group very similar OCR results together.
    canonical = None

    for old_text, _, _ in record["readings"]:
        if (
            len(old_text) == len(text)
            and
            edit_distance(
                old_text,
                text
            ) <= MAX_EDIT_DISTANCE
        ):
            canonical = old_text
            break

    if canonical is None:
        canonical = text

    record["readings"].append(
        (
            canonical,
            float(confidence),
            frame_no
        )
    )

    if len(record["readings"]) > HISTORY_SIZE:
        record["readings"] = (
            record["readings"][
                -HISTORY_SIZE:
            ]
        )

    # Confidence-weighted voting.
    scores = defaultdict(float)
    counts = defaultdict(int)
    best_conf = defaultdict(float)

    for plate, conf, _ in record["readings"]:
        counts[plate] += 1

        scores[plate] += (
            max(0.15, conf) ** 1.5
        )

        best_conf[plate] = max(
            best_conf[plate],
            conf
        )

    if not scores:
        return

    best_plate = max(
        scores.keys(),
        key=lambda p: (
            scores[p],
            best_conf[p],
            counts[p]
        )
    )

    record["best_plate"] = best_plate
    record["best_conf"] = best_conf[
        best_plate
    ]
    record["votes"] = counts[
        best_plate
    ]
    record["score"] = scores[
        best_plate
    ]


def get_stable(vehicle_id):
    if vehicle_id not in vehicle_records:
        return "", 0.0, 0

    record = vehicle_records[
        vehicle_id
    ]

    if record["votes"] < MIN_STABLE_VOTES:
        return "", 0.0, 0

    if record.get("score", 0.0) < STABLE_SCORE:
        return "", 0.0, 0

    return (
        record["best_plate"],
        record["best_conf"],
        record["votes"]
    )


# ============================================================
# SAVE EVIDENCE IMAGES
# ============================================================

def save_evidence_images(vehicle, frame_no, frame, plate_box, plate_text):
    """
    Save the vehicle frame crop and the detected number-plate crop.

    These files are linked to the same Vehicle ID and frame number
    used by the CSV record, so the dashboard can later display
    the correct evidence for an investigation.
    """
    vehicle_id = vehicle["id"]

    safe_plate = clean_text(plate_text)
    if not safe_plate:
        safe_plate = "UNKNOWN"

    # Save vehicle crop.
    vehicle_box = clamp_box(vehicle["box"], frame)
    vx1, vy1, vx2, vy2 = vehicle_box

    vehicle_crop = frame[vy1:vy2, vx1:vx2]

    vehicle_image_path = (
        VEHICLE_EVIDENCE_DIR
        / f"vehicle_{vehicle_id}_frame_{frame_no}.jpg"
    )

    if vehicle_crop.size > 0:
        cv2.imwrite(
            str(vehicle_image_path),
            vehicle_crop,
            [cv2.IMWRITE_JPEG_QUALITY, 95]
        )

    # Save number-plate crop.
    plate_image_path = (
        PLATE_EVIDENCE_DIR
        / f"plate_{vehicle_id}_frame_{frame_no}_{safe_plate}.jpg"
    )

    if plate_box is not None:
        plate_crop = crop_plate(frame, plate_box)

        if plate_crop is not None and plate_crop.size > 0:
            cv2.imwrite(
                str(plate_image_path),
                plate_crop,
                [cv2.IMWRITE_JPEG_QUALITY, 98]
            )

    print(
        f"[EVIDENCE SAVED] Vehicle ID: {vehicle_id} | "
        f"Vehicle image: {vehicle_image_path.name} | "
        f"Plate image: {plate_image_path.name}",
        flush=True
    )


# ============================================================
# SAVE STABLE RESULT
# ============================================================

def record_stable(vehicle, frame_no, frame):
    vehicle_id = vehicle["id"]

    plate, confidence, votes = (
        get_stable(vehicle_id)
    )

    if not plate:
        return

    record = vehicle_records[
        vehicle_id
    ]

    # Don't save the same vehicle/plate repeatedly.
    if record["recorded_plate"] == plate:
        return

    record["recorded_plate"] = plate

    # Save evidence at the same moment that the stable CSV
    # investigation record is created.
    save_evidence_images(
        vehicle,
        frame_no,
        frame,
        record.get("best_plate_box"),
        plate
    )

    seconds = (
        frame_no / SOURCE_FPS
        if SOURCE_FPS
        else 0.0
    )

    csv_writer.writerow([
        f"{seconds:.2f}",
        frame_no,
        vehicle_id,
        vehicle["name"],
        plate,
        f"{confidence:.2f}",
        votes
    ])

    csv_file.flush()

    print(
        f"[RECORDED] Vehicle ID: {vehicle_id} | "
        f"{vehicle['name']} | "
        f"Plate: {plate} | "
        f"Confidence: {confidence:.2f} | "
        f"Votes: {votes}"
    )


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        # ------------------------------------------------------
        # Grab frames efficiently.
        # ------------------------------------------------------

        ret = True

        for _ in range(FRAME_SKIP):
            ret = cap.grab()

            if not ret:
                break

        if not ret:
            break

        ret, frame = cap.retrieve()

        if not ret:
            break

        frame_number += FRAME_SKIP
        processed_frames += 1

        # ======================================================
        # VEHICLE DETECTION + TRACKING
        # ======================================================

        try:

            results = vehicle_model.track(
                frame,
                persist=True,
                classes=VEHICLE_CLASSES,
                conf=VEHICLE_CONF,
                imgsz=VEHICLE_IMGSZ,
                verbose=False,
                tracker="bytetrack.yaml"
            )

            result = results[0]

        except Exception as e:

            print(
                "Vehicle detection error:",
                e
            )

            continue

        current_vehicles = []

        if result.boxes is not None:

            for box in result.boxes:

                try:

                    class_id = int(
                        box.cls[0]
                    )

                    if class_id not in VEHICLE_CLASSES:
                        continue

                    vehicle_box = clamp_box(
                        box.xyxy[0].tolist(),
                        frame
                    )

                    x1, y1, x2, y2 = (
                        vehicle_box
                    )

                    if x2 <= x1 or y2 <= y1:
                        continue

                    vehicle_id = -1

                    if box.id is not None:

                        vehicle_id = int(
                            box.id[0]
                        )

                    vehicle_conf = float(
                        box.conf[0]
                    )

                    current_vehicles.append(
                        {
                            "id": vehicle_id,
                            "class_id": class_id,
                            "name": VEHICLE_NAMES[
                                class_id
                            ],
                            "box": vehicle_box,
                            "confidence": vehicle_conf
                        }
                    )

                except Exception:
                    continue

        # ======================================================
        # LICENSE PLATE DETECTION
        # ======================================================

        try:

            plate_results = (
                plate_model.predict(
                    frame,
                    conf=PLATE_CONF,
                    imgsz=PLATE_IMGSZ,
                    verbose=False
                )
            )

            plate_result = (
                plate_results[0]
            )

        except Exception as e:

            print(
                "Plate detection error:",
                e
            )

            plate_result = None

        detected_plates = []

        if (
            plate_result is not None
            and
            plate_result.boxes is not None
        ):

            for box in (
                plate_result.boxes
            ):

                try:

                    plate_conf = float(
                        box.conf[0]
                    )

                    plate_box = clamp_box(
                        box.xyxy[0].tolist(),
                        frame
                    )

                except Exception:
                    continue

                x1, y1, x2, y2 = (
                    plate_box
                )

                plate_width = (
                    x2 - x1
                )

                plate_height = (
                    y2 - y1
                )

                if plate_width < MIN_PLATE_W:
                    continue

                if plate_height < MIN_PLATE_H:
                    continue

                # Important:
                # Wheels/headlights generally don't have
                # the long rectangular plate shape.
                aspect = (
                    plate_width /
                    max(1, plate_height)
                )

                if aspect < MIN_ASPECT:
                    continue

                if aspect > MAX_ASPECT:
                    continue

                plate_center = center(
                    plate_box
                )

                best_vehicle = None
                best_overlap = 0.0

                for vehicle in (
                    current_vehicles
                ):

                    overlap = (
                        intersection_over_plate(
                            plate_box,
                            vehicle["box"]
                        )
                    )

                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_vehicle = vehicle

                # A real plate must belong to a vehicle.
                if best_vehicle is None:
                    continue

                if best_overlap < MIN_VEHICLE_OVERLAP:
                    continue

                # Plates are normally in the lower part
                # of the vehicle box.
                vx1, vy1, vx2, vy2 = (
                    best_vehicle["box"]
                )

                vehicle_height = max(
                    1,
                    vy2 - vy1
                )

                relative_y = (
                    plate_center[1] - vy1
                ) / vehicle_height

                if relative_y < 0.20:
                    continue

                detected_plates.append(
                    {
                        "box": plate_box,
                        "confidence": plate_conf,
                        "vehicle_id":
                            best_vehicle["id"],
                        "vehicle_name":
                            best_vehicle["name"],
                        "text": "",
                        "ocr_confidence": 0.0
                    }
                )

        # Only keep the best candidate for each vehicle.
        best_by_vehicle = {}

        for plate in detected_plates:

            vehicle_id = (
                plate["vehicle_id"]
            )

            if (
                vehicle_id not in
                best_by_vehicle
                or
                plate["confidence"]
                >
                best_by_vehicle[
                    vehicle_id
                ]["confidence"]
            ):

                best_by_vehicle[
                    vehicle_id
                ] = plate

        detected_plates = list(
            best_by_vehicle.values()
        )

        # ======================================================
        # OCR
        # ======================================================

        if (
            processed_frames %
            OCR_INTERVAL
            == 0
        ):

            for plate in (
                detected_plates
            ):

                crop = crop_plate(
                    frame,
                    plate["box"]
                )

                text, confidence = (
                    run_ocr(crop)
                )

                plate["text"] = text

                plate[
                    "ocr_confidence"
                ] = confidence

                vehicle_id = (
                    plate["vehicle_id"]
                )

                if text:

                    add_reading(
                        vehicle_id,
                        text,
                        confidence,
                        frame_number
                    )

                    # Keep the most recent valid plate box so that
                    # the stable investigation record can save the
                    # corresponding plate evidence image.
                    vehicle_records[
                        vehicle_id
                    ]["best_plate_box"] = plate["box"]

                    # Raw OCR is printed so we can
                    # diagnose accuracy if needed.
                    print(
                        f"OCR | "
                        f"Vehicle {vehicle_id} | "
                        f"{text} | "
                        f"conf={confidence:.2f}"
                    )

        # ======================================================
        # SAVE STABLE VEHICLE RECORDS
        # ======================================================
        # IMPORTANT:
        # record_stable() was defined earlier but was never called.
        # OCR therefore worked, but the CSV stayed empty.
        for vehicle in current_vehicles:
            if vehicle["id"] != -1:
                record_stable(
                    vehicle,
                    frame_number,
                    frame
                )

        # ======================================================
        # REMOVE VERY OLD TRACK RECORDS
        # ======================================================

        old_ids = [
            vehicle_id
            for vehicle_id, record
            in vehicle_records.items()
            if (
                frame_number -
                record["last_seen"]
            ) > STALE_FRAMES
        ]

        for vehicle_id in old_ids:
            del vehicle_records[
                vehicle_id
            ]

        # ======================================================
        # PROGRESS
        # ======================================================

        if TOTAL_FRAMES > 0:
            progress = int(
                min(
                    100,
                    (frame_number / TOTAL_FRAMES) * 100
                )
            )
        else:
            progress = 0

        if progress != last_progress:
            last_progress = progress
            print(f"PROGRESS:{progress}", flush=True)

        

finally:

    cap.release()
    csv_file.close()


print("PROGRESS:100", flush=True)
print()
print("=" * 64)
print("WatchX processing completed.", flush=True)
print(f"Records saved to: {CSV_PATH}", flush=True)
print("PROCESSING_COMPLETED", flush=True)
print("=" * 64, flush=True)
