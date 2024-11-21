import serial
import time
import threading
import configuration as con

class ArduinoCommunicator(threading.Thread):
    def __init__(self, port, baud_rate, send_interval=2):
        """
        Arduino와 통신하기 위한 클래스 초기화
        """
        super(ArduinoCommunicator, self).__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.send_interval = send_interval
        self.oper_state = 0  # 기본 상태 (0 또는 1)
        self.final_pass = False  # 최종 전송할 값
        self.pending_final_pass = None  # 요청된 final_pass 값 (활성화 대기 중)
        self.final_pass_active = False  # FINAL 값 전송 활성화 플래그
        self.last_sent_time = time.time()
        self.ser = None

        # 시리얼 포트 연결
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Connected to Arduino on {self.port}")
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            exit()

    def request_final_pass(self, final_value):
        """
        final_pass 변경 요청 (활성화 대기 상태로 저장)
        """
        self.pending_final_pass = f"FINAL_{final_value}"
        print(f"Requested final_pass change to: {self.pending_final_pass} (awaiting activation)")

    def send_data(self):
        """
        데이터를 아두이노로 전송
        """
        current_time = time.time()
        if current_time - self.last_sent_time >= self.send_interval:
            if self.final_pass_active and self.final_pass:
                self.ser.write(f"{self.final_pass}\n".encode())  # FINAL 값 전송
                print(f"Sent: {self.final_pass}")
            else:
                self.ser.write(f"{self.oper_state}\n".encode())  # 기본 상태 전송
                print(f"Sent: {self.oper_state}")
            self.last_sent_time = current_time

    def receive_data(self):
        """
        아두이노로부터 데이터를 수신
        """
        if self.ser.in_waiting > 0:
            response = self.ser.readline().decode().strip()
            print(f"Received: {response}")

            # 아두이노에서 'sensing done' 메시지 수신 시 final_pass 활성화
            if response == "sensing done" and self.pending_final_pass:
                self.final_pass = self.pending_final_pass
                self.final_pass_active = True
                self.pending_final_pass = None  # 대기 중 값을 초기화
                print(f"Activated final_pass: {self.final_pass}")

    def run(self):
        """
        메인 루프: 데이터 송수신
        """
        try:
            while True:
                self.send_data()
                self.receive_data()
                time.sleep(0.1)  # 루프 속도 조절
        except KeyboardInterrupt:
            print("\nExiting...")
            self.close_connection()

    def close_connection(self):
        """
        시리얼 포트 연결 종료
        """
        if self.ser:
            self.ser.close()
            print("Serial connection closed.")
    
    def stop(self):
        self.ser.close()
        print("disconnection arduino pass")


# 설정에 따른 실행
if __name__ == "__main__":
    try:
        arduino_port = con.ser_setting["Mac"]
        baud_rate = 9600

        communicator = ArduinoCommunicator(port=arduino_port, baud_rate=baud_rate)
        communicator.start()

        # 실행 코드에서 final_pass를 요청
        # communicator.oper_state = 1
        communicator.request_final_pass(0) #("FINAL_1")

        # 메인 루프 실행
        communicator.run()
    finally:
        communicator.stop()
        communicator.join()
