import serial
import time
import configuration as con

arduino_port = con.ser_setting["voice4"]  # Windows 예시
baud_rate = 9600

oper_state = 1  # 0 또는 1
final_pass = None
final_pass_active = False  # FINAL 값 전송 활성화 플래그

SEND_INTERVAL = 2
last_sent_time = time.time()

# 시리얼 포트 연결
try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
except serial.SerialException as e:
    print(f"Failed to connect: {e}")
    exit()

def communicate_with_arduino():
    global oper_state, final_pass, last_sent_time, final_pass_active
    while True:
        current_time = time.time()

        # 데이터 송신
        if current_time - last_sent_time >= SEND_INTERVAL:
            if final_pass_active and final_pass:
                ser.write(f"{final_pass}\n".encode())  # FINAL_0 또는 FINAL_1 전송
                print(f"Sent: {final_pass}")
            else:
                ser.write(f"{oper_state}\n".encode())  # 0 또는 1 전송
                print(f"Sent: {oper_state}")
            last_sent_time = current_time

        # 데이터 수신
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            print(f"Received: {response}")
            if response == "sensing done":
                final_pass = "FINAL_1"  # 이 값은 상황에 맞게 설정
                final_pass_active = True  # FINAL 전송 활성화

        time.sleep(0.1)  # 루프 속도 조절

# 메인 실행
try:
    communicate_with_arduino()
except KeyboardInterrupt:
    print("\nExiting...")
    ser.close()
