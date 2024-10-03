#include <Wire.h> // i2C 통신을 위한 라이브러리
#include <LiquidCrystal_I2C.h> // LCD 2004 I2C용 라이브러리
LiquidCrystal_I2C lcd(0x27,20,4); // 접근주소 : 0x3F or 0x27

void setup() {
  // put your setup code here, to run once:
  lcd.init(); // LCD 초기화
  lcd.backlight(); // 백라이트 켜기

  lcd.setCursor(0,0); // 1번째 줄 문자열 출력
  lcd.print("Hello, world! 1");

  lcd.setCursor(0,1); // 2번째 줄 문자열 출력
  lcd.print("Hello, world! 2");

  lcd.setCursor(0,2); // 3번째 줄 문자열 출력
  lcd.print("Hello, world! 3");

  lcd.setCursor(0,3); // 4번째 줄 문자열 출력
  lcd.print("Hello, world! 4");

}

void loop() {
  // put your main code here, to run repeatedly:
  for(int i=0;i<4;i++){ // 오른쪽으로 4칸 움직이기
    lcd.scrollDisplayRight();
    delay(500);
  }
  for(int j=0;j<4;j++){ // 왼쪽으로 4칸 움직이기
    lcd.scrollDisplayLeft(); 
    delay(500);
  }

}
