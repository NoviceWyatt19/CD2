#include <Simpletimer.h>
#include <Wire.h>
#include <LiquidCrystal.h>
#include <LiquidCrystal_I2C.h> // LCD 2004 I2C용 라이브러리
LiquidCrystal_I2C lcd(0x27,20,4); // 접근주소 : 0x3F or 0x27

Simpletimer timer;

int mq3Pin = A3;    // MQ-3 센서핀을 아두이노 보드의 A3 핀으로 설정
int PulseSensorPurplePin = A0; // A0에 심박 센서를 할당
int PIR = 7; // 센서 변수를 D7에 초기화
int state = 0; // 센서 상태값 저장 변수 (0:Low,1:High)
int piezo = 8;  // 피에조 부저를 D8에 초기화
int Signal; // HeartSensor 관련 변수
int Threshold = 550; // HeartSensor 관련 변수
String inChar = "a"; // SleepSensor 관련 변수

void setup() {
  pinMode(piezo, OUTPUT); //piezo를 출력으로 설정
  pinMode(PIR,INPUT); //센서를 입력으로 설정
  Serial.begin(9600); //시리얼 통신, 속도는 9600
  Serial.println("$$$Arduino System Online.$$$"); // 라즈베리파이 연결 전송메세지
  inChar = "a";

  lcd.init(); // LCD 초기화
  lcd.backlight(); // 백라이트 켜기

  lcd.setCursor(0,0); // 1번째 줄 문자열 출력
  lcd.print("Alcol?");

  lcd.setCursor(0,1); // 2번째 줄 문자열 출력
  lcd.print("PIR?");

  lcd.setCursor(0,2); // 3번째 줄 문자열 출력
  lcd.print("Heart?");

  lcd.setCursor(0,3); // 4번째 줄 문자열 출력
  lcd.print("Sleep?");
}

void loop() {
  Alcol_Sensor();
  PIR_Sensor();
  Heart_Sensor();
  Sleep_Sensor();
  End_Loop(); 
}

//SleepSensor ------------------------------------------------------------

void Sleep_Sensor(){

  // timer.run();
  if (Serial.available() > 0) {
    inChar = Serial.readStringUntil('\n'); // 입력되는 문자 존재 확인

    if (inChar == "SLEEP_TRUE") {
      lcd.setCursor(0,3); // 4번째 줄 문자열 출력
      lcd.print("Sleep: Warning!");
      
      Sound_Do5(0.5);
      delay(100);
      Sound_Re5(0.5);
      delay(100);
      Sound_Do5(0.5);
      delay(100);
      Sound_Re5(0.5);
      delay(100);
    } else {
      lcd.setCursor(0,3); // 4번째 줄 문자열 출력
      lcd.print("Sleep: Safety");
    }
    delay(1000);
  }
}

//AlcolSensor ------------------------------------------------------------

void Alcol_Sensor()
{
  Serial.println(analogRead(mq3Pin));   // MQ-3 센서 출력값을 시리얼 모니터로 출력
  int alcol_val = analogRead(mq3Pin);          
  if(alcol_val>=600){                  // 센서 값이 600 이상이면
    lcd.setCursor(11,0); // 1번째 줄 문자열 출력
    lcd.print(alcol_val);

    Sound_Do5(0.5);
    delay(100);
    Sound_Re5(0.5);
    delay(100);
    Sound_Do5(0.5);
    delay(100);
    Sound_Re5(0.5);
    delay(100);
  }  
  else if(alcol_val>=200 && alcol_val<600){  // 센서 값이 200 이상, 600 미만이면
    lcd.setCursor(11,0); // 1번째 줄 문자열 출력
    lcd.print(alcol_val);
  }
  else if(alcol_val<200){               // 센서 값이 200 미만 이면
    lcd.setCursor(11,0); // 1번째 줄 문자열 출력
    lcd.print(alcol_val);
  }
  delay(1000);
}

// Heart_Sensor --------------------------------------------------------
// 심박수 측정 센서

void Heart_Sensor() {
  Signal = analogRead(PulseSensorPurplePin);
  Serial.println(Signal); // 현재 심박수를 출력합니다.

  if (Signal > Threshold) {
    lcd.setCursor(11,2); // 3번째 줄 문자열 출력
    lcd.print(Signal);
    
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
    lcd.setCursor(11,2); // 3번째 줄 문자열 출력
    lcd.print(Signal);
  }
  delay(1000); // 1초마다 체크
}


//PIR_SENSOR ---------------------------------------------------------------
//적외선 감지 센서

void PIR_Sensor()
{
  state = digitalRead(PIR); // PIR 센서값 입력 받음

  if(state==0){ // 센서 값이 0일 경우
    lcd.setCursor(0,1); // 2번째 줄 문자열 출력
    lcd.print("PIR Warning!");
    
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
    lcd.setCursor(0,1); // 2번째 줄 문자열 출력
    lcd.print("PIR Safety");
    
    Serial.println("OFF"); // 시리얼 통신에 센서값 출력
  }

  delay(1000); // 1초 대기
}

//End_Loop --------------------------------------------------------------
// 구동이 올바르게 되는지 확인하기 위한 루프 종료시 발생하는 함수

void End_Loop(){
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