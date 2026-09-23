WatchX

AI-Powered Vehicle Investigation \& Road Surveillance System



WatchX is an AI-powered vehicle investigation and road surveillance system designed to make existing CCTV footage searchable, structured, and useful for authorized investigations.



Don't make investigators watch more CCTV. Make CCTV searchable.



🚨 The Problem



Modern cities already have large numbers of road surveillance cameras continuously recording traffic and public-road activity.



Today, surveillance cameras can capture increasingly high-resolution footage, including 4K and 8K video, providing a huge amount of visual information about vehicles and road activity.



However, there is a major gap between recording the footage and efficiently investigating the footage.



📹 Cameras Record Everything — But Finding the Required Information Is Still Difficult



When an incident occurs, investigators may need to determine:



Which vehicles were present at a particular location?

What license plates appeared in the area?

Where did a particular vehicle travel?

Which camera captured the vehicle?

At what time did the vehicle appear?

Did the same vehicle appear at another location?

Which other camera may have captured the same vehicle?

What visual evidence is associated with that vehicle?



In a conventional CCTV workflow, investigators may have to manually retrieve and search recorded footage.



For example, if an incident occurs at approximately 8:30 PM, an investigator may need to:



Identify the relevant CCTV camera.

Retrieve the recorded footage.

Select the approximate date and time.

Open the recording.

Manually scan through the footage.

Look for the relevant vehicle.

Pause and replay frames.

Read the license plate manually.

Check additional cameras.

Repeat the process across different time periods.

Manually correlate the observations.



This becomes increasingly difficult when dealing with:



Multiple cameras

Long recording durations

Heavy traffic

Large numbers of vehicles

Multiple possible routes

High-resolution video

Multiple locations

Multiple days of recordings

The problem is not simply the lack of CCTV cameras.

The problem is the lack of intelligence over the footage that already exists.

🎥 The High-Resolution CCTV Challenge



High-resolution cameras such as 4K and 8K systems can capture significantly more visual detail.



But higher resolution also means surveillance systems can generate extremely large amounts of video data.



A camera may record thousands of vehicles over a day.



When an investigation requires one particular vehicle, the relevant information may already exist somewhere inside those recordings.



The challenge is finding it efficiently.



Thousands of vehicles

&#x20;       ↓

Hours of CCTV footage

&#x20;       ↓

Multiple cameras

&#x20;       ↓

Large amounts of recorded data

&#x20;       ↓

Investigator manually searches

&#x20;       ↓

Relevant vehicle may eventually be found



The valuable information already exists.



Finding the required information is the problem.

🔍 The Existing CCTV Investigation Gap



Traditional CCTV systems are primarily designed to record and provide access to video footage.



They can answer:



"What did this camera record?"



But an investigation often requires questions such as:



"Show me vehicles with this license plate."



"When did this vehicle appear?"



"Where did this vehicle appear?"



"Which other camera may have captured it?"



"Show me the visual evidence associated with this detection."



Traditional video storage does not automatically convert the entire recording into searchable vehicle events.



Therefore:



CCTV is good at recording.

Investigation requires searching, identifying, correlating, and verifying.



WatchX is designed to bridge this gap.



🧩 Why Manual Investigation Does Not Scale



Consider a surveillance network containing many road cameras.



Each camera continuously records video.



Now consider an investigation involving:



20 cameras

24 hours of recordings

Hundreds or thousands of vehicles per camera

Multiple possible routes

Multiple time periods



The amount of video that an investigator may need to examine can become enormous.



Even when the required information exists somewhere inside the recordings, finding it can be time-consuming.



The investigator may know:



A vehicle's approximate appearance

A suspected license plate

An approximate time

A location

A vehicle type



But the evidence may still be buried inside raw video files.



The data exists.

Finding the data is the problem.

💡 The WatchX Approach



WatchX adds an AI-based intelligence layer on top of CCTV footage.



Instead of treating CCTV footage as something an investigator must watch from beginning to end, WatchX processes the footage and attempts to convert it into structured vehicle investigation data.



The core pipeline is:



CCTV VIDEO

&#x20;    ↓

VEHICLE DETECTION

&#x20;    ↓

VEHICLE TRACKING

&#x20;    ↓

LICENSE PLATE DETECTION

&#x20;    ↓

