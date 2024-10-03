int PulseSensorPurplePin = A0; // A0에 심박 센서를 할당
int LED13 = 13;
int Signal;
int Threshold = 550;

void setup() {
  // put your setup code here, to run once:
  pinMode(LED13, OUTPUT);
  Serial.begin(9600);

}

void loop() {
  Heart_Sensor();
}

void Heart_Sensor() {
  Signal = analogRead(PulseSensorPurplePin);
  Serial.println(Signal); // 현재 심박수를 출력합니다.

  if (Signal > Threshold) {
    digitalWrite(LED13, HIGH); // LED 가동
  }

  else {
    digitalWrite(LED13, LOW); // LED 꺼짐
  }
  delay(100); // 0.1초마다 체크
}