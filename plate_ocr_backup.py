import cv2
import re
import time
from collections import defaultdict, Counter
from ultralytics import YOLO
from fast_plate_ocr import LicensePlateRecognizer


# ============================================================
# WATCHX
# AI VEHICLE + NUMBER PLATE DETECTION + OCR
#
# Pipeline:
# Video
#   ↓
# Vehicle detection + tracking
#   ↓
# License plate detection
#   ↓
# High quality plate crop
#   ↓
# Fast Plate OCR
#   ↓
# Multi-frame voting
#   ↓
# Stable number plate
# ============================================================


print("=" * 60)
print("WATCHX - AI VEHICLE INVESTIGATION")
print("NUMBER PLATE DETECTION + OCR")
print("=" * 60)


# ============================================================
# MODELS
# ============================================================

print("Loading vehicle detector...")

vehicle_model = YOLO("yolo11n.pt")

print("Loading license plate detector...")

plate_model = YOLO("license_plate_detector.pt")

print("Loading Fast Plate OCR...")

plate_ocr = LicensePlateRecognizer(
    "cct-s-v2-global-model"
)

print("All models loaded successfully.")
print()


# ============================================================
# VIDEO
# ============================================================

VIDEO_PATH = "data/videos/my_traffic_video.MOV"

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    raise RuntimeError(
        f"Could not open video:\n{VIDEO_PATH}"
    )


SOURCE_FPS = cap.get(cv2.CAP_PROP_FPS)

WIDTH = int(
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)

HEIGHT = int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)


print("WatchX started.")
print(f"Video: {VIDEO_PATH}")
print(f"Resolution: {WIDTH} x {HEIGHT}")
print(f"Source FPS: {SOURCE_FPS:.2f}")
print()


# ============================================================
# PERFORMANCE SETTINGS
# ============================================================

# Process every 2nd frame.
# This keeps the system considerably faster.
FRAME_SKIP = 2


# Vehicle detection/tracking input size.
VEHICLE_IMGSZ = 640


# License plate detector input size.
# Higher value helps small plates.
PLATE_IMGSZ = 960


# Vehicle confidence.
VEHICLE_CONF = 0.30


# Plate detector confidence.
PLATE_CONF = 0.20


# Run plate detector every N processed frames.
#
# 1 = maximum detection
# 2 = faster
#
# Start with 1 because we want accuracy.
PLATE_DETECT_INTERVAL = 1


# OCR every N processed frames.
#
# OCR is expensive, therefore don't run it
# on every single frame.
OCR_INTERVAL = 2


# Minimum OCR confidence.
#
# We intentionally allow fairly low confidence
# because temporal voting will improve it.
OCR_CONF_MIN = 0.15


# Number of OCR readings stored per vehicle.
HISTORY_SIZE = 20


# Minimum votes required before displaying
# a final stable plate.
MIN_STABLE_VOTES = 3


# Maximum character difference for grouping
# similar OCR readings.
MAX_EDIT_DISTANCE = 2


# ============================================================
# VEHICLE CLASSES
# ============================================================

VEHICLE_CLASSES = [
    2,  # car
    3,  # motorcycle
    5,  # bus
    7,  # truck
]


VEHICLE_NAMES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck",
}


# ============================================================
# DATA
# ============================================================

vehicle_records = defaultdict(
    lambda: {
        "readings": [],
        "best_plate": "",
        "best_conf": 0.0,
        "votes": 0,
        "last_seen": 0,
    }
)


last_plates = []

frame_number = 0
processed_frames = 0

start_time = time.time()


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if text is None:
        return ""

    text = str(text).upper()

    # Remove spaces, hyphens and symbols.
    text = re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )

    return text


# ============================================================
# CHARACTER NORMALIZATION
# ============================================================

