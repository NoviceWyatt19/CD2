import cv2
import threading
import time
import queue
import serial
import configuration as con
from user_recog import recognize_user_from_frame
from gaze_classifier import detect_drowsy_with_gaze

import sys
sys.path.append("/Users/wyatt/Desktop/CD2_project")

# 비디오 캡처 스레드
class VideoCaptureThread(threading.Thread):
    def __init__(self, frame_queue, max_queue_size=10):
        super(VideoCaptureThread, self).__init__()
        self.cap = cv2.VideoCapture(0)
        self.frame_queue = frame_queue
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                self.running = False
                break

            # 큐에 프레임 저장 (버퍼링)
            if not self.frame_queue.full():
                self.frame_queue.put(frame)

            time.sleep(0.1)  # 약간의 대기 (33ms, 30fps 기준)

    def stop(self):
        self.running = False
        self.cap.release()

# 유저 인식 스레드
class UserRecognitionThread(threading.Thread):
    def __init__(self, frame_queue):
        super(UserRecognitionThread, self).__init__()
        self.frame_queue = frame_queue
        self.user_status = "No face detected"
        self.running = True

    def run(self):
        while self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                self.user_status = recognize_user_from_frame(frame)
            time.sleep(0.5) 

    def stop(self):
        self.running = False

# 졸음 판단 스레드
class DrowsinessDetectionThread(threading.Thread):
    def __init__(self, frame_queue):
        super(DrowsinessDetectionThread, self).__init__()
        self.frame_queue = frame_queue
        self.drowsiness_status = "Unknown"
        self.ear = 0.0
        self.running = True
        self.processed_frame = None

    def run(self):
        while self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                try:
                    (
                        self.processed_frame,
                        self.drowsiness_status,
                        self.ear,
                        _,
                        _,
                        _,
                        _,
                    ) = detect_drowsy_with_gaze(frame)
                except Exception as e:
                    print(f"Drowsiness detection error: {e}")
            time.sleep(0.05)

    def stop(self):
        self.running = False


# class ArduinoCommunicator(threading.Thread):
#     def __init__(self, port, baud_rate, send_interval=2):
#         super(ArduinoCommunicator, self).__init__()  # threading.Thread 초기화
#         self.port = port
#         self.baud_rate = baud_rate
#         self.send_interval = send_interval

#         # 상태 변수 초기화
#         self._oper_state = 0  # 내부 변수
#         self._final_pass = 0  # 0 또는 1 값만 허용
#         self.final_pass_active = False
#         self.running = False
#         self.last_sent_time = 0

#         # 시리얼 포트 연결
#         try:
#             self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
#             print(f"Connected to Arduino on {self.port}")
#         except serial.SerialException as e:
#             print(f"Failed to connect: {e}")
#             exit()

#     # Getter 및 Setter 메서드
#     def get_oper_state(self):
#         return self._oper_state

#     def set_oper_state(self, value):
#         if value in (0, 1):  # 값 검증
#             self._oper_state = value
#             print(f"oper_state updated to: {self._oper_state}")
#         else:
#             raise ValueError("oper_state must be 0 or 1.")

#     def get_final_pass(self):
#         return self._final_pass

#     def set_final_pass(self, value):
#         if value in (0, 1):  # 0 또는 1 값만 허용
#             self._final_pass = value
#             # self.final_pass_active = True  # 전송 활성화
#             print(f"final_pass updated to: {self._final_pass}")
#         else:
#             raise ValueError("final_pass must be 0 or 1.")

#     def send_data(self):
#         """아두이노로 데이터를 송신."""
#         current_time = time.time()
#         if current_time - self.send_interval >= self.last_sent_time:
#             if self.final_pass_active:  # final_pass 전송
#                 send_final_pass:str = f"FINAL_{self._final_pass}"
#                 self.ser.write(f"{send_final_pass} \n".encode())
#                 print(f"Sent: {send_final_pass}")
#                 # self.final_pass_active = False  # 전송 후 비활성화
#             else:  # oper_state 전송
#                 self.ser.write(f"{self._oper_state}\n".encode())
#                 print(f"Sent: {self._oper_state} \n")

#             self.last_sent_time = current_time


#     def receive_data(self):
#         """아두이노로부터 데이터를 수신."""
#         if self.ser.in_waiting > 0:
#             response = self.ser.readline().decode().strip()
#             print(f"Received: {response}")
#             if response == "sensing done":
#                 if self._final_pass is not None:
#                     self.final_pass_active = True
#                     print("sensing done received. Ready to send final_pass.")

#     def run(self):
#         """스레드 실행 루프."""
#         self.running = True
#         while self.running:
#             self.send_data()
#             self.receive_data()
#             time.sleep(0.3)  # 루프 속도 조절

#     def stop(self):
#         self.running = False
#         self.ser.close()

