import os
import sys
import time
import warnings
import logging
from datetime import datetime

# Set runtime logging controls before importing InsightFace.
os.environ["INSIGHTFACE_LOG_LEVEL"] = "ERROR"
os.environ["ORT_LOG_SEVERITY_LEVEL"] = "3"
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)

class HiddenPrints:
    def __enter__(self):
        self.original_stdout = sys.stdout
        self.sink = open(os.devnull, "w")
        sys.stdout = self.sink
    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.original_stdout
        self.sink.close()

import cv2
import numpy as np
import serial
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from insightface.app import FaceAnalysis

SERIAL_PORT = "COM4"  # Change to the Arduino port on your computer.
BAUD_RATE = 9600
CAMERA_INDEX = 0
DB_PATH = "database"
SHEET_NAME = "Face Attendance"
FACE_THRESHOLD = 0.45
INITIAL_SCAN_SECONDS = 4
ID_SCAN_SECONDS = 6
ID_CAMERA_DELAY_SECONDS = 2

arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)
arduino.reset_input_buffer()

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)
google_client = gspread.authorize(credentials)
sheet = google_client.open(SHEET_NAME).sheet1

today = datetime.now().strftime("%d-%m-%Y")
marked_today = set()
attendance_closed = False

with HiddenPrints():
    face_app = FaceAnalysis(
        name="buffalo_s",
        providers=["CPUExecutionProvider"],
    )
    face_app.prepare(ctx_id=0, det_size=(640, 640))

if not os.path.isdir(DB_PATH):
    raise FileNotFoundError(f"Face database folder not found: {DB_PATH}")

known_embeddings = []
known_names = []
for person_name in sorted(os.listdir(DB_PATH)):
    person_dir = os.path.join(DB_PATH, person_name)
    if not os.path.isdir(person_dir):
        continue
    for image_name in sorted(os.listdir(person_dir)):
        if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        image_path = os.path.join(person_dir, image_name)
        image = cv2.imread(image_path)
        if image is None:
            print(f"Skipping unreadable image: {image_path}")
            continue
        faces = face_app.get(image)
        if faces:
            known_embeddings.append(faces[0].embedding)
            known_names.append(person_name)

known_embeddings = np.asarray(known_embeddings, dtype=np.float32)
if len(known_embeddings) == 0:
    print("Warning: no usable reference-face embeddings were loaded.")

def recognize_face(embedding):
    if len(known_embeddings) == 0:
        return "Unknown"
    similarities = np.dot(known_embeddings, embedding)
    best_index = int(np.argmax(similarities))
    return known_names[best_index] if similarities[best_index] >= FACE_THRESHOLD else "Unknown"

def open_camera():
    camera = cv2.VideoCapture(CAMERA_INDEX)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError("Could not open laptop camera. Check CAMERA_INDEX.")
    return camera

def scan_initial_face():
    print("Scanning face...")
    camera = open_camera()
    recognized_name = "Unknown"
    started_at = time.time()
    try:
        while time.time() - started_at < INITIAL_SCAN_SECONDS:
            ok, frame = camera.read()
            if not ok:
                continue
            faces = face_app.get(frame)
            if faces:
                face = max(
                    faces,
                    key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]),
                )
                candidate = recognize_face(face.embedding)
                if candidate != "Unknown":
                    recognized_name = candidate
                    cv2.putText(frame, f"Welcome {candidate}", (20, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.imshow("Face Scan", frame)
                    cv2.waitKey(700)
                    break
            cv2.putText(frame, "Scanning Face", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.imshow("Face Scan", frame)
            if cv2.waitKey(1) == 27:
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
    return recognized_name

def verify_id_with_two_faces(expected_name):
    print("Show your ID card")
    time.sleep(ID_CAMERA_DELAY_SECONDS)
    print("Scanning ID...")
    camera = open_camera()
    verified = False
    started_at = time.time()
    try:
        while time.time() - started_at < ID_SCAN_SECONDS:
            ok, frame = camera.read()
            if not ok:
                continue
            faces = face_app.get(frame)
            if len(faces) >= 2:
                largest_two = sorted(
                    faces,
                    key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]),
                    reverse=True,
                )[:2]
                first = recognize_face(largest_two[0].embedding)
                second = recognize_face(largest_two[1].embedding)
                if first == expected_name and second == expected_name:
                    verified = True
                    cv2.putText(frame, "ID Verification Passed", (20, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow("ID Verification", frame)
                    cv2.waitKey(700)
                    break
            cv2.putText(frame, "Show face and ID photo", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.imshow("ID Verification", frame)
            if cv2.waitKey(1) == 27:
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
    return verified

def mark_absentees():
    print("Attendance Closing...")
    current_time = datetime.now().strftime("%H:%M:%S")
    absent_names = []
    for person_name in sorted(os.listdir(DB_PATH)):
        person_dir = os.path.join(DB_PATH, person_name)
        if os.path.isdir(person_dir) and person_name not in marked_today:
            sheet.append_row([today, person_name, "Absent", current_time])
            absent_names.append(person_name)
            print(f"{person_name} - Absent")
    print(f"Total Absent: {len(absent_names)}")
    print("Attendance Closed")

print("System Ready")
try:
    while True:
        if not arduino.in_waiting:
            time.sleep(0.05)
            continue
        command = arduino.readline().decode("utf-8", errors="ignore").strip()

        if command == "CLOSE":
            if attendance_closed:
                print("Attendance already closed")
                arduino.write(b"ALREADY_CLOSED\n")
                continue
            try:
                mark_absentees()
                attendance_closed = True
                arduino.write(b"CLOSED\n")
            except Exception as error:
                print(f"Attendance closing error: {error}")
            continue

        if command == "SCAN":
            if attendance_closed:
                print("Attendance already closed")
                arduino.write(b"ALREADY_CLOSED\n")
                continue
            try:
                name = scan_initial_face()
                if name == "Unknown":
                    print("Face not recognized")
                    arduino.write(b"FAIL\n")
                    continue
                print(f"Welcome {name}")
                verified = verify_id_with_two_faces(name)
                if not verified:
                    print("ID verification failed")
                    arduino.write(b"FAIL\n")
                    continue

                current_time = datetime.now().strftime("%H:%M:%S")
                if name not in marked_today:
                    sheet.append_row([today, name, "Present", current_time])
                    marked_today.add(name)
                    print(f"{name} - Attendance Marked")
                else:
                    print(f"{name} - Already marked Present today")
                arduino.write(f"OK:{name}\n".encode("utf-8"))
            except Exception as error:
                print(f"Scan error: {error}")
                arduino.write(b"FAIL\n")
except KeyboardInterrupt:
    print("\nSystem stopped by user.")
finally:
    if arduino.is_open:
        arduino.close()
    cv2.destroyAllWindows()
