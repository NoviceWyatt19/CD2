// #include <Simpletimer.h>
#include <Wire.h>

// Simpletimer timer;

int mq3Pin = A5; // alcol sensor A5
int PIR = D7; // 센서 변수를 D7에 초기화

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
  int value1 = analogRead(mq3Pin);  // 첫 번째 센서 값 읽기
  int value2 = digitalRead(PIR);  // 두 번째 센서 값 읽기
  int value3 = analogRead(heart.PulseSensorPurplePin);  // 세 번째 센서 값 읽기

  Serial.print(value1);
  Serial.print(",");
  Serial.print(value2);
  Serial.print(",");
  Serial.println(value3);  // 마지막 값은 println으로 줄바꿈 포함

  Serial.flush();  // 전송 버퍼를 비우기
  
  delay(1000);  // 1초 대기
}