class ArduinoCommunicator(threading.Thread):
    def __init__(self, port, baud_rate, send_interval=1.5):
        """
        Arduino와 통신하기 위한 클래스 초기화
        """
        super(ArduinoCommunicator, self).__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.send_interval = send_interval
        self.oper_state = 0  # 기본 상태 (0 또는 1)
        self.final_pass = 0  # 최종 전송할 값
        self.pending_final_pass = None  # 요청된 final_pass 값 (활성화 대기 중)
        self.final_pass_active = False  # FINAL 값 전송 활성화 플래그
        self.last_sent_time = time.time()
        self.reset_active = True
        self.ser = None

        # 시리얼 포트 연결
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Connected to Arduino on {self.port}")
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            exit()

    # def request_final_pass(self, final_value):
    #     self.pending_final_pass = f"FINAL_{final_value}"
    #     print(f"Requested final_pass change to: {self.pending_final_pass} (awaiting activation)")

    def send_data(self):
        """
        데이터를 아두이노로 전송
        """
        current_time = time.time()
        if current_time - self.last_sent_time >= self.send_interval:
            if self.final_pass_active:
                self.ser.write(f"FINAL_{self.final_pass}\n".encode())  # FINAL 값 전송
                print(f"Sent: FINAL_{self.final_pass}")
            elif self.reset_active:
                for _ in range(3):
                    self.ser.write("oper_reset\n".encode())  # 초기화 명령문 전송
                    time.sleep(0.02)
                self.reset_active = False
            elif not self.reset_active:
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
            if response == "sensing done": # and self.pending_final_pass
                # self.final_pass = self.pending_final_pass
                self.final_pass_active = True
                # self.pending_final_pass = None  # 대기 중 값을 초기화
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

# 메인 프로세싱
def main():
    frame_queue = queue.Queue(maxsize=20)

    # 스레드 생성
    video_thread = VideoCaptureThread(frame_queue)
    user_thread = UserRecognitionThread(frame_queue)
    drowsiness_thread = DrowsinessDetectionThread(frame_queue)
    arduino_thread = ArduinoCommunicator(port=con.ser_setting["voice4"], baud_rate=9600)

    # 스레드 시작
    video_thread.start()
    user_thread.start()
    drowsiness_thread.start()
    arduino_thread.start()

    # 상태 변수
    oper_state = False
    final_pass = None

    # 점수 변수 초기화
    user_recognition_score = 0
    drowsiness_score = 0

    # 상태 지속 시간 추적 변수
    user_status_frame_count = {"No face detected": 0, "User not recognized": 0, "User recognized": 0}
    drowsiness_status_frame_count = {"Drowsy": 0, "Little Drowsy": 0, "Awake": 0}

    # 점수 업데이트 주기 (프레임 단위)
    update_frequency = 30

    # 점수 임계값
    user_threshold = 20
    drowsiness_threshold = 30

    try:

        while True:
            if drowsiness_thread.processed_frame is not None:
                frame = drowsiness_thread.processed_frame.copy()

                # 유저 상태 업데이트 로직
                current_user_status = user_thread.user_status
                for status in user_status_frame_count:
                    if status == current_user_status:
                        user_status_frame_count[status] += 1
                    else:
                        user_status_frame_count[status] = 0

                if user_status_frame_count["No face detected"] >= update_frequency:
                    user_recognition_score += 1
                    user_status_frame_count["No face detected"] = 0  
                elif user_status_frame_count["User not recognized"] >= update_frequency:
                    user_recognition_score += 2
                    user_status_frame_count["User not recognized"] = 0

                # 졸음 상태 업데이트 로직
                current_drowsiness_status = drowsiness_thread.drowsiness_status
                for status in drowsiness_status_frame_count:
                    if status == current_drowsiness_status:
                        drowsiness_status_frame_count[status] += 1
                    else:
                        drowsiness_status_frame_count[status] = 0

                if drowsiness_status_frame_count["Drowsy"] >= update_frequency:
                    drowsiness_score += 2
                    drowsiness_status_frame_count["Drowsy"] = 0
                elif drowsiness_status_frame_count["Little Drowsy"] >= update_frequency:
                    drowsiness_score += 1
                    drowsiness_status_frame_count["Little Drowsy"] = 0
                
                # 유저 상태 업데이트
                if user_recognition_score > user_threshold:
                    arduino_thread.oper_state = 1
                    arduino_thread.final_pass = 0

                if drowsiness_score > drowsiness_threshold:
                    arduino_thread.final_pass = 0
                else:
                    arduino_thread.final_pass = 1
                
                 # 프레임에 상태 및 점수 출력
                cv2.putText(frame, f"User: {user_thread.user_status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                cv2.putText(frame, f"Drowsiness: {drowsiness_thread.drowsiness_status}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"EAR: {drowsiness_thread.ear:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # 왼쪽 하단에 점수 출력
                height, width, _ = frame.shape
                cv2.putText(frame, f"User Score: {int(user_recognition_score)}", (10, height - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.putText(frame, f"Drowsy Score: {int(drowsiness_score)}", (10, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                # 처리된 프레임 디스플레이
                cv2.imshow("Drowsiness Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        video_thread.stop()
        user_thread.stop()
        drowsiness_thread.stop()
        arduino_thread.stop()

        video_thread.join()
        user_thread.join()
        drowsiness_thread.join()
        arduino_thread.join()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()