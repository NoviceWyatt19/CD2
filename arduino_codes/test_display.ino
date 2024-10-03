#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);  // Set the LCD I2C address (usually 0x27 or 0x3F) and size (16x2 or 20x4)

int mq3Pin = A3;    // MQ-3 센서핀을 아두이노 보드의 A3 핀으로 설정
int PulseSensorPurplePin = A0; // A0에 심박 센서를 할당
int PIR = 7; // 센서 변수를 D7에 초기화
int state = 0; // 센서 상태값 저장 변수 (0:Low,1:High)
int piezo = 8;  // 피에조 부저를 D8에 초기화
int Signal; // HeartSensor 관련 변수
int Threshold = 550; // HeartSensor 관련 변수

void setup() {
    pinMode(piezo, OUTPUT); //piezo를 출력으로 설정
    pinMode(PIR,INPUT); //센서를 입력으로 설정

    lcd.init();           // Initialize the LCD
    lcd.backlight();      // Turn on the backlight

    lcd.setCursor(0, 0);  // Set the cursor to the first line, first column
    lcd.print("Alcol Val:"); // Display static text

    lcd.setCursor(0, 1);  // Set the cursor to the first line, first column
    lcd.print("Heart Val:"); // Display static text

    lcd.setCursor(0, 2);  // Set the cursor to the first line, first column
    lcd.print("PIR Val:"); // Display static text
}

void loop() {
    int alcol_val = analogRead(mq3Pin);
    Signal = analogRead(PulseSensorPurplePin);
    state = digitalRead(PIR); // PIR 센서값 입력 받음


    // Update the LCD with sensor values
    lcd.setCursor(11, 0);           // Set the cursor to the second line
    // lcd.print("                "); // Clear the previous number (for consistent display)
    lcd.setCursor(11, 0);           // Reset the cursor to the start of the second line
    lcd.print(alcol_val);        // Display the sensor value as a number

    lcd.setCursor(11, 1);           // Set the cursor to the second line
    // lcd.print("                "); // Clear the previous number (for consistent display)
    lcd.setCursor(11, 1);           // Reset the cursor to the start of the second line
    lcd.print(Signal);        // Display the sensor value as a number

    lcd.setCursor(11, 2);           // Set the cursor to the second line
    // lcd.print("                "); // Clear the previous number (for consistent display)
    lcd.setCursor(11, 2);           // Reset the cursor to the start of the second line
    lcd.print(state);        // Display the sensor value as a number

    delay(1000);  // Wait for a second before updating again
}