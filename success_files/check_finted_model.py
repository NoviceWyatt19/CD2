import cv2
import dlib
import numpy as np
from success_gaze import get_eye_states_from_frame

# Dlib 얼굴 탐지기와 랜드마크 예측기 초기화
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("/Users/wyatt/Desktop/CD2_project/CD2_models/shape_predictor_68_face_landmarks.dat")

# EAR 계산 함수
def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# 눈 상태와 EAR을 계산하고 drowsiness 상태를 판단하는 함수
def detect_drowsiness_from_frame(frame, ear_threshold=0.2):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    
    drowsiness_status = "Awake"

    for face in faces:
        landmarks = predictor(gray, face)
        
        # 왼쪽 눈과 오른쪽 눈 랜드마크 추출
        left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
        right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])

        # EAR 계산
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        # EAR에 따라 drowsiness 상태 판단
        if ear < ear_threshold:
            drowsiness_status = "Eyes Closed"
            ear = 0.0  # 눈 감김 상태로 EAR을 0으로 설정
        else:
            drowsiness_status = "Eyes Open"
            # 눈 윤곽선 그리기
            cv2.drawContours(frame, [cv2.convexHull(left_eye)], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [cv2.convexHull(right_eye)], -1, (0, 255, 0), 1)

        # EAR 및 drowsiness 상태 텍스트 출력
        cv2.putText(frame, f"EAR: {ear:.3f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        cv2.putText(frame, f"Drowsiness: {drowsiness_status}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    return frame, drowsiness_status

def detect_drowsy_with_gaze(frame):
    # 프레임에서 눈 상태 가져오기
    left_eye_state, right_eye_state = get_eye_states_from_frame(frame)

    # 눈 상태가 감지된 경우 화면에 표시
    if left_eye_state and right_eye_state:
        if left_eye_state == 'Open' and right_eye_state == 'Open':
            frame, drowsiness_status = detect_drowsiness_from_frame(frame)
        else:
            # 눈이 감긴 경우 EAR을 0으로 표시하고 'Eyes Closed' 메시지 표시
            # cv2.putText(frame, "Left Eye: Closed", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            # cv2.putText(frame, "Right Eye: Closed", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, "EAR: 0.000", (300, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    else:
        cv2.putText(frame, "No face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    return frame, drowsiness_status
