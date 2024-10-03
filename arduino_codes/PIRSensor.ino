int LED = 8; // LED를 D8에 초기화
int PIR = 7; // 센서 변수를 D7에 초기화
int state = 0; // 센서 상태값 저장 변수 (0:Low,1:High)

void setup() {
  pinMode(LED,OUTPUT); //LED를 출력으로 설정
  pinMode(PIR,INPUT); //센서를 입력으로 설정
  Serial.begin(9600); //시리얼 통신, 속도는 9600
}

void loop() {
  PIR_Sensor();
}

void PIR_Sensor()
{
  state = digitalRead(PIR); // PIR 센서값 입력 받음

  digitalWrite(LED,LOW); // 초기 LED값을 OFF로 설정

  if(state==0){ // 센서 값이 0일 경우
    Serial.println("ON"); // 시리얼 통신에 센서값 출력
    digitalWrite(LED,HIGH); //LED ON
  }
  else { // 센서 값이 1일 경우
    Serial.println("OFF"); // 시리얼 통신에 센서값 출력
    digitalWrite(LED,LOW); //LED OFF
  }

  delay(100); // 0.1초 대기
}
