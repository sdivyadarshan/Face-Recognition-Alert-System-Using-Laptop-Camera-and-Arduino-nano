#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);
#define SCAN_BTN 9
#define BUZZ 8
#define LED_RED 4

const unsigned long LONG_PRESS_MS = 2000;
const unsigned long DEBOUNCE_MS = 35;
unsigned long pressStart = 0;
unsigned long lastButtonChange = 0;
bool buttonWasPressed = false;
bool pressHandled = false;
bool attendanceClosed = false;

void beep(unsigned int durationMs) {
  digitalWrite(BUZZ, HIGH);
  delay(durationMs);
  digitalWrite(BUZZ, LOW);
}

void beepSuccess() {
  beep(90);
  delay(90);
  beep(90);
}

void showHome() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Face Attendance");
  lcd.setCursor(0, 1);
  lcd.print(attendanceClosed ? "Attendance Closed" : "Press SCAN");
}

void setup() {
  pinMode(SCAN_BTN, INPUT_PULLUP);
  pinMode(BUZZ, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  digitalWrite(BUZZ, LOW);
  digitalWrite(LED_RED, LOW);
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  showHome();
}

void loop() {
  const bool pressed = (digitalRead(SCAN_BTN) == LOW);

  if (pressed && !buttonWasPressed && millis() - lastButtonChange >= DEBOUNCE_MS) {
    buttonWasPressed = true;
    pressHandled = false;
    pressStart = millis();
    lastButtonChange = millis();
  }

  if (pressed && buttonWasPressed && !pressHandled && millis() - pressStart >= LONG_PRESS_MS) {
    pressHandled = true;
    if (attendanceClosed) {
      lcd.clear();
      lcd.print("Already Closed");
      beep(120);
    } else {
      lcd.clear();
      lcd.print("Attendance");
      lcd.setCursor(0, 1);
      lcd.print("Closing...");
      Serial.println("CLOSE");
    }
  }

  if (!pressed && buttonWasPressed && millis() - lastButtonChange >= DEBOUNCE_MS) {
    const unsigned long duration = millis() - pressStart;
    buttonWasPressed = false;
    lastButtonChange = millis();
    if (!pressHandled) {
      if (attendanceClosed) {
        lcd.clear();
        lcd.print("Attendance");
        lcd.setCursor(0, 1);
        lcd.print("Already Closed");
        beep(120);
      } else if (duration < LONG_PRESS_MS) {
        lcd.clear();
        lcd.print("Scanning Face...");
        lcd.setCursor(0, 1);
        lcd.print("Please Wait");
        Serial.println("SCAN");
      }
    }
  }

  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();
    if (msg.startsWith("OK:")) {
      String name = msg.substring(3);
      digitalWrite(LED_RED, LOW);
      lcd.clear();
      lcd.print("Welcome ");
      lcd.print(name.substring(0, 8));
      lcd.setCursor(0, 1);
      lcd.print("Present Marked");
      beepSuccess();
      delay(1800);
      showHome();
    } else if (msg == "FAIL") {
      digitalWrite(LED_RED, HIGH);
      lcd.clear();
      lcd.print("Verification");
      lcd.setCursor(0, 1);
      lcd.print("Failed - Retry");
      beep(180);
      delay(1500);
      digitalWrite(LED_RED, LOW);
      showHome();
    } else if (msg == "CLOSED") {
      attendanceClosed = true;
      digitalWrite(LED_RED, LOW);
      lcd.clear();
      lcd.print("Attendance");
      lcd.setCursor(0, 1);
      lcd.print("Closed!");
      beepSuccess();
      delay(1800);
      showHome();
    } else if (msg == "ALREADY_CLOSED") {
      attendanceClosed = true;
      lcd.clear();
      lcd.print("Attendance");
      lcd.setCursor(0, 1);
      lcd.print("Already Closed");
      beep(120);
      delay(1500);
      showHome();
    }
  }
}
