# Design Decisions

1. **Laptop-side vision:** Arduino Nano handles I/O; Python on the laptop performs face inference and cloud spreadsheet access.
2. **InsightFace buffalo_s:** The configured CPU execution provider avoids requiring CUDA-capable hardware.
3. **Folder-based identity database:** Each student is represented by a folder under `database/`; folder name becomes the attendance name.
4. **Two camera stages:** The first identifies the attendee; the second checks for two detected faces that both match the first identity.
5. **No NFC/RFID:** NFC was removed from the current project workflow.
6. **One-button interaction:** Short press starts a scan; holding for at least two seconds requests attendance closing.
7. **Serial text protocol:** Simple newline-terminated messages make the Arduino/Python interface straightforward to debug.
8. **Session state:** Present names and the closed flag are stored in Python memory for the current run.

## Known limitations
- Face detection on a printed ID portrait may fail due to small image size, glare, blur or card layout.
- A threshold of 0.45 is a project setting, not a universal accuracy or security guarantee.
- Two-face matching is not liveness detection. A displayed or printed photo may satisfy the matching rule.
- Restarting Python resets the in-memory attendance set and closed flag. Cross-restart duplicate prevention would require reading today's sheet entries or persistent state.
