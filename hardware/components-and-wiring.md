# Hardware Components and Wiring

## Components

| Component | Qty. | Purpose |
|---|---:|---|
| Arduino Nano | 1 | Hardware controller and USB serial interface |
| 16x2 LCD with I2C backpack | 1 | Prompts and attendance status |
| Push button | 1 | Short press to scan; hold for 2 seconds to close |
| Buzzer | 1 | Success/failure/close feedback |
| Red LED | 1 | Verification-failure indicator |
| Current-limiting resistor | 1 | LED protection |
| Breadboard and jumper wires | As needed | Prototype wiring |
| Laptop with webcam | 1 | Face processing and Google Sheets connection |

## Pin connections

| Module | Signal | Arduino Nano |
|---|---|---|
| Push button | Terminal 1 | D9 |
| Push button | Terminal 2 | GND |
| Buzzer | Signal / positive | D8 |
| Buzzer | GND / negative | GND |
| Red LED | Anode through resistor | D4 |
| Red LED | Cathode | GND |
| I2C LCD | SDA | A4 |
| I2C LCD | SCL | A5 |
| I2C LCD | VCC | 5V (for a 5V-compatible module) |
| I2C LCD | GND | GND |

The laptop connects to the Arduino over USB. The built-in laptop camera is used by the Python program.

## Notes
- The sketch uses LCD address `0x27`; some backpacks use `0x3F`.
- Confirm buzzer type/polarity and use a suitable resistor in series with the LED.
- The Python serial-port setting is `COM4` from the development setup; change it if necessary.
- NFC/RFID is not used in this version.
