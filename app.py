import cv2
import queue
import time
from threading import Thread
import serial
import configuration as con  # 사용자 업로드한 설정 파일 사용
from Distinguish_User.user_recognizer import recognize_user, add_new_user
from DD_classifier import check_drowsiness  # 졸음 분류기 함수 가져오기
from face_detector_mtcnn import detect_faces as detect_faces_mtcnn

# 비디오 캡처 초기화
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 20)

frame_queue = queue.Queue(maxsize=100)

# 아두이노 시리얼 연결 (COM 포트와 baudrate는 환경에 맞게 설정)
try:
    arduino = serial.Serial(con.ser_setting["Mac"], con.ser_setting['Speed'][0])
except serial.SerialException as e:
    print(f"Failed to connect to Arduino: {e}")
    arduino = None

# 프레임 캡처 및 버퍼링
def capture_frames():
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_queue.full():
                frame_queue.get()  # 가장 오래된 프레임 제거
            frame_queue.put(frame)
        except Exception as e:
            print(f"Error capturing frames: {e}")

capture_thread = Thread(target=capture_frames, daemon=True)
capture_thread.start()

user_recognition_flag = False
drowsiness_flag = False
last_user_check_time = time.time()

def preprocess_frame(frame):
    # 얼굴 탐지
    faces = detect_faces_mtcnn(frame)
    cropped_faces = []

    for face in faces:
        x, y, w, h = face['box']
        x, y = max(x, 0), max(y, 0)  # 좌표가 음수가 되지 않도록 처리
        cropped_face = frame[y:y+h, x:x+w]
        resized_face = cv2.resize(cropped_face, (160, 160))  # FaceNet 요구사항에 맞춤
        cropped_faces.append(resized_face)

    return cropped_faces

def process_user_recognition():
    global user_recognition_flag, last_user_check_time
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            current_time = time.time()

            if current_time - last_user_check_time >= 5:  # 5초 쿨타임
                try:
                    faces = preprocess_frame(frame)
                    for face in faces:
                        message, recognized_name = recognize_user(face)
                        print(message)

                        # 결과 시각화 (디버깅 및 사용자 피드백)
                        if recognized_name:
                            user_recognition_flag = True
                            cv2.putText(frame, f"User: {recognized_name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        else:
                            user_recognition_flag = False
                            cv2.putText(frame, "Unknown User", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    # 디스플레이 프레임 (디버깅)
                    cv2.imshow('User Recognition', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    last_user_check_time = current_time

                except Exception as e:
                    print(f"Error during user recognition: {e}")

def process_drowsiness_detection():
    global drowsiness_flag
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            try:
                faces = preprocess_frame(frame)
                for face in faces:
                    if check_drowsiness(face):
                        drowsiness_flag = True
                        print("Drowsiness detected!")
                        cv2.putText(frame, "Drowsiness Detected", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    else:
                        drowsiness_flag = False

                # 디스플레이 프레임 (디버깅)
                cv2.imshow('Drowsiness Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            except Exception as e:
                print(f"Error during drowsiness detection: {e}")

# 종료 처리 함수
def cleanup():
    cap.release()
    cv2.destroyAllWindows()
    if arduino:
        arduino.close()

# 스레드 초기화 및 시작
user_thread = Thread(target=process_user_recognition, daemon=True)
drowsiness_thread = Thread(target=process_drowsiness_detection, daemon=True)
user_thread.start()
drowsiness_thread.start()

# 메인 루프
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    cleanup()
    print("Program interrupted and terminated gracefully.")
except Exception as e:
    cleanup()
    print(f"Unexpected error: {e}")