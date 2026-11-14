# Algorithm

## Startup
1. Open the configured Arduino serial port.
2. Connect to the Google Sheets service account and open the attendance spreadsheet.
3. Initialize InsightFace `buffalo_s` with the CPU execution provider.
4. Read reference images from each person folder under `database/` and create face embeddings.
5. Print `System Ready`.

## Short-press scan
1. Arduino sends `SCAN`.
2. Python opens the laptop camera for the initial scan.
3. The largest detected face is compared with the stored reference embeddings.
4. If no registered identity is found within the scan window, send `FAIL`.
5. If recognized, print `Welcome <name>`.
6. Print `Show your ID card`, wait two seconds, and open the camera again.
7. Require at least two detected faces in one frame.
8. Compare the two largest detected faces with the reference database. Both must match the identity from the first stage.
9. On success, append a Present row to Google Sheets if the name has not already been marked in this Python run, then send `OK:<name>`.
10. Otherwise send `FAIL`.

## Long-press close
1. Holding the button for at least two seconds sends `CLOSE`.
2. Iterate over person folders in `database/`.
3. Append an Absent row for each person not in the current run's Present set.
4. Print absent names and count.
5. Lock the current application session and send `CLOSED`.
6. Later scan requests are rejected with `ALREADY_CLOSED`.

## Serial protocol

| Direction | Message | Meaning |
|---|---|---|
| Arduino → Python | `SCAN` | Start recognition and ID stage |
| Arduino → Python | `CLOSE` | Close attendance |
| Python → Arduino | `OK:<name>` | Verification accepted |
| Python → Arduino | `FAIL` | Recognition/verification failed |
| Python → Arduino | `CLOSED` | Attendance close completed |
| Python → Arduino | `ALREADY_CLOSED` | Session already locked |

The ID-stage rule is a prototype face-matching check, not proof of liveness or resistance to photo replay.
