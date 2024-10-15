#include <Simpletimer.h>
#include <Wire.h>
#include <LiquidCrystal.h>
#include <LiquidCrystal_I2C.h> // LCD 2004 I2C용 라이브러리
LiquidCrystal_I2C lcd(0x27,20,4); // 접근주소 : 0x3F or 0x27

Simpletimer timer;

int sensor=A2 // 압전 센서핀을  A2핀으로 설정
int mq3Pin = A3;    // MQ-3 센서핀을 아두이노 보드의 A3 핀으로 설정
int PulseSensorPurplePin = A0; // A0에 심박 센서를 할당
int state = 0; // 센서 상태값 저장 변수 (0:Low,1:High)
int piezo = 8;  // 피에조 부저를 D8에 초기화
int Signal; // HeartSensor 관련 변수
int Threshold = 550; // HeartSensor 관련 변수
String inChar = "a"; // SleepSensor 관련 변수
int alcol_sensor_val = 600; // alcolSensor 관련 변수
int Alcol_Flag = 0;
int Heart_Flag = 0;
int Sleep_Flag = 0;
int SensorCheck = 0;

void setup() {
  pinMode(piezo, OUTPUT); //piezo를 출력으로 설정
  pinMode(PIR,INPUT); //센서를 입력으로 설정
  Serial.begin(9600); //시리얼 통신, 속도는 9600
  Serial.println("$$$Arduino System Online.$$$"); // 라즈베리파이 연결 전송메세지
  inChar = "a";
  alcol_sensor_val = 600;
  Alcol_Flag = 0;
  Heart_Flag = 0;
  Sleep_Flag = 0;
  SensorCheck = 0;

  lcd.init(); // LCD 초기화
  lcd.backlight(); // 백라이트 켜기

  lcd.setCursor(0,0); // 1번째 줄 문자열 출력
  lcd.print("Sensor ON");

  lcd.setCursor(0,1); // 2번째 줄 문자열 출력
  lcd.print("Alcol?");

  lcd.setCursor(0,2); // 3번째 줄 문자열 출력
  lcd.print("Heart?");

  lcd.setCursor(0,3); // 4번째 줄 문자열 출력
  lcd.print("Sleep?");
}

void loop() {
  Alcol_Sensor();
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
      lcd.print("Sleep Warning!");
      Sleep_Flag = 1;
      
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
      lcd.print("Sleep Safety");
      Sleep_Flag = 0;
    }
    delay(1000);
  }
}

//AlcolSensor ------------------------------------------------------------

void Alcol_Sensor()
{
  Serial.println(analogRead(mq3Pin));   // MQ-3 센서 출력값을 시리얼 모니터로 출력
  int alcol_val = analogRead(mq3Pin);          
  if(alcol_val>=alcol_sensor_val){                  // 센서 값이 600 이상이면
    lcd.setCursor(11,1); // 1번째 줄 문자열 출력
    lcd.print(alcol_val);
    Alcol_Flag = 1;

    Sound_Do5(0.5);
    delay(100);
    Sound_Re5(0.5);
    delay(100);
    Sound_Do5(0.5);
    delay(100);
    Sound_Re5(0.5);
    delay(100);
    
  }  
  else {  // 센서 값이 200 이상, 600 미만이면
    lcd.setCursor(11,1); // 1번째 줄 문자열 출력
    lcd.print(alcol_val);
  }

  alcol_sensor_val = alcol_val;

  if(alcol_sensor_val<600){
      alcol_sensor_val=600;
      Alcol_Flag = 0;
    }
    
  delay(1000);
}

// Heart_Sensor --------------------------------------------------------
// 심박수 측정 센서

void Heart_Sensor() {
  Signal = analogRead(PulseSensorPurplePin);
  Serial.println(Signal); // 현재 심박수를 출력합니다.
  analogRead(sensor);
  if(val>120){
    z

  }
  else{

  }

  
  delay(1000); // 1초마다 체크
}

//End_Loop --------------------------------------------------------------
// 구동이 올바르게 되는지 확인하기 위한 루프 종료시 발생하는 함수

void End_Loop(){
  
  SensorCheck = Alcol_Flag + Heart_Flag + Sleep_Flag;

  if(SensorCheck>1){
    lcd.setCursor(0,0); // 1번째 줄 문자열 출력
    lcd.print("Sensor Warning");
    Sound_Do6(0.5);
    delay(100);
    Sound_Do6(0.5);
    delay(1000);
  }
  else{
    lcd.setCursor(0,0); // 1번째 줄 문자열 출력
    lcd.print("Sensor ON        ");
    Sound_Do6(0.5);
    delay(1000);
  }
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