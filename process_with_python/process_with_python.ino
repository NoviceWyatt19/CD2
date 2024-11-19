#include <Simpletimer.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <LiquidCrystal.h>

int mq3Pin = A3;    // MQ-3 센서핀을 아두이노 보드의 A3 핀으로 설정
int alcol_sensor_val = 600; // alcolSensor 관련 변수

int PulseSensorPurplePin = A0; // A0에 심박 센서를 할당
int Signal; // HeartSensor 관련 변수
int Threshold = 550; // HeartSensor 관련 변수

int piezo = 9;  // 피에조 부저를 D9에 초기화

int in1 = 6; // 모터동력1 D6 할당
int in2 = 5; // 모터동력1 D5 할당

SoftwareSerial voiceSerial(8,7); // D8,D7 Voice 할당 Rx,Tx
char id , acc; // voice 관련 변수

String receivedData;  // 수신된 데이터 저장 변수
String finalGiven;    // "FINAL_"을 잘라낸 값 저장 변수

String given;
bool sensorData = true;    // sensorData는 상황에 맞게 값 변경이 필요할 수 있음

const unsigned long sensingTime = 30000; // 각 케이스 당 센싱 시간을 20초로 지정 총 60초 동안 진행
unsigned long StartTime = 0;  // 센싱 시작 시각 저장
bool allSensingDone = false; // 모든 센싱 완료 여부

unsigned int dataSum;
unsigned int dataCount;
unsigned int averageValue = 0;

enum Sensor{
    HEART,
    ALCOHOL,
    VOICE
};
Sensor currentSensing = HEART;

void setup() {
  pinMode(piezo, OUTPUT); //piezo를 출력으로 설정
  pinMode(in1,OUTPUT);
  pinMode(in2,OUTPUT); // 각 포트 출력으로 사용

  Serial.begin(9600); //시리얼 통신, 속도는 9600

  alcol_sensor_val = 600; // alcolSensor 관련 변수
  Threshold = 550; // HeartSensor 관련 변수

  voiceSerial.begin(9600);//voice 관련 할당
  voiceSerial.listen();

  given = "";
  receivedData = "";
  finalGiven = "";
  sensorData = false;
  dataSum=0;
  dataCount=0;
  averageValue = 0;
  allSensingDone = false;
}

void loop() {
  // 1. 파이썬에서 데이터 수신
  if (Serial.available() > 0) {
    given = Serial.readStringUntil('\n');
    given.trim();

    // 2. 수신된 문자열의 길이가 6보다 긴 경우
    if (given.length() > 9) {                                                         
      finalGiven = given.substring(6);  // "FINAL_"을 제외한 값 저장
      Serial.println("Successfully given final state");

    } else {
      receivedData = given;  // "True" 또는 "False" 값이 directly 저장
      Serial.println("Successfully given oper state");
    }

    given = ""; // 다음 문자열을 받기위해 초기화
  }

  // 3. receivedData가 "False"일 때 계속 메인 코드 실행
  if( receivedData == "False" )
    StartTime = millis();  // 타이머 시작 시간 기록
  while (receivedData == "False") {

    if (!allSensingDone) {
          switch (currentSensing) {
              case HEART:
                  Heart_Sensor();
                  break;
              case ALCOHOL:
                  Alcol_Sensor();
                  break;
              case VOICE:
                  Voice_Sensor();
                  break;
          }
      }

    if (allSensingDone) {
      Serial.println("sensing done");  // 타임아웃 알림 
      break;         // 상태 변경
    }
    delay(300);  // 너무 빠른 반복 방지
  }
  StartTime = 0;

  // 4. finalGiven이 존재할 경우 조건 체크 및 메시지 전송
  if (finalGiven.length() > 0) {
    if (sensorData && finalGiven == "True") {
      Serial.println("motor on");

    //   Serial.println("Vehicle Turn ON        ");
    //   Sound_Do6(0.5);

      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW); // 앞으로 계속 회전

      delay(1000);

    //   Serial.println("Vehicle Turn OFF        ");
    //   Sound_Do6(0.5);

      digitalWrite(in1, LOW);
      digitalWrite(in2, LOW); // 회전 정지

      delay(1000);

    } else {
      Serial.println("do not drive");
    }
    // finalGiven = "";  // 처리 후 초기화
  }
  if(given == "True"){
    Serial.println("looks like Nobody here");
  }
  
  delay(500);  // 루프 주기 조절
}

//AlcolSensor ------------------------------------------------------------


void Alcol_Sensor() {
    unsigned long alcolTime = millis(); // 현재 시간

    if (alcolTime - StartTime < sensingTime) {
        int alcol_val = analogRead(mq3Pin);

        dataSum += alcol_val;
        dataCount++;

        Serial.print("Alcol Value: ");
        Serial.println(alcol_val);
    } else {
        // 센싱 종료 후 평균값 계산
        averageValue = (int)dataSum / dataCount;
        Serial.print("Alcol Average: ");
        Serial.println(averageValue);

        if (averageValue >= alcol_sensor_val) {
            Serial.println("Alcol Warning!");
        } else {
            Serial.println("Alcol Normal");
        }

        // 다음 센서로 전환
        resetSensing(VOICE);
    }
}

// Heart_Sensor --------------------------------------------------------
// 심박수 측정 센서

void Heart_Sensor() {
    unsigned long heartMillis = millis(); // 현재 시간 계산

    // 1. 센싱 로직 실행
    if (heartMillis - StartTime < sensingTime) {
        // 데이터 수집
        int Signal = analogRead(PulseSensorPurplePin);
        dataSum += Signal;
        dataCount++;

        // 데이터 출력
        Serial.print("Heart Signal: ");
        Serial.println(Signal);
        Serial.println(heartMillis - StartTime);
    } else {
        // 2. 센싱 종료 후 평균 계산
        averageValue = (int)dataSum / dataCount;
        Serial.print("Heart Sensor Average: ");
        Serial.println(averageValue);

        if (averageValue < Threshold) {
            Serial.println("Heart Sensor Warning!");
            // 경고음을 출력하거나 특정 동작 실행 가능
        } else {
            Serial.println("Heart Sensor Normal");
        }

        // 3. 센싱 데이터 초기화 및 알코올 센서로 전환
        resetSensing(ALCOHOL);
    }
}

//Voice_Sensor-------------------------------------------------------

void Voice_Sensor() {
    unsigned long voiceMillis = millis(); // 현재 시간 계산

    // 1. 센싱 시간이 종료되었는지 확인
    if (voiceMillis - StartTime >= sensingTime) {
        Serial.println("Voice Sensor sensing time ended.");
        resetSensing(HEART);
        allSensingDone = true;
        return;
    }

    // 2. 센싱 데이터 처리
    if (voiceSerial.available() > 1) {
        char id = voiceSerial.read();
        char acc = voiceSerial.read();

        Serial.print("Channel: ");
        Serial.println((char)id);
        Serial.print("Accuracy: ");
        Serial.println(acc, DEC);

        switch (id) {
            case '0':
                if (acc > 40) {
                    Serial.println("Voice Command Accepted: Action Triggered");
                } else {
                    Serial.println("Voice Command Rejected: Low Accuracy");
                }
                break;

            default:
                Serial.println("Unknown Command");
                break;
        }
    }
}


// 상태 초기화 및 전환
void resetSensing(Sensor nextState) {
    dataSum = 0;
    dataCount = 0;
    averageValue = 0;
    StartTime = millis();
    currentSensing = nextState;
    Serial.print("State Changed to: ");
    Serial.println(currentSensing);  // 상태 확인
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