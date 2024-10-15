int in1 = 7, in2 =5;

void setup(){
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
}

void loop(){
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  delay(2000);
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  delay(200);
}