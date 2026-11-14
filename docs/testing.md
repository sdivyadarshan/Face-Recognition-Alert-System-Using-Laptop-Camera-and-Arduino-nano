# Testing and Validation

Record actual results after running each test on the prototype. No test is marked passed by default.

## Hardware
- [ ] Arduino Nano sketch uploads successfully.
- [ ] LCD initializes and displays the home screen.
- [ ] Short button press sends one SCAN command.
- [ ] Button hold of at least two seconds sends one CLOSE command.
- [ ] Buzzer feedback is audible and distinguishable.
- [ ] Red LED indicates failure.
- [ ] USB serial communication works at 9600 baud.

## Software setup
- [ ] Python dependencies install successfully.
- [ ] InsightFace model initializes.
- [ ] Correct COM port and camera index are configured.
- [ ] `credentials.json` exists locally and is excluded from Git.
- [ ] Google Sheet is shared with the service-account email.
- [ ] Each database person folder contains readable reference images.

## Functional
- [ ] Startup prints `System Ready`.
- [ ] Short press opens initial face scan.
- [ ] Unknown identity returns FAIL.
- [ ] Known identity prints Welcome and advances to ID prompt.
- [ ] ID prompt waits two seconds before second camera stage.
- [ ] ID stage requires two detected faces matching the first identity.
- [ ] Success writes one Present row and sends OK:<name>.
- [ ] Failure does not write Present and sends FAIL.
- [ ] Repeat success does not add another Present row during the same run.
- [ ] Long press marks remaining database people Absent.
- [ ] Attendance close confirmation is received by Arduino.
- [ ] Scan after closing is rejected without opening the camera.

## Results log

| Date | Test | Expected | Actual result |
|---|---|---|---|
| TBD | Face recognition | Registered name / Unknown | Not recorded |
| TBD | ID stage | Two matching identities | Not recorded |
| TBD | Google Sheets write | Correct attendance row | Not recorded |
| TBD | Attendance close | Remaining names Absent | Not recorded |
| TBD | Post-close scan | Scan blocked | Not recorded |

## Troubleshooting
- Close Arduino Serial Monitor if the Python process cannot access the COM port.
- Close other applications using the webcam if camera initialization fails.
- Check reference image quality and lighting if a registered face is Unknown.
- Reduce glare and improve framing if the ID portrait is not detected.
- Check Google API enablement and spreadsheet sharing if Sheets access fails.