def normalize_plate(text):

    """
    Correct common OCR character mistakes.

    Indian registration plates normally contain:

        letters + numbers + letters + numbers

    Common OCR mistakes:

        O <-> 0
        I <-> 1
        Z <-> 2
        S <-> 5
        B <-> 8
        G <-> 6
    """

    text = clean_text(text)

    if not text:
        return ""


    # We mainly expect 10-character Indian plates.
    #
    # Example:
    #
    # AP09CG5555
    #
    # TS09AB1234
    #

    if len(text) == 10:

        chars = list(text)


        # First two = letters
        letter_map = {
            "0": "O",
            "1": "I",
            "2": "Z",
            "5": "S",
            "6": "G",
            "8": "B",
        }

        for i in [0, 1]:

            if chars[i] in letter_map:
                chars[i] = letter_map[chars[i]]


        # Positions 2 and 3 = digits
        digit_map = {
            "O": "0",
            "Q": "0",
            "D": "0",
            "I": "1",
            "L": "1",
            "Z": "2",
            "S": "5",
            "G": "6",
            "B": "8",
        }

        for i in [2, 3]:

            if chars[i] in digit_map:
                chars[i] = digit_map[chars[i]]


        # Positions 4 and 5 = letters
        for i in [4, 5]:

            if chars[i] in letter_map:
                chars[i] = letter_map[chars[i]]


        # Last four = digits
        for i in [6, 7, 8, 9]:

            if chars[i] in digit_map:
                chars[i] = digit_map[chars[i]]


        text = "".join(chars)


    return text


# ============================================================
# INDIAN PLATE VALIDATION
# ============================================================

def valid_indian_plate(text):

    text = clean_text(text)

    if not text:
        return False


    # Main Indian registration format.
    #
    # Example:
    # AP09CG5555
    # TS09AB1234
    # KA01MN1234
    #

    if re.fullmatch(
        r"^[A-Z]{2}[0-9]{2}[A-Z]{1,3}[0-9]{4}$",
        text
    ):
        return True


    # Slightly more permissive format.
    #
    # This allows the OCR model to produce
    # a valid partial-length registration.
    #

    if re.fullmatch(
        r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$",
        text
    ):
        return True


    return False


# ============================================================
# EDIT DISTANCE
# ============================================================

def edit_distance(a, b):

    if a == b:
        return 0

    if not a:
        return len(b)

    if not b:
        return len(a)


    previous = list(
        range(len(b) + 1)
    )


    for i, ca in enumerate(a, 1):

        current = [i]


        for j, cb in enumerate(b, 1):

            insert_cost = (
                current[j - 1] + 1
            )

            delete_cost = (
                previous[j] + 1
            )

            replace_cost = (
                previous[j - 1]
                + (ca != cb)
            )

            current.append(
                min(
                    insert_cost,
                    delete_cost,
                    replace_cost
                )
            )


        previous = current


    return previous[-1]


# ============================================================
# FIND SIMILAR PLATE
# ============================================================

def find_similar_plate(
    text,
    existing
):

    for candidate in existing:

        if edit_distance(
            text,
            candidate
        ) <= MAX_EDIT_DISTANCE:

            return candidate


    return text


# ============================================================
# BOX UTILITIES
# ============================================================

def clamp_box(box, frame):

    h, w = frame.shape[:2]

    x1, y1, x2, y2 = [
        int(v)
        for v in box
    ]


    x1 = max(
        0,
        min(x1, w - 1)
    )

    y1 = max(
        0,
        min(y1, h - 1)
    )

    x2 = max(
        0,
        min(x2, w - 1)
    )

    y2 = max(
        0,
        min(y2, h - 1)
    )


    return (
        x1,
        y1,
        x2,
        y2
    )


# ============================================================
# CENTER
# ============================================================

def box_center(box):

    x1, y1, x2, y2 = box

    return (
        int((x1 + x2) / 2),
        int((y1 + y2) / 2)
    )


# ============================================================
# POINT INSIDE BOX
# ============================================================

def point_inside(
    point,
    box
):

    px, py = point

    x1, y1, x2, y2 = box

    return (
        x1 <= px <= x2
        and
        y1 <= py <= y2
    )


# ============================================================
# PLATE CROP
# ============================================================

def crop_plate(
    frame,
    box
):

    x1, y1, x2, y2 = box

    h, w = frame.shape[:2]


    plate_width = x2 - x1
    plate_height = y2 - y1


    # Small padding.
    #
    # Too much background can confuse OCR.
    #

    pad_x = max(
        3,
        int(plate_width * 0.10)
    )

    pad_y = max(
        3,
        int(plate_height * 0.18)
    )


    x1 = max(
        0,
        x1 - pad_x
    )

    y1 = max(
        0,
        y1 - pad_y
    )

    x2 = min(
        w,
        x2 + pad_x
    )

    y2 = min(
        h,
        y2 + pad_y
    )


    crop = frame[
        y1:y2,
        x1:x2
    ]


    return crop


