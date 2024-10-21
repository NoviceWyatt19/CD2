#include <Simpletimer.h>
#include <Wire.h>
#include <LiquidCrystal.h>
#include <LiquidCrystal_I2C.h> // LCD 2004 I2C용 라이브러리
LiquidCrystal_I2C lcd(0x27,20,4); // 접근주소 : 0x3F or 0x27

int mq3Pin = A3;    // MQ-3 센서핀을 아두이노 보드의 A3 핀으로 설정
int PulseSensorPurplePin = A0; // A0에 심박 센서를 할당
int sensor = A2; // 압전 센서핀을 A2번 할당
int piezo = 8;  // 피에조 부저를 D8에 초기화
int in1 = 6; // 모터동력1 D6 할당
int in2 = 5; // 모터동력1 D5 할당

int Signal; // HeartSensor 관련 변수
int Threshold = 550; // HeartSensor 관련 변수
String inChar = "a"; // SleepSensor 관련 변수
int alcol_sensor_val = 600; // alcolSensor 관련 변수
int step_val = 0 // 현재 loop 분기를 정할 변수



void setup() {
  // put your setup code here, to run once:
  pinMode(piezo, OUTPUT); //piezo를 출력으로 설정
  pinMode(in1,OUTPUT);
  pinMode(in2,OUTPUT); // 각 포트 출력으로 사용

  Serial.begin(9600); //시리얼 통신, 속도는 9600
  Serial.println("$$$Arduino System Online.$$$"); // 라즈베리파이 연결 전송메세지

  inChar = "a"; // SleepSensor 관련 변수
  alcol_sensor_val = 600; // alcolSensor 관련 변수
  Threshold = 550; // HeartSensor 관련 변수
  step_val = 1;// 현재 loop 분기를 정할 변수

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
  // put your main code here, to run repeatedly:
  switch(step_val)
  {
    case 1:
    Step1_HeartANDAlcol();
    break;
    case 2:
    Step2_Voice();
    break;
    case 3:
    Step3_Sleep();
    break;
    case 4:
    Step4_TurnON();
    break;
    default:
    step_val = 1;
    break;
  }
  End_Loop(); 
}

// Step1_HeartANDAlcol ----------------------------------------------------

void Step1_HeartANDAlcol()
{
  Heart_Sensor();
}

// Step2_Voice ----------------------------------------------------

void Step2_Voice()
{
  step_val = 3;
  delay(1000);
}

// Step3_Sleep -----------------------------------------------------

void Step3_Sleep()
{
  Sleep_Sensor();
}

// Step4_TurnON ---------------------------------------------------------

void Step4_TurnON()
{
  lcd.setCursor(0,0); // 1번째 줄 문자열 출력
  lcd.print("Vehicle Turn ON        ");
  Sound_Do6(0.5);

  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW); // 앞으로 계속 회전

  delay(1000);

  lcd.setCursor(0,0); // 1번째 줄 문자열 출력
  lcd.print("Vehicle Turn OFF        ");
  Sound_Do6(0.5);

  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW); // 회전 정지

  delay(1000);

  step_val = 1; // 다시 처음으로
}

//AlcolSensor ------------------------------------------------------------

void Alcol_Sensor()
{
  Serial.println(analogRead(mq3Pin));   // MQ-3 센서 출력값을 시리얼 모니터로 출력
  int alcol_val = analogRead(mq3Pin);          
  if(alcol_val>=alcol_sensor_val){                  // 센서 값이 alcol_sensor_val 이상이면
    lcd.setCursor(11,1); // 1번째 줄 문자열 출력
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
  else {  // 센서 값이 alcol_sensor_val 미만이면 이상없음
    lcd.setCursor(11,1); // 1번째 줄 문자열 출력
    lcd.print(alcol_val);

    step_val = 2; // 다음 스텝으로 진행
  }

  alcol_sensor_val = alcol_val;

  if(alcol_sensor_val<600){
    alcol_sensor_val=600;
  }
    
  delay(1000);
}

// Heart_Sensor --------------------------------------------------------
// 심박수 측정 센서

void Heart_Sensor() {
  int val = analogRead(sensor); // 압전 센서의 데이터 받아오기
  
  if (val>120) // 압전 센서 데이터 값으로 LED 제어
  {
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

      delay(1000); // 1초마다 체크
    }

    else { // 이상없음 분기
      lcd.setCursor(11,2); // 3번째 줄 문자열 출력
      lcd.print(Signal);

      delay(1000); // 1초마다 체크
      Alcol_Sensor();
    }
  }
  else // 손을 안 댈 때 분기
  {
    lcd.setCursor(11,2); // 3번째 줄 문자열 출력
    lcd.print("No Signal               ");

    delay(1000); // 1초마다 체크
  }
}

//SleepSensor ------------------------------------------------------------

void Sleep_Sensor(){

  // timer.run();
  if (Serial.available() > 0) {
    inChar = Serial.readStringUntil('\n'); // 입력되는 문자 존재 확인

    if (inChar == "SLEEP_TRUE") {
      lcd.setCursor(0,3); // 4번째 줄 문자열 출력
      lcd.print("Sleep Warning!");
      
      Sound_Do5(0.5);
      delay(100);
      Sound_Re5(0.5);
      delay(100);
      Sound_Do5(0.5);
      delay(100);
      Sound_Re5(0.5);
      delay(100);

      step_val = 1; // 처음 스텝으로 돌아가기

    } else { // 문제없음 분기
      lcd.setCursor(0,3); // 4번째 줄 문자열 출력
      lcd.print("Sleep Safety");

      step_val = 4; // 다음 스텝으로 진행하기
    }
    delay(1000);
  }
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