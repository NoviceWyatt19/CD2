
import cv2
import threading
import time
from modified_check_finted_model import detect_drowsy_with_gaze  # detect_drowsy_with_gaze 함수 사용
from user_recog import recognize_user_from_frame
import sys
sys.path.append("/Users/wyatt/Desktop/inst_CD2")

# 비디오 캡처 스레드
class VideoCaptureThread(threading.Thread):
    def __init__(self):
        super(VideoCaptureThread, self).__init__()
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.running = True

    def run(self):
        while self.running:
            ret, self.frame = self.cap.read()
            if not ret:
                self.running = False

    def stop(self):
        self.running = False
        self.cap.release()

# 유저 인식 스레드
class UserRecognitionThread(threading.Thread):
    def __init__(self, video_thread):
        super(UserRecognitionThread, self).__init__()
        self.video_thread = video_thread
        self.user_status = "No face detected"

    def run(self):
        while self.video_thread.running:
            frame = self.video_thread.frame
            if frame is not None:
                self.user_status = recognize_user_from_frame(frame)
            time.sleep(1 / 30)

# 졸음 감지 스레드
class DrowsinessDetectionThread(threading.Thread):
    def __init__(self, video_thread):
        super(DrowsinessDetectionThread, self).__init__()
        self.video_thread = video_thread
        self.drowsiness_status = ""
        self.left_eye_status = "Closed"
        self.right_eye_status = "Closed"
        self.processed_frame = None
        self.ear = 0.0  # EAR placeholder
        self.score = 0  # Placeholder for the score

    def run(self):
        while self.video_thread.running:
            frame = self.video_thread.frame
            if frame is not None:
                # detect_drowsy_with_gaze 함수 호출하여 처리된 프레임과 상태 받기
                self.processed_frame, self.drowsiness_status, self.ear, self.left_eye_status, self.right_eye_status, self.score = detect_drowsy_with_gaze(frame)

# 메인 루프
def main():
    video_thread = VideoCaptureThread()
    user_thread = UserRecognitionThread(video_thread)
    drowsiness_thread = DrowsinessDetectionThread(video_thread)

    video_thread.start()
    user_thread.start()
    drowsiness_thread.start()

    while video_thread.running:
        frame = video_thread.frame
        if frame is not None:
            # 프레임에 모델 결과 출력 (유저 확인, EAR, 눈 상태, 스코어)
            user_status = user_thread.user_status
            drowsiness_status = drowsiness_thread.drowsiness_status
            left_eye_status = drowsiness_thread.left_eye_status
            right_eye_status = drowsiness_thread.right_eye_status
            ear = drowsiness_thread.ear
            score = drowsiness_thread.score

            # Overlay text on frame
            cv2.putText(frame, f"User: {user_status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Drowsiness: {drowsiness_status}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"EAR: {ear:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(frame, f"Left Eye: {left_eye_status}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"Right Eye: {right_eye_status}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"Score: {score}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            # Display the frame
            cv2.imshow("Drowsiness Detection", frame)

            # Check for exit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Stop all threads and release resources
    video_thread.stop()
    user_thread.join()
    drowsiness_thread.join()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
