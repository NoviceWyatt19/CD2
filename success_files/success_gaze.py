import cv2
import dlib
import numpy as np
from tensorflow.keras.models import load_model

# 모델 로드
gaze_model = load_model("/Users/wyatt/Desktop/inst_CD2/CD2_models/working.keras")

# Dlib 얼굴 탐지기와 랜드마크 예측기 초기화
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("/Users/wyatt/Desktop/inst_CD2/CD2_models/shape_predictor_68_face_landmarks.dat")

# 눈 상태 감지 함수
def preprocess_eye(eye):
    gray_eye = cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)
    resized_eye = cv2.resize(gray_eye, (60, 60))
    normalized_eye = resized_eye / 255.0
    return np.expand_dims(normalized_eye, axis=(0, -1))

def detect_eye_states(left_eye, right_eye):
    # 각각의 눈을 전처리 후 예측
    left_eye_input = preprocess_eye(left_eye)
    right_eye_input = preprocess_eye(right_eye)

    left_prediction = gaze_model.predict(left_eye_input)[0][0]
    right_prediction = gaze_model.predict(right_eye_input)[0][0]

    # 임계값을 설정하여 열린 상태와 닫힌 상태를 구분
    left_eye_state = 'Open' if left_prediction >= 0.333 else 'Closed'
    right_eye_state = 'Open' if right_prediction >= 0.322 else 'Closed'

    # 상태 반환
    return left_eye_state, right_eye_state

def get_eye_states_from_frame(frame):
    # 프레임을 그레이스케일로 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        # 왼쪽 눈 랜드마크 추출
        left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
        right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])

        # 왼쪽 눈 중심을 기준으로 크롭
        left_eye_center = np.mean(left_eye, axis=0).astype(int)
        left_eye_y_min = max(0, left_eye_center[1] - 70)
        left_eye_y_max = min(frame.shape[0], left_eye_center[1] + 70)
        left_eye_x_min = max(0, left_eye_center[0] - 70)
        left_eye_x_max = min(frame.shape[1], left_eye_center[0] + 70)
        left_eye_crop = frame[left_eye_y_min:left_eye_y_max, left_eye_x_min:left_eye_x_max]

        # 오른쪽 눈 중심을 기준으로 크롭
        right_eye_center = np.mean(right_eye, axis=0).astype(int)
        right_eye_y_min = max(0, right_eye_center[1] - 70)
        right_eye_y_max = min(frame.shape[0], right_eye_center[1] + 70)
        right_eye_x_min = max(0, right_eye_center[0] - 70)
        right_eye_x_max = min(frame.shape[1], right_eye_center[0] + 70)
        right_eye_crop = frame[right_eye_y_min:right_eye_y_max, right_eye_x_min:right_eye_x_max]

        # 눈 상태 예측
        if left_eye_crop.size and right_eye_crop.size:  # 눈이 화면에 있을 때만 예측 수행
            left_eye_state, right_eye_state = detect_eye_states(left_eye_crop, right_eye_crop)
            return left_eye_state, right_eye_state

    # 얼굴을 찾지 못한 경우 None 반환
    return None, None