LICENSE PLATE OCR

&#x20;    ↓

STRUCTURED VEHICLE RECORD

&#x20;    ↓

VISUAL EVIDENCE

&#x20;    ↓

INVESTIGATION DASHBOARD



This allows investigators to work with structured vehicle events instead of manually searching every frame.



🚗 What WatchX Does

1\. Vehicle Detection



WatchX analyzes video and identifies vehicles appearing in the scene.



Supported vehicle categories can include:



Cars

Motorcycles

Other supported vehicle classes



Each detected vehicle can become part of the tracking and investigation pipeline.



2\. Vehicle Tracking



Detecting a vehicle in a single frame is not enough.



A vehicle appears across multiple frames as it moves through the camera's view.



WatchX uses vehicle tracking to associate repeated detections with a tracking identity.



This helps determine:



When the vehicle appeared

Which frames contained the vehicle

How long it remained visible

Which detections belong to the same tracked object

3\. License Plate Detection



When a vehicle is detected, WatchX attempts to locate its visible license plate.



The detected plate region can then be passed to the OCR pipeline.



4\. License Plate Recognition



WatchX uses Optical Character Recognition (OCR) to extract characters from detected license plates.



Example outputs:



AP09C6555

AP99C6555

TS07GD3211

TG07A3233

TG07W7025



Instead of leaving plate information only inside the video frame, WatchX stores the result as structured investigation data.



5\. Confidence-Based Records



License plate recognition can be affected by:



Motion blur

Distance

Lighting

Camera angle

Occlusion

Low visibility

Plate condition

Image quality



WatchX therefore records confidence information associated with detections.



This helps investigators distinguish stronger detections from results that may require additional verification.



🕒 From Raw Video to Structured Investigation Data

Traditional CCTV Investigation

VIDEO

&#x20; ↓

INVESTIGATOR WATCHES VIDEO

&#x20; ↓

MANUALLY FINDS VEHICLE

&#x20; ↓

MANUALLY READS PLATE

&#x20; ↓

MANUALLY RECORDS INFORMATION

WatchX

VIDEO

&#x20; ↓

AI VEHICLE DETECTION

&#x20; ↓

VEHICLE TRACKING

&#x20; ↓

PLATE DETECTION

&#x20; ↓

OCR

&#x20; ↓

STRUCTURED RECORD

&#x20; ↓

VISUAL EVIDENCE

&#x20; ↓

INVESTIGATOR VERIFICATION



A WatchX investigation record can contain:



Information	Example

Timestamp	18.91 seconds

Frame	1134

Vehicle ID	311

Vehicle Type	Motorcycle

License Plate	TS07GD3211

OCR Confidence	99%

Evidence	Associated vehicle/plate images



This converts raw visual information into structured investigation events.



🔎 Investigation Instead of Video Watching

Conventional Workflow

Incident

&#x20;  ↓

Find CCTV camera

&#x20;  ↓

Retrieve recording

&#x20;  ↓

Search through hours of footage

&#x20;  ↓

Find possible vehicle

&#x20;  ↓

Pause / replay

&#x20;  ↓

Read plate manually

&#x20;  ↓

Check other footage

&#x20;  ↓

Repeat

WatchX Workflow

Incident

&#x20;  ↓

Process available CCTV footage

&#x20;  ↓

AI detects vehicles

&#x20;  ↓

AI tracks vehicles

&#x20;  ↓

AI detects license plates

&#x20;  ↓

OCR extracts plate numbers

&#x20;  ↓

Create structured vehicle records

&#x20;  ↓

Search / review investigation records

&#x20;  ↓

Inspect visual evidence



The investigator can therefore start with structured information extracted from the footage instead of manually searching every frame.



🏙️ Designed Around Existing CCTV Infrastructure



An important principle of WatchX is:



The goal is not necessarily to replace existing cameras.



Government agencies and other authorized organizations already operate CCTV infrastructure across roads and public locations.



WatchX is designed to provide an AI investigation layer that can process compatible recorded surveillance footage.



The long-term vision is to connect suitable authorized road-camera feeds to a centralized investigation system.



This means the value comes not only from installing more cameras, but also from making existing camera footage more useful.



🧠 Centralized Vehicle Investigation



A future deployment could use an architecture such as:



&#x20;             AUTHORIZED ROAD CAMERAS

