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
        if not self.cap.isOpened():
            print("Cannot open camera")
            self.running = False
            return
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                self.running = False
                break

            # 큐에 프레임 저장 (버퍼링)
            if not self.frame_queue.full():
                self.frame_queue.put(frame)

            time.sleep(0.03)  # 약간의 대기 (33ms, 30fps 기준)

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
            time.sleep(0.03) 

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
            time.sleep(0.03)

    def stop(self):
        self.running = False

# 아두이노 통신 스레드
class ArduinoCommunicationThread(threading.Thread):
    def __init__(self, port):
        super(ArduinoCommunicationThread, self).__init__()
        self.port = port
        self.running = True
        self.connection = None
        self.oper_state = "False"  # 기본값 초기화
        self.final_pass = True     # 기본값 초기화
        self.sensing_data_store = {"a": "000", "h": "000", "v": "000"}  # 초기 센싱 데이터
        self.lock = threading.Lock()  # 데이터 보호용

    def run(self):
        try:
            self.connection = serial.Serial(self.port, 9600, timeout=1)
            print(f"Connected to Arduino on {self.port}")
        except Exception as e:
            print(f"Failed to connect to Arduino: {e}")
            self.running = False
            return
        
        delay_interval = 1.5  # 데이터 전송 주기

        while self.running:
            try:
                 # Arduino로 데이터 전송
                if self.oper_state is not None:  # oper_state가 None이 아닌 경우만 전송
                    self.connection.write((str(self.oper_state) + '\n').encode())
                    self.connection.flush()  # 전송 강제
                    print(f"Sent to Arduino: {self.oper_state}")
                    
                # Arduino로부터 데이터 수신
                if self.connection.in_waiting > 0:
                    message = self.connection.readline().decode(errors="ignore").strip()
                    print(f"Received from Arduino: {message}")

                    # 센싱 데이터 파싱
                    if message.startswith("sensing data"):
                        self.parse_sensing_data(message)
                # 딜레이 추가
                time.sleep(delay_interval)

            except Exception as e:
                print(f"Arduino communication error: {e}")

    def parse_sensing_data(self, message):
        # 센싱 데이터를 파싱하여 저장
        try:
            parts = message.split("_")[1].split(",")
            sensing_data = {
                "a": parts[0].split(":")[1],
                "h": parts[1].split(":")[1],
                "v": parts[2].split(":")[1],
            }
            with self.lock:
                self.sensing_data = sensing_data
        except Exception as e:
            print(f"Failed to parse sensing data: {e}")

    def get_sensing_data(self):
        # 현재 센싱 데이터를 안전하게 반환
        with self.lock:
            return self.sensing_data.copy()  # 딕셔너리의 copy() 메서드 호출


    def update_state(self, oper_state, final_pass):
        # 스레드 안전하게 상태 업데이트
        with self.lock:
            self.oper_state = oper_state
            self.final_pass = final_pass

    def stop(self):
        self.running = False
        if self.connection and self.connection.is_open:
            self.connection.close()

# 메인 프로세싱
def main():
    frame_queue = queue.Queue(maxsize=10)

    # 스레드 생성
    video_thread = VideoCaptureThread(frame_queue)
    user_thread = UserRecognitionThread(frame_queue)
    drowsiness_thread = DrowsinessDetectionThread(frame_queue)
    arduino_thread = ArduinoCommunicationThread(port=con.ser_setting["Mac"])
    

    # 스레드 시작
    video_thread.start()
    user_thread.start()
    drowsiness_thread.start()
    arduino_thread.start()

    # 상태 변수
    oper_state = False
    final_pass = True

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

    # 추가 변수
    h_adjusted_value = None  # `s`를 눌렀을 때 계산된 값 저장

    try:
        while True:
            if drowsiness_thread.processed_frame is not None:
                frame = drowsiness_thread.processed_frame.copy()
                
                # 프레임 크기 초기화
                height, width, _ = frame.shape
                
                # 센싱 데이터 가져오기
                sensing_data = arduino_thread.get_sensing_data()
                try:
                    a_value = sensing_data['a']
                    h_value = sensing_data['h']
                    v_value = sensing_data['v']
                except KeyError:
                    a_value, h_value, v_value = "N/A", "N/A", "N/A"

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
                    oper_state = "True"
                else:
                    oper_state = "False"

                # 아두이노 상태 업데이트
                arduino_thread.update_state(oper_state, final_pass)

                # 키 입력 처리
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):  # 'q'를 누르면 종료
                    break
                elif key == ord('s'):  # 's'를 누르면 H 값 + 70 계산
                    try:
                        h_adjusted_value = int(h_value) + 70
                    except (ValueError, KeyError):
                        print("Invalid H value received from Arduino")
                        h_adjusted_value = None

                # 센싱 데이터 출력
                cv2.putText(frame, f"A: {a_value}", (width - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                cv2.putText(frame, f"H: {h_value}", (width - 150, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"V: {v_value}", (width - 150, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

        


                # 프레임에 상태 및 점수 출력
                cv2.putText(frame, f"User: {user_thread.user_status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                cv2.putText(frame, f"Drowsiness: {drowsiness_thread.drowsiness_status}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"EAR: {drowsiness_thread.ear:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # 왼쪽 하단에 점수 출력
                cv2.putText(frame, f"User Score: {int(user_recognition_score)}", (10, height - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.putText(frame, f"Drowsy Score: {int(drowsiness_score)}", (10, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # 처리된 프레임 디스플레이
                cv2.imshow("Drowsiness Detection", frame)

          
    finally:
        # 스레드 정지
        video_thread.stop()
        user_thread.stop()
        drowsiness_thread.stop()
        arduino_thread.stop()

        # 스레드 종료 대기
        video_thread.join()
        user_thread.join()
        drowsiness_thread.join()
        arduino_thread.join()

        # OpenCV 창 닫기
        cv2.destroyAllWindows()
if __name__ == "__main__":
    main()