# ============================================================
# PREPARE OCR IMAGE
# ============================================================

def prepare_ocr_image(crop):

    if (
        crop is None
        or crop.size == 0
    ):
        return None


    h, w = crop.shape[:2]


    # Don't upscale tiny garbage crops.
    if w < 10 or h < 5:
        return None


    # Make the plate substantially larger.
    #
    # This is important because the actual plate
    # in a 1080p traffic video may only occupy
    # a small number of pixels.
    #

    scale = 4.0


    crop = cv2.resize(
        crop,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC
    )


    # Mild sharpening.
    #
    # We don't aggressively threshold because
    # Fast Plate OCR's model generally performs
    # better with natural plate appearance.
    #

    blurred = cv2.GaussianBlur(
        crop,
        (0, 0),
        1.0
    )


    sharpened = cv2.addWeighted(
        crop,
        1.35,
        blurred,
        -0.35,
        0
    )


    # Slight contrast enhancement.
    lab = cv2.cvtColor(
        sharpened,
        cv2.COLOR_BGR2LAB
    )

    l, a, b = cv2.split(lab)


    clahe = cv2.createCLAHE(
        clipLimit=1.5,
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
    rgb = cv2.cvtColor(
        enhanced,
        cv2.COLOR_BGR2RGB
    )


    return rgb


# ============================================================
# RUN OCR
# ============================================================

def run_ocr(crop):

    rgb = prepare_ocr_image(
        crop
    )


    if rgb is None:
        return "", 0.0


    try:

        predictions = plate_ocr.run(
            [rgb],
            return_confidence=True
        )

    except Exception as e:

        print(
            "OCR error:",
            e
        )

        return "", 0.0


    if not predictions:
        return "", 0.0


    prediction = predictions[0]


    # --------------------------------------------------------
    # Get text
    # --------------------------------------------------------

    text = clean_text(
        getattr(
            prediction,
            "plate",
            ""
        )
    )


    # --------------------------------------------------------
    # Get character confidence
    # --------------------------------------------------------

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
                    sum(values)
                    /
                    len(values)
                )

        except Exception:
            confidence = 0.0


    # Fallback.
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


    # --------------------------------------------------------
    # Normalize common OCR mistakes.
    # --------------------------------------------------------

    normalized = normalize_plate(
        text
    )


    if normalized:
        text = normalized


    # --------------------------------------------------------
    # We don't immediately reject every imperfect
    # OCR result.
    #
    # Temporal voting will decide the final result.
    # --------------------------------------------------------

    if len(text) < 7:
        return "", confidence


    if confidence < OCR_CONF_MIN:
        return "", confidence


    return text, confidence


# ============================================================
# UPDATE VEHICLE OCR HISTORY
# ============================================================

def update_vehicle_record(
    vehicle_id,
    text,
    confidence,
    current_frame
):

    if not text:
        return


    record = vehicle_records[
        vehicle_id
    ]


    record["last_seen"] = (
        current_frame
    )


    # --------------------------------------------------------
    # Match this OCR result to an existing similar result.
    #
    # Example:
    #
    # AP09CG5555
    # AP09CG555S
    # AP09C65555
    #
    # These may actually represent the same plate.
    # --------------------------------------------------------

    existing = [
        item[0]
        for item in record["readings"]
    ]


    canonical = find_similar_plate(
        text,
        existing
    )


    record["readings"].append(
        (
            canonical,
            confidence
        )
    )


    if len(
        record["readings"]
    ) > HISTORY_SIZE:

        record["readings"] = (
            record["readings"][
                -HISTORY_SIZE:
            ]
        )


    # --------------------------------------------------------
    # Weighted voting.
    #
    # Higher-confidence OCR results contribute
    # more than weak readings.
    # --------------------------------------------------------

    scores = defaultdict(
        float
    )

    counts = Counter()


    for plate, conf in record[
        "readings"
    ]:

        counts[plate] += 1

        # Confidence weight.
        weight = max(
            0.10,
            float(conf)
        )

        scores[plate] += weight


    if not scores:
        return


    best_plate = max(
        scores,
        key=scores.get
    )


    best_score = scores[
        best_plate
    ]


    best_votes = counts[
        best_plate
    ]


    # Best confidence for this plate.
    plate_confidences = [
        conf
        for plate, conf
        in record["readings"]
        if plate == best_plate
    ]


    best_conf = max(
        plate_confidences
    )


    record["best_plate"] = (
        best_plate
    )

    record["best_conf"] = (
        best_conf
    )

    record["votes"] = (
        best_votes
    )

    record["score"] = (
        best_score
    )


