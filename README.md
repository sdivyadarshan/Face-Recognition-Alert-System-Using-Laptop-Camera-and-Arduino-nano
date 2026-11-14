# Face Recognition Alert System Using Laptop Camera and Arduino Nano

A prototype attendance system combining an Arduino Nano interface, laptop-based face recognition and Google Sheets logging. A short button press starts recognition; holding the button for at least two seconds closes attendance and marks remaining registered names Absent.

> **Prototype notice:** This is an educational prototype. The two-face ID-stage check is not liveness detection, anti-spoofing or certified biometric authentication.

## Features

- InsightFace `buffalo_s` face recognition on the laptop CPU.
- Laptop webcam used for the initial face scan and ID verification stage.
- Local reference images organized in one folder per registered person.
- ID stage requires two detected faces in one frame; both must match the identity found in the initial scan.
- Google Sheets attendance logging with date, name, status and time.
- Arduino Nano, 16x2 I2C LCD, push button, buzzer and red LED.
- Short press to scan; press and hold for at least 2 seconds to close attendance.
- Remaining database names are marked Absent when attendance is closed.
- Further scans are blocked after closing for the current Python run.

## System workflow

1. Power on Arduino and run the Python application. LCD shows **Press SCAN** and Python prints **System Ready**.
2. Short press sends `SCAN`; laptop camera opens.
3. The largest detected face is compared with reference embeddings.
4. If recognized, Python prints **Welcome <name>**. If not, it sends `FAIL`.
5. Python prints **Show your ID card**, waits two seconds and opens the camera again.
6. The ID stage requires at least two detected faces in one frame. Both must match the previously recognized name.
7. On success, Python appends a Present record to Google Sheets and sends `OK:<name>`; Arduino displays success and beeps.
8. A failed recognition or ID check sends `FAIL`.
9. Holding the button for at least two seconds sends `CLOSE`. Python marks all remaining database names Absent, reports the names and locks the session.
10. Further scan commands are rejected after closing.

## Architecture

```text
Push Button -> Arduino Nano --USB Serial--> Python Application
                   |                            |-- Laptop Camera
                   |-- I2C LCD                  |-- InsightFace buffalo_s
                   |-- Buzzer                   |-- Local database/
                   |-- Red LED                  |-- Google Sheets API
```

See [System Architecture](docs/system-architecture.md) and [Algorithm](docs/algorithm.md).

## Repository structure

```text
.
├── src/
│   ├── arduino/face_attendance_controller.ino
│   └── python/face_attendance.py
├── hardware/
│   ├── components-and-wiring.md
│   └── pinout.csv
├── docs/
│   ├── algorithm.md
│   ├── system-architecture.md
│   ├── design-decisions.md
│   ├── testing.md
│   └── contribution-and-ai-disclosure.md
├── media/README.md
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Hardware

- Arduino Nano
- 16x2 LCD with I2C backpack
- Push button
- Buzzer
- Red LED and current-limiting resistor
- Breadboard, jumper wires and USB cable
- Laptop with webcam

Wiring: [hardware/components-and-wiring.md](hardware/components-and-wiring.md).

## Software requirements

- Python 3.11 was used in the development environment.
- Arduino IDE
- OpenCV, NumPy, PySerial
- InsightFace and ONNX Runtime
- gspread and oauth2client
- Google Sheets API and Google Drive API enabled in the Google Cloud project

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Local setup

1. Upload `src/arduino/face_attendance_controller.ino` to the Arduino Nano.
2. From the project working directory, create a folder named `database/`.
3. Create one subfolder per registered person. Use the folder name as the attendance name.
4. Add clear JPG/JPEG/PNG reference images to each person's folder. Prefer one clearly visible face per image.
5. Create a Google service account, enable the Sheets and Drive APIs, download its JSON key as `credentials.json`, and share the **Face Attendance** spreadsheet with the service-account email.
6. Place `credentials.json` beside the script or update its path in the Python file.
7. Set `SERIAL_PORT` to the Arduino port (the development setup used `COM4`). Confirm `CAMERA_INDEX` if needed.
8. Run the script from the project root so relative paths resolve:

```bash
python src/python/face_attendance.py
```

## Google Sheets columns

| Column | Value |
|---|---|
| A | Date (DD-MM-YYYY) |
| B | Student name |
| C | Present / Absent |
| D | Time (HH:MM:SS) |

## Serial protocol

| Direction | Message | Meaning |
|---|---|---|
| Arduino → Python | `SCAN` | Start recognition |
| Arduino → Python | `CLOSE` | Close attendance |
| Python → Arduino | `OK:<name>` | Verification accepted |
| Python → Arduino | `FAIL` | Recognition or verification failed |
| Python → Arduino | `CLOSED` | Closing completed |
| Python → Arduino | `ALREADY_CLOSED` | Session already locked |

## Limitations, privacy and security

- A small printed ID portrait may not be detected reliably due to glare, blur, resolution or card layout.
- Two matching face detections do not prove that a live person is present. A printed or displayed photograph may pass this check.
- The similarity threshold `0.45` is a project tuning value and must be validated with the actual camera and lighting.
- Present/closed state is held in memory. Restarting Python resets the current-run set and closed flag; persistent daily-state handling is a future improvement.
- Face images and biometric embeddings are sensitive. Obtain appropriate consent and restrict access.
- Do not commit `database/`, `credentials.json`, biometric data or private attendance exports. These are excluded by `.gitignore`.
- NFC/RFID is not part of this project version.

## Testing

See [docs/testing.md](docs/testing.md). Test results are intentionally left unclaimed until recorded on the actual prototype.

## Contributions and AI disclosure

The project owner defined the project workflow, selected and assembled the hardware, prepared the face database, configured Google Sheets and the development environment, and tested the prototype. AI assistance was used for troubleshooting, code drafting/refinement and documentation. See [docs/contribution-and-ai-disclosure.md](docs/contribution-and-ai-disclosure.md) for details.

## Demo media

Add project photographs and the demonstration video under [media/](media/). The demo video has not yet been uploaded because its file or share link was not supplied in this conversation. See [media/README.md](media/README.md).

## License

The repository's existing MIT License is retained.
