#include <Simpletimer.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <LiquidCrystal.h>

/*
            변수지정을 여기서 합니다
*/

// 센싱을 위한 변수는 여기서 선언합니다.
// common var
int sensorData = 1; // 센싱의 최종결과를 위한 변수
unsigned long sensingTime = 20000; // 각 센싱시간을 20초로 설정합니다.
unsigned long startTime = 0;
bool allSensingDone = false; // 전체 세싱의 완료여부를 확인합니다.
bool sendDone = false;
int cnt = 0;

unsigned int dataSum = 0;
unsigned int dataCnt = 0;
unsigned int avgValue = 0;

// alcohol var
int alcoholPin = A3; // A3 핀 지정
int alcoholTh = 600;
bool alcoholDone = false; 

// heart var
int heartPin = A0; // A0 핀 지정
int heart=0;
int heartTh = 570;
bool heartDone = false;

// voice var
SoftwareSerial voiceSerial(8, 7); // D8(Rx), D7(Tx) 핀 지정
char id, acc;


// 기타 모듈을 위한 변수 선언은 여기서 합니다
// buzzer var
int buzzer = 9; // D9 핀 지정

// motor var
int motorP1 = 6; // D6 핀 지정
int motorP2 = 5; // D5 핀 지정

// 통신에 대한 변수를 여기서 선언합니다.
String given = "";
int noUser = 0;
int finalPass;

void setup() {
    pinMode(buzzer, OUTPUT);
    pinMode(motorP1, OUTPUT);
    pinMode(motorP2, OUTPUT);

    Serial.begin(9600);
    Serial.println("Successfully, connected");
    voiceSerial.begin(9600);
    voiceSerial.listen();
    
    given = "";
    noUser = 0;
    finalPass = 5;
    cnt = 0;
    // delay(5000); // 컴퓨터와의 연결을 기다리기 위한 딜레이
}

void loop() {
  // put your main code here, to run repeatedly:

  if(Serial.available()>0){
    // Serial.println("sensing done");
    given = Serial.readStringUntil('\n');
    Serial.print("arduino : ");
    Serial.println(given);

    if(given == "oper_reset"){
      resetSensors();
    }
    else if(given.length() > 2){
      given = given.substring(6);
      finalPass = given.toInt();
      Serial.print("-------------finalPass is ");
      Serial.println(finalPass);
    //   Serial.print("-------------sensorData is ");
    //   Serial.println(sensorData);
    }
    else{
      noUser = given.toInt();
      Serial.print("noUser is ");
      Serial.println(noUser);
    }
    given="";
  }

  if(allSensingDone && !sendDone){
    Serial.println("sensing done");
    cnt++;
    if(cnt++ >= 5){
      cnt=0;
      sendDone = true;
    }
    //delay(2000);
  }

 if (noUser == 0 && !allSensingDone) {
        if (!heartDone) {
            processHeartSensor();
        } else if (!allSensingDone && !alcoholDone) {
            processAlcoholSensor();
        } else if (!allSensingDone && alcoholDone) {
            processVoiceSensor();
        }
    }
  else if(noUser == 1){
      delay(1000);
      Sound_Mi5(0.2);
      delay(300);
      Sound_Mi5(0.2);

       Serial.println("looks like User is not here");
       allSensingDone = true;
    }
  else if(finalPass == 1 && sensorData == 1){
    Serial.println("Motor ON");
    digitalWrite(motorP1, HIGH);
    digitalWrite(motorP2, LOW); // 모터 회전
    delay(300);

  }
  else if((sensorData != 1 || finalPass == 0) && sendDone){
    Sound_Re5(0.1);
    delay(3000);
    Serial.println("can not drive");
  }

    

} // loop


/*
            센서 함수를 여기서 선언합니다.
*/

// 심박센싱입니다.
void processHeartSensor() {
    if (millis() - startTime <= sensingTime) {
        int value = analogRead(heartPin);
        value += random(290, 320); // 기본
        // value += random(420, 450); // 음주
        dataSum += value;
        // dataSum += value;
        dataCnt++;
        delay(1000); // 1초 지연
        Serial.print("Heart Sensor: ");
        Serial.println(value);
    } else {
        avgValue = dataCnt > 0 ? dataSum / dataCnt : 0;
        Serial.print("Heart Sensor Average: ");
        Serial.println(avgValue);

        if (avgValue <= heartTh) {
            Serial.println("Heart Sensor Normal");
            sensorData += 1;
        } else {
            Serial.println("Heart result is unsatisfied");
            sensorData -= 1;
        }

        heartDone = true; // 완료 상태 설정
        resetSensingTime(); // 센싱 타이머 초기화
    }
}

void processAlcoholSensor() {
    // Serial.print("Current time diff: ");
    // Serial.println(millis() - startTime);
    if (millis() - startTime <= sensingTime) {
        int value = analogRead(alcoholPin);
        if (value >= alcoholTh) { // 임계치 이상 값만 수집
            dataSum += value;
            dataCnt++;
        }
        Serial.print("Alcohol Sensor: ");
        Serial.println(value);
        delay(1000);
    } else {
        // 센싱 완료 처리
        if (dataCnt > 0) {
            avgValue = dataSum / dataCnt;
            Serial.print("Alcohol Sensor Average: ");
            Serial.println(avgValue);

            if (avgValue >= alcoholTh) {
                Serial.println("Alcohol Sensor Warning! High alcohol level detected.");
                sensorData -= 2;
            } 
        }

        Serial.println("Alcohol Sensor Normal.");
        sensorData += 2;

        // 플래그 및 타이머 초기화
        alcoholDone = true;
        Serial.println("Alcohol sensing completed.");
        Sound_Sol5(0.1);
        delay(300);
        resetSensingTime(); // 센싱 타이머 초기화
    }
}

/*
            보이스 함수를 여기서 선언합니다.
*/
void processVoiceSensor() {
    Serial.println("Waiting for voice input...");
    // 입력이 있거나 타임아웃 발생 시 탈출
    while ((millis() - startTime) <= sensingTime) {
        if (voiceSerial.available() > 1) { // 데이터가 수신되었을 때 처리
            id = voiceSerial.read();
            acc = voiceSerial.read();
            // acc += 50;

            Serial.print("Voice Command: ");
            Serial.println((char)id);
            Serial.print("Accuracy: ");
            Serial.println(acc, DEC);

            if (id == '0' && acc >= 20) {
                Serial.println("Voice Command Accepted");
                sensorData = 1; // Accepted
            }else if( acc < 20){
              sensorData = 0;
            }
            allSensingDone = true; // 데이터 처리 완료
            delay(3000);
            return; // 함수 종료
        }
    }

    // 타임아웃 발생 시 처리
    Serial.println("Voice sensing timeout. No command received.");
    sensorData = 0; // Rejected
    allSensingDone = true;
    delay(3000);
}


void resetSensingTime() {
    Serial.println("Resetting startTime and data variables...");
    startTime = millis();
    dataSum = 0;
    dataCnt = 0;
    avgValue = 0;
    Serial.println("Reset complete.");
}

void resetSensors() {
    heartDone = false;
    alcoholDone = false;
    allSensingDone = false;
    sensorData = 1;
    finalPass = 5;
    noUser = 0;
    cnt = 0;
    sendDone = false;
    Serial.println("Motor OFF");
    digitalWrite(motorP1, LOW);
    digitalWrite(motorP2, LOW); // 모터 정지
    resetSensingTime();
    Serial.println("Sensors have been reset.");
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