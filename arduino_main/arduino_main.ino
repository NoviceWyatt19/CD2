#include <Simpletimer.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <LiquidCrystal.h>

/*
            변수지정을 여기서 합니다
*/

// 센싱을 위한 변수는 여기서 선언합니다.
// common var
int sensorDate = 1; // 센싱의 최종결과를 위한 변수
unsigned long sensingTime = 20000; // 각 센싱시간을 20초로 설정합니다.
unsigned long startTime = 0;
bool allSensingDone = false; // 전체 세싱의 완료여부를 확인합니다.

unsigned int dataSum = 0;
unsigned int dataCnt = 0;
unsigned int avgValue = 0;

// alcohol var
int alcoholPin = A3; // A3 핀 지정
int alcoholTh = 600;

// heart var
int heartPin = A0; // A0 핀 지정
int heart=0;
int heartTh = 570;

// voice var
SoftwareSerial voiceSerial(8, 7); // D8(Rx), D7(Tx) 핀 지정
char id, acc;

// switch
enum State{
    HEART, // 0
    ALCOHOL, // 1
    VOICE // 2
};
State currentState = HEART;

// 기타 모듈을 위한 변수 선언은 여기서 합니다
// buzzer var
int buzzer = 9; // D9 핀 지정

// motor var
int motorP1 = 6; // D6 핀 지정
int motorP2 = 5; // D5 핀 지정

// 통신에 대한 변수를 여기서 선언합니다.
String given = "";
int noUser = 0;
int finalPass = 1;


/*
            시리얼 연결 및 변수 초기화를 여기서 합니다
*/
void setup() {
    pinMode(buzzer, OUTPUT);
    pinMode(motorP1, OUTPUT);
    pinMode(motorP2, OUTPUT);

    Serial.begin(9600);
    voiceSerial.begin(9600);
    voiceSerial.listen();
}

/*
            메인루프는 여기입니다.
*/
void loop(){
    /*
                파이썬으로부터 noUser와 finalPass에 대한 정보를 받아옵니다
    */
   if (Serial.available() > 0){
        given = Serial.readStringUntil('\n');
        given.trim();

        if (given.length() > 6){
            finalPass = given.substring(6).toInt();
            Serial.print("---------- given final state : ");
            Serial.println(finalPass);
        }else{
            noUser = given.toInt();
            Serial.print("given User state : ");
            Serial.println(noUser);
        }

        given = "";
   }

    /*
                여기는 noUser가 0일때 진행하는 while문 입니다
    */
    startTime = millis();
    while( noUser == 0 ){

        if(allSensingDone){
            Serial.println("sensing done");
            break;
        }

        switch (currentState) {
            case HEART:
                processSensor(HEART);
                break;
            case ALCOHOL:
                processSensor(ALCOHOL);
                break;
            case VOICE:
                Voice_sensor();
                break;
        }
    }
    startTime = 0;

    /*
                여기서 최종결과 또는 도중중지에 대한 결과를 설정합니다.
    */
   if(finalPass > 0){
      if (allSensingDone && sensorDate > 0 && finalPass > 0) {
        Serial.println("Motor ON");
        digitalWrite(motorP1, HIGH);
        digitalWrite(motorP2, LOW); // 모터 회전
      } else {
        Serial.println("Motor OFF");
        digitalWrite(motorP1, LOW);
        digitalWrite(motorP2, LOW); // 모터 정지
      }
    }else {
      Serial.println("do not drive");
    }
    if(given == "True"){
       Serial.println("looks like Nobody here");
    }
    
    delay(500);  // 루프 주기 조절
}


/*
            센서 함수를 여기서 선언합니다.
*/
void processSensor(State sensorType) {

    if (millis() - startTime <= sensingTime) {
        int value = 0;
        if (sensorType == HEART) value = analogRead(heartPin);
        if (sensorType == ALCOHOL) value = analogRead(alcoholPin);
        
        dataSum += value;
        dataCnt++;
        Serial.print(sensorType);
        Serial.println(" : sensing");
    } else {
        avgValue = dataSum / dataCnt;
        Serial.print("Sensor Average: ");
        Serial.println(avgValue);

        if ((sensorType == HEART && avgValue < heartTh) ||
            (sensorType == ALCOHOL && avgValue >= alcoholTh)) {
            Serial.println("Warning! Sensor threshold exceeded.");
            sensorDate -= 1;
        } else {
            Serial.println("Sensor normal.");
            sensorDate += 1;
        }

        // Reset for next state
        resetSensing(sensorType == HEART ? ALCOHOL : VOICE);
    }
}

void resetSensing(State nextState) {
    dataSum = 0;
    dataCnt = 0;
    avgValue = 0;
    startTime = millis();
    currentState = nextState;

    if (nextState == VOICE) {
        allSensingDone = true;
    }

    Serial.print("State Changed to: ");
    Serial.println(nextState);
}

/*
            보이스 함수를 여기서 선언합니다.
*/
void Voice_sensor() {
    if (millis() - startTime <= sensingTime) {
        if (voiceSerial.available() > 1) {
            id = voiceSerial.read();
            acc = voiceSerial.read();

            Serial.print("Voice Command: ");
            Serial.println((char)id);
            Serial.print("Accuracy: ");
            Serial.println(acc, DEC);

            if (id == '0' && acc > 40) {
                Serial.println("Voice Command Accepted");
                sensorDate = 1;
            } else {
                Serial.println("Voice Command Rejected");
                sensorDate = 0;
            }
        }else{
            Serial.println("No voice command received.");
            sensorDate = 0;
        }
    } else {
        allSensingDone = true;
        Serial.println("Voice sensing complete.");
    }
}


/*
            부저 함수를 여기서 선언합니다.
*/

void Sound_Do5(double sec){
  tone(buzzer, 523); // 5옥타브 도
  delay(1000 * sec);
  noTone(buzzer);
}

void Sound_Re5(double sec){
  tone(buzzer, 587); // 레
  delay(1000 * sec);
  noTone(buzzer);
}

void Sound_Mi5(double sec){
  tone(buzzer, 659); // 미
  delay(1000 * sec);
  noTone(buzzer);
}

void Sound_Pa5(double sec){
  tone(buzzer, 698); // 파
  delay(1000 * sec);
  noTone(buzzer);
}

void Sound_Sol5(double sec){
  tone(buzzer, 784); // 솔
  delay(1000 * sec);
  noTone(buzzer);
}

void Sound_La5(double sec){
  tone(buzzer, 880); // 라
  delay(1000 * sec);
  noTone(buzzer);
}

void Sound_Shi5(double sec){
  tone(buzzer, 988); // 시
  delay(1000 * sec);
  noTone(buzzer);
}

void Sound_Do6(double sec){
  tone(buzzer, 1046); // 6옥타브 도
  delay(1000 * sec);
  noTone(buzzer);
}