# System Architecture

```text
[Push Button] -> [Arduino Nano] --USB Serial--> [Python Application]
                       |                              |
                       +--> [16x2 I2C LCD]             +--> [Laptop Camera]
                       +--> [Buzzer]                   +--> [InsightFace buffalo_s]
                       +--> [Red LED]                  +--> [database/ reference images]
                                                      +--> [Google Sheets API]
```

## Responsibilities

### Arduino Nano
- Reads the push button and distinguishes short press from a hold of at least two seconds.
- Displays prompts and results on the LCD.
- Drives the buzzer and red LED.
- Exchanges newline-terminated serial messages with Python.

### Python application
- Manages serial communication and Google Sheets access.
- Loads reference images and generates InsightFace embeddings.
- Captures webcam frames and performs the two-stage matching workflow.
- Writes Present/Absent rows and locks attendance for the current run after closing.

### Google Sheets
Stores date, student name, status and time.

The Arduino handles physical interaction while the laptop performs face inference and spreadsheet operations. Serial communication uses 9600 baud.