# ============================================================
# GET STABLE PLATE
# ============================================================

def get_stable_plate(
    vehicle_id
):

    if vehicle_id not in (
        vehicle_records
    ):
        return "", 0.0, 0


    record = vehicle_records[
        vehicle_id
    ]


    if record["votes"] < (
        MIN_STABLE_VOTES
    ):
        return "", 0.0, 0


    return (
        record["best_plate"],
        record["best_conf"],
        record["votes"]
    )


# ============================================================
# MAIN LOOP
# ============================================================

print(
    "Press Q to quit."
)

print()


while True:

    # --------------------------------------------------------
    # Grab frames efficiently.
    # --------------------------------------------------------

    ret = True


    for _ in range(
        FRAME_SKIP
    ):

        ret = cap.grab()

        if not ret:
            break


    if not ret:
        break


    ret, frame = (
        cap.retrieve()
    )


    if not ret:
        break


    frame_number += (
        FRAME_SKIP
    )

    processed_frames += 1


    # ========================================================
    # VEHICLE DETECTION + TRACKING
    # ========================================================

    try:

        results = (
            vehicle_model.track(
                frame,
                persist=True,
                classes=VEHICLE_CLASSES,
                conf=VEHICLE_CONF,
                imgsz=VEHICLE_IMGSZ,
                verbose=False,
                tracker="bytetrack.yaml"
            )
        )


        result = results[0]


    except Exception as e:

        print(
            "Vehicle detection error:",
            e
        )

        continue


    current_vehicles = []


    if (
        result.boxes is not None
    ):

        for box in result.boxes:

            try:

                class_id = int(
                    box.cls[0]
                )


            except Exception:
                continue


            if class_id not in (
                VEHICLE_CLASSES
            ):
                continue


            try:

                coords = (
                    box.xyxy[0]
                    .tolist()
                )


                x1, y1, x2, y2 = (
                    clamp_box(
                        coords,
                        frame
                    )
                )


            except Exception:
                continue


            if (
                x2 <= x1
                or
                y2 <= y1
            ):
                continue


            try:

                vehicle_conf = float(
                    box.conf[0]
                )

            except Exception:

                vehicle_conf = 0.0


            vehicle_id = -1


            if box.id is not None:

                try:

                    vehicle_id = int(
                        box.id[0]
                    )

                except Exception:

                    vehicle_id = -1


            current_vehicles.append(
                {
                    "id": vehicle_id,
                    "class_id": class_id,
                    "name": VEHICLE_NAMES[
                        class_id
                    ],
                    "box": (
                        x1,
                        y1,
                        x2,
                        y2
                    ),
                    "confidence":
                        vehicle_conf,
                }
            )


    # ========================================================
    # PLATE DETECTION
    # ========================================================

    if (
        processed_frames
        %
        PLATE_DETECT_INTERVAL
        == 0
    ):

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
            plate_result.boxes
            is not None
        ):

            for box in (
                plate_result.boxes
            ):

                try:

                    plate_conf = float(
                        box.conf[0]
                    )


                    coords = (
                        box.xyxy[0]
                        .tolist()
                    )


                    x1, y1, x2, y2 = (
                        clamp_box(
                            coords,
                            frame
                        )
                    )


                except Exception:
                    continue


                if (
                    plate_conf
                    <
                    PLATE_CONF
                ):
                    continue


                plate_width = (
                    x2 - x1
                )

                plate_height = (
                    y2 - y1
                )


                # Reject extremely tiny detections.
                if plate_width < 12:
                    continue

                if plate_height < 5:
                    continue


                detected_plates.append(
                    {
                        "box": (
                            x1,
                            y1,
                            x2,
                            y2
                        ),
                        "confidence":
                            plate_conf,
                        "text": "",
                        "ocr_confidence":
                            0.0,
                        "vehicle_id": -1,
                    }
                )


        last_plates = (
            detected_plates
        )


    detected_plates = (
        last_plates
    )


    # ========================================================
    # MATCH PLATES TO VEHICLES
    # ========================================================

    for plate in (
        detected_plates
    ):

        pc = box_center(
            plate["box"]
        )


        best_vehicle = None


        for vehicle in (
            current_vehicles
        ):

            if point_inside(
                pc,
                vehicle["box"]
            ):

                best_vehicle = (
                    vehicle
                )

                break


        if best_vehicle is not None:

            plate[
                "vehicle_id"
            ] = best_vehicle[
                "id"
            ]


    # ========================================================
    # OCR
    # ========================================================

    if (
        processed_frames
        %
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


            if (
                vehicle_id != -1
                and
                text
            ):

                update_vehicle_record(
                    vehicle_id,
                    text,
                    confidence,
                    frame_number
                )


                print(
                    f"Vehicle ID: "
                    f"{vehicle_id} | "
                    f"OCR: {text} | "
                    f"Confidence: "
                    f"{confidence:.2f}"
                )


    # ========================================================
    # DRAW VEHICLES
    # ========================================================

    for vehicle in (
        current_vehicles
    ):

        x1, y1, x2, y2 = (
            vehicle["box"]
        )

        vehicle_id = (
            vehicle["id"]
        )


        # Vehicle box.
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            2
        )


        label = (
            f"{vehicle['name']} "
            f"ID:{vehicle_id}"
        )


        cv2.putText(
            frame,
            label,
            (
                x1,
                max(
                    25,
                    y1 - 8
                )
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            (255, 0, 0),
            2
        )


        # ----------------------------------------------------
        # Stable plate
        # ----------------------------------------------------

        (
            stable_plate,
            stable_conf,
            votes
        ) = get_stable_plate(
            vehicle_id
        )


        if stable_plate:

            plate_label = (
                f"PLATE: "
                f"{stable_plate} "
                f"[{votes}x]"
            )


            text_y = min(
                HEIGHT - 40,
                y2 + 25
            )


            cv2.putText(
                frame,
                plate_label,
                (
                    x1,
                    text_y
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )


            cv2.putText(
                frame,
                f"CONF: "
                f"{stable_conf:.2f}",
                (
                    x1,
                    min(
                        HEIGHT - 10,
                        y2 + 50
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (0, 255, 0),
                2
            )


    # ========================================================
    # DRAW PLATE BOXES
    # ========================================================

    for plate in (
        detected_plates
    ):

        x1, y1, x2, y2 = (
            plate["box"]
        )


        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 255),
            2
        )


        text = (
            plate["text"]
        )

        ocr_conf = (
            plate["ocr_confidence"]
        )

        det_conf = (
            plate["confidence"]
        )


        if text:

            label = (
                f"{text} "
                f"OCR:{ocr_conf:.2f}"
            )

        else:

            label = (
                f"PLATE "
                f"DET:{det_conf:.2f}"
            )


        cv2.putText(
            frame,
            label,
            (
                x1,
                max(
                    20,
                    y1 - 8
                )
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (0, 255, 255),
            2
        )


    # ========================================================
    # HEADER
    # ========================================================

    cv2.putText(
        frame,
        "WatchX - AI Vehicle Investigation",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.85,
        (0, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"Frame: {frame_number}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"Vehicles: "
        f"{len(current_vehicles)}",
        (20, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )


    # ========================================================
    # FPS
    # ========================================================

    elapsed = (
        time.time()
        -
        start_time
    )


    if elapsed > 0:

        processing_fps = (
            processed_frames
            /
            elapsed
        )

    else:

        processing_fps = 0


    cv2.putText(
        frame,
        f"Processing FPS: "
        f"{processing_fps:.1f}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (255, 255, 255),
        1
    )


    cv2.putText(
        frame,
        "Q = Quit",
        (20, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "WatchX - Vehicle + Number Plate OCR",
        frame
    )


    key = (
        cv2.waitKey(1)
        &
        0xFF
    )


    if key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()


print()
print("=" * 60)
print("WatchX processing completed.")
print("=" * 60)