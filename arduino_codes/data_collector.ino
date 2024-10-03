// #include <Simpletimer.h>
#include <Wire.h>
#include <LiquidCrystal.h>
#include <LiquidCrystal_I2C.h> // LCD 2004 I2C용 라이브러리
LiquidCrystal_I2C lcd(0x27,20,4); // 접근주소 : 0x3F or 0x27

// Simpletimer timer;

int mq3Pin = A5; // alcol sensor A5
int PIR = 7; // 센서 변수를 D7에 초기화

struct HeartPulse
{
    int PulseSensorPurplePin = A0; // heart bps sensor A0
    int Signal; // HeartSensor 관련 변수
    int Threshold = 550; // HeartSensor 관련 변수
} heart;


void setup() {
  Serial.begin(9600);  // 빠른 시리얼 통신 9600, 115200
  pinMode(PIR,INPUT); //센서를 입력으로 설정
}

void loop() {
  int alcolValue = analogRead(mq3Pin);  // 첫 번째 센서 값 읽기
  int pirValue = digitalRead(PIR);  // 두 번째 센서 값 읽기
  int heartValue = analogRead(heart.PulseSensorPurplePin);  // 세 번째 센서 값 읽기

  Serial.print(alcolValue);
  Serial.print(",");
  Serial.print(pirValue);
  Serial.print(",");
  Serial.println(heartValue);  // 마지막 값은 println으로 줄바꿈 포함

  Serial.flush();  // 전송 버퍼를 비우기
  
  delay(1000);  // 1초 대기
}