&#x20;                       │

&#x20;                       ▼

&#x20;                CCTV VIDEO FEEDS

&#x20;                       │

&#x20;                       ▼

&#x20;              ┌─────────────────┐

&#x20;              │   WATCHX AI     │

&#x20;              │                 │

&#x20;              │ Vehicle Detect  │

&#x20;              │ Vehicle Track   │

&#x20;              │ Plate Detect    │

&#x20;              │ Plate OCR       │

&#x20;              └────────┬────────┘

&#x20;                       │

&#x20;                       ▼

&#x20;               VEHICLE EVENT DATA

&#x20;                       │

&#x20;                       ▼

&#x20;             INVESTIGATION DATABASE

&#x20;                       │

&#x20;                       ▼

&#x20;             INVESTIGATION DASHBOARD



The long-term objective is to transform distributed CCTV footage into a searchable vehicle intelligence layer for authorized investigations.



🕵️ Investigation Workflow

Step 1 — CCTV Footage



Recorded road surveillance footage is provided to WatchX.



Step 2 — AI Processing



WatchX analyzes the video frame by frame.



Step 3 — Vehicle Detection



Vehicles are detected in the video.



Step 4 — Vehicle Tracking



Detected vehicles are tracked across frames.



Step 5 — License Plate Detection



Visible license plates are identified.



Step 6 — OCR



The plate image is processed to extract characters.



Step 7 — Investigation Record



WatchX creates a structured record containing information such as:



Vehicle ID

Vehicle type

License plate

Timestamp

Frame number

OCR confidence

Evidence images

Step 8 — Investigator Review



An authorized investigator can search the generated records and inspect associated visual evidence.



📊 Investigation Dashboard



WatchX provides a desktop investigation dashboard for reviewing processed vehicle events.



The dashboard can display:



Recorded vehicle events

Unique license plates

Average OCR confidence

High-confidence records

Search results

Vehicle detection history

Timestamps

Vehicle IDs

Vehicle types

License plate results

Visual evidence



The purpose of the dashboard is to turn AI processing results into information that an investigator can review efficiently.



🖼️ Visual Evidence



A license plate result alone should not automatically be treated as ground truth.



OCR can make mistakes.



Therefore, WatchX associates detection results with visual evidence where available.



The investigation workflow can be:



AI DETECTION

&#x20;    ↓

LICENSE PLATE RESULT

&#x20;    ↓

CONFIDENCE SCORE

&#x20;    ↓

VISUAL EVIDENCE

&#x20;    ↓

HUMAN VERIFICATION



WatchX is designed as an investigation-assistance system where AI supports the investigator rather than replacing human verification.



🤖 AI Technologies



WatchX currently uses computer-vision and AI components including:



YOLO — Object / Vehicle Detection

ByteTrack — Multi-Object Tracking

PaddleOCR / OCR Pipeline — License Plate Recognition

OpenCV — Video Processing and Computer Vision

Python — Application and AI Processing

Tkinter — Desktop Application Interface

🏗️ System Architecture

&#x20;                CCTV VIDEO

&#x20;                    │

&#x20;                    ▼

&#x20;         ┌────────────────────┐

&#x20;         │  VIDEO PROCESSING  │

&#x20;         └─────────┬──────────┘

&#x20;                   │

&#x20;                   ▼

&#x20;         ┌────────────────────┐

&#x20;         │ VEHICLE DETECTION  │

&#x20;         │       YOLO         │

&#x20;         └─────────┬──────────┘

&#x20;                   │

&#x20;                   ▼

&#x20;         ┌────────────────────┐

&#x20;         │ VEHICLE TRACKING   │

&#x20;         │     ByteTrack      │

&#x20;         └─────────┬──────────┘

&#x20;                   │

&#x20;                   ▼

&#x20;         ┌────────────────────┐

&#x20;         │ PLATE DETECTION    │

&#x20;         └─────────┬──────────┘

&#x20;                   │

&#x20;                   ▼

&#x20;         ┌────────────────────┐

&#x20;         │       OCR          │

&#x20;         │ PLATE RECOGNITION  │

&#x20;         └─────────┬──────────┘

&#x20;                   │

&#x20;                   ▼

&#x20;         ┌────────────────────┐

&#x20;         │ STRUCTURED RECORDS │

