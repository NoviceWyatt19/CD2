#include <Wire.h>
#include <LiquidCrystal.h>

int PulseSensorPurplePin = A0; // A0에 심박 센서를 할당
int PIR = 7; // 센서 변수를 D7에 초기화
int state = 0; // 센서 상태값 저장 변수 (0:Low,1:High)
int piezo = 8;  // 피에조 부저를 D8에 초기화
int Signal; // HeartSensor 관련 변수
int Threshold = 550; // HeartSensor 관련 변수

void setup() {
  pinMode(piezo, OUTPUT); //piezo를 출력으로 설정
  pinMode(PIR,INPUT); //센서를 입력으로 설정
  Serial.begin(9600); //시리얼 통신, 속도는 9600
  Serial.println("$$$Arduino System Online.$$$"); // 라즈베리파이 연결 전송메세지

}

void loop() {
  PIR_Sensor();
  Heart_Sensor();
  End_Loop(); 
}

// Heart_Sensor --------------------------------------------------------
// 심박수 측정 센서

void Heart_Sensor() {
  Signal = analogRead(PulseSensorPurplePin);
  Serial.println(Signal); // 현재 심박수를 출력합니다.

  if (Signal > Threshold) {
    Sound_Do5(0.5); // 특정 심박수 이상 시 소리를 낸다.
    delay(100);
    Sound_Re5(0.5);
    delay(100);
    Sound_Do5(0.5); 
    delay(100);
    Sound_Re5(0.5);
    delay(100);
  }

  else {
    Sound_Do5(0.5); 
    delay(100);
    Sound_Do5(0.5); 
    delay(100);
  }
  delay(100); // 0.1초마다 체크
}


//PIR_SENSOR ---------------------------------------------------------------
//적외선 감지 센서

void PIR_Sensor()
{
  state = digitalRead(PIR); // PIR 센서값 입력 받음

  digitalWrite(LED,LOW); // 초기 LED값을 OFF로 설정

  if(state==0){ // 센서 값이 0일 경우
    Serial.println("ON"); // 시리얼 통신에 센서값 출력
    Sound_Do5(0.5); // 센서 감지시 소리를 낸다.
    delay(100);
    Sound_Re5(0.5);
    delay(100);
    Sound_Do5(0.5); 
    delay(100);
    Sound_Re5(0.5);
    delay(100);
  }
  else { // 센서 값이 1일 경우
    Serial.println("OFF"); // 시리얼 통신에 센서값 출력
    Sound_Do5(0.5); 
    delay(100);
    Sound_Do5(0.5); 
    delay(100);
  }

  delay(1000); // 1초 대기
}

//End_Loop --------------------------------------------------------------
// 구동이 올바르게 되는지 확인하기 위한 루프 종료시 발생하는 함수

void End_Loop(){
  Sound_Do6(0.5);
  delay(100);
  Sound_Do6(0.5);
  delay(1000);
}

// Piezo -----------------------------------------------------------------
// 부저의 소리를 담당하는 함수

void Sound_Do5(double sec){
  tone(piezo, 523); // 5옥타브 도
  delay(1000 * sec);
  noTone(piezo);
}

void Sound_Re5(double sec){
  tone(piezo, 587); // 레
  delay(1000 * sec);
  noTone(piezo);
}

void Sound_Mi5(double sec){
  tone(piezo, 659); // 미
  delay(1000 * sec);
  noTone(piezo);
}

void Sound_Pa5(double sec){
  tone(piezo, 698); // 파
  delay(1000 * sec);
  noTone(piezo);
}

void Sound_Sol5(double sec){
  tone(piezo, 784); // 솔
  delay(1000 * sec);
  noTone(piezo);
}

void Sound_La5(double sec){
  tone(piezo, 880); // 라
  delay(1000 * sec);
  noTone(piezo);
}

void Sound_Shi5(double sec){
  tone(piezo, 988); // 시
  delay(1000 * sec);
  noTone(piezo);
}

void Sound_Do6(double sec){
  tone(piezo, 1046); // 6옥타브 도
  delay(1000 * sec);
  noTone(piezo);
}