&#x20;         │ + VISUAL EVIDENCE  │

&#x20;         └─────────┬──────────┘

&#x20;                   │

&#x20;                   ▼

&#x20;         ┌────────────────────┐

&#x20;         │ WATCHX DASHBOARD   │

&#x20;         └────────────────────┘

🖥️ Current MVP



The current WatchX MVP supports:



CCTV video selection

AI video processing

Vehicle detection

Vehicle tracking

License plate detection

License plate OCR

Structured vehicle records

Timestamp information

Frame information

Vehicle IDs

OCR confidence

Visual evidence

Detection history

Record searching

Investigation dashboard

Investigator login interface

Windows desktop application

Packaged executable



The complete MVP has been tested end-to-end.



🔐 Investigator Access



WatchX includes an investigator authentication interface for the dashboard.



The current MVP uses predefined investigator IDs for demonstration purposes.



A production deployment would require integration with an organization's secure identity and access-management infrastructure.



📈 Example Investigation Records



Example records generated during MVP testing include:



Time	Frame	Vehicle ID	Type	Plate	Confidence

5.50s	330	2	Car	AP09C6555	76%

14.61s	876	2	Car	AP99C6555	78%

18.91s	1134	311	Motorcycle	TS07GD3211	99%

29.72s	1782	2	Car	AP09G6555	76%

41.82s	2508	619	Car	TG07A3233	99%

45.22s	2712	650	Car	TG07W7025	99%



These records demonstrate how raw video can be converted into structured vehicle events that can be reviewed through the investigation dashboard.



🎯 The Core Difference



WatchX is not intended to be just another CCTV recording application.



The key concept is:



TRADITIONAL CCTV



Camera

&#x20; ↓

Records Video

&#x20; ↓

Stores Video

&#x20; ↓

Investigator Manually Searches





WATCHX



Camera

&#x20; ↓

Records Video

&#x20; ↓

AI Analyzes Video

&#x20; ↓

Detects Vehicles

&#x20; ↓

Tracks Vehicles

&#x20; ↓

Reads License Plates

&#x20; ↓

Creates Structured Records

&#x20; ↓

Stores Evidence

&#x20; ↓

Investigator Searches Records



The goal is to move from:



Video Storage



to:



Video Intelligence



🚀 Future Vision



The current MVP works primarily with recorded video.



The long-term WatchX vision includes:



Real-Time CCTV Processing



Process authorized CCTV streams as they are generated.



Multi-Camera Vehicle Correlation



Associate vehicle detections across multiple cameras.



Vehicle Search



Search the investigation database using available vehicle information.



Plate-Based Investigation



Search historical records using a license plate.



Route Reconstruction



Use timestamped detections across cameras to help reconstruct a vehicle's observed route.



Centralized Investigation Database



Store structured vehicle events from multiple authorized camera locations.



Real-Time Alerts



Generate configurable alerts for authorized investigation use cases.



Role-Based Access



Provide different permissions for investigators, administrators, and other authorized personnel.



Audit Logging



Record investigation activity for accountability and security.



⚠️ Production Considerations



WatchX is currently an MVP/prototype.



A real-world government deployment would require additional engineering and validation, including:



Secure infrastructure

Encryption

Strong authentication

Role-based access control

Audit logging

Data protection

Data retention policies

Accuracy testing

False-positive handling

Camera calibration

Human verification

Secure database architecture

Legal and regulatory compliance

Appropriate authorization for accessing surveillance data



AI-generated detections should be treated as investigative assistance and verified by authorized personnel before being used for consequential decisions.



📁 Project Structure

WatchX/

│

├── watchx\_desktop.py

├── plate\_ocr.py

├── dashboard.py

├── vehicle\_detection.py

│

├── yolo11n.pt

├── license\_plate\_detector.pt

│

├── watchx\_data/

│   ├── watchx\_records.csv

│   └── evidence/

│

├── data/

│   └── videos/

│

└── README.md

⚙️ Technology Stack

Component	Technology

Programming Language	Python

Object Detection	YOLO

Object Tracking	ByteTrack

License Plate OCR	PaddleOCR / OCR Pipeline

Computer Vision	OpenCV

Desktop UI	Tkinter

Data Storage	CSV / File System

Packaging	PyInstaller

Development	VS Code

Platform	Windows

🧪 MVP Status

WatchX MVP — COMPLETED ✅

Vehicle Detection        ✅

Vehicle Tracking         ✅

License Plate Detection  ✅

License Plate OCR        ✅

Structured Records       ✅

OCR Confidence            ✅

Visual Evidence           ✅

Detection History         ✅

Search                    ✅

Investigation Dashboard   ✅

Investigator Login        ✅

Windows Desktop App       ✅

PyInstaller Packaging     ✅

End-to-End Testing        ✅

GitHub Repository         ✅

🌐 Project Vision



WatchX aims to make existing road surveillance footage more useful by adding an AI intelligence layer.



The vision is to help authorized investigators move from:



RAW CCTV FOOTAGE

&#x20;      ↓

MANUAL SEARCH

&#x20;      ↓

MANUAL IDENTIFICATION

&#x20;      ↓

MANUAL CORRELATION



towards:



CCTV FOOTAGE

&#x20;      ↓

AI PROCESSING

&#x20;      ↓

VEHICLE DETECTION

&#x20;      ↓

VEHICLE TRACKING

&#x20;      ↓

LICENSE PLATE RECOGNITION

&#x20;      ↓

STRUCTURED INVESTIGATION DATA

&#x20;      ↓

SEARCH

&#x20;      ↓

VISUAL VERIFICATION

&#x20;      ↓

INVESTIGATION

💡 The One-Line Idea



WatchX transforms existing CCTV footage into searchable vehicle investigation intelligence.



👨‍💻 Project



WatchX — AI-Powered Vehicle Investigation \& Road Surveillance System



Built as an AI and computer-vision prototype for intelligent analysis of road surveillance footage.

\---



\# 📸 WatchX — Application Screenshots



\## 🖥️ WatchX Desktop Application



The WatchX desktop application provides the main interface for selecting CCTV footage, starting AI-powered processing, monitoring processing progress, and accessing the investigation dashboard.



!\[WatchX Desktop](screenshots/watchx\_desktop.png)



\---



\## ⚙️ Video Processing



WatchX processes the selected CCTV footage and provides real-time processing progress.



!\[Video Processing](screenshots/processing.png)



\---



\## ✅ Processing Completed



After processing is completed, WatchX confirms that the investigation data has been generated successfully.



!\[Processing Completed](screenshots/Processing%20completed%20%20final%20result.png)



\---



\## 📊 Investigation Dashboard



The investigation dashboard provides investigators with a centralized view of detected vehicle events, number plates, OCR confidence, and investigation information.



!\[Investigation Dashboard](screenshots/Investigation%20Dashboard.png)



\---



\## 🚗 Vehicle Detection Records



Detected vehicles and their extracted license plates are displayed as structured investigation records.



!\[Vehicle Detection Records](screenshots/Vehicle%20detection%20records.png)



\---



\## 🔎 Search Vehicle



Investigators can search the available detection records to locate specific vehicles or license plates.



!\[Search Vehicle](screenshots/search%20vechile.png)



\---



\## 🖼️ Visual Evidence



WatchX provides visual evidence associated with detected vehicles and license plates to support investigation.



!\[Visual Evidence](screenshots/Visual%20Evidence%20%20selected%20vehicle.png)



\---



\## 📜 Detection History



The dashboard maintains a history of detected vehicle events for investigation and review.



!\[Detection History](screenshots/detection%20histroy.png)



\---





\---



\## 🔐 Investigator Authentication



WatchX includes an investigator authentication layer for accessing the investigation dashboard.



The dashboard requires a valid authorized investigator ID and password before access is granted.



\### Authorized Investigator IDs



The current MVP uses predefined investigator IDs:



\- `24VE1A05HC`

\- `24VE1AO5KD`

\- `24VE1AO5JH`

\- `24VE1A05HA`



> \*\*Security Note:\*\* The current MVP uses fixed credentials for demonstration and prototype purposes. Production deployment should use secure credential storage, password hashing, role-based access control, account management, and secure authentication mechanisms.



\### Dashboard Access



1\. Launch WatchX.

2\. Process the CCTV footage.

3\. Open the Investigation Dashboard.

4\. Enter an authorized investigator ID.

5\. Enter the configured password.

6\. Access the investigation dashboard.



\---
and the password is : WatchX@2026
