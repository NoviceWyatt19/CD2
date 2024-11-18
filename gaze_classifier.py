import cv2
import dlib
import numpy as np
from tensorflow.keras.models import load_model

# 모델 로드
gaze_model = load_model("/Users/wyatt/Desktop/CD2_project/CD2_models/working.keras")

# Dlib 얼굴 탐지기와 랜드마크 
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("/Users/wyatt/Desktop/CD2_project/CD2_models/shape_predictor_68_face_landmarks.dat")


# gaze model을 위한 전처리
def preprocess_eye(eye):
    gray_eye = cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)
    resized_eye = cv2.resize(gray_eye, (60, 60))
    normalized_eye = resized_eye / 255.0
    return np.expand_dims(normalized_eye, axis=(0, -1))

# gaze model 출력
def detect_eye_states(left_eye, right_eye):
    left_eye_input = preprocess_eye(left_eye)
    right_eye_input = preprocess_eye(right_eye)

    left_prediction = gaze_model.predict(left_eye_input)[0][0]
    right_prediction = gaze_model.predict(right_eye_input)[0][0]

    left_eye_state = "Closed" if left_prediction >= 0.34 else "Open" # 0.6
    right_eye_state = "Closed" if right_prediction >= 0.34 else "Open"

    return left_eye_state, right_eye_state


# 전역 변수로 이전 프레임 좌표 저장
prev_left_eye_points = None
prev_right_eye_points = None

# 눈의 랜드마크를 기반으로 눈 영역을 크롭
def crop_eye_region(frame, eye_points):
    eye_center = np.mean(eye_points, axis=0).astype(int)
    y_min = max(0, eye_center[1] - 70)
    y_max = min(frame.shape[0], eye_center[1] + 70)
    x_min = max(0, eye_center[0] - 70)
    x_max = min(frame.shape[1], eye_center[0] + 70)
    
    cropped = frame[y_min:y_max, x_min:x_max]
    
    # 크롭된 영역 유효성 검사
    if cropped.size == 0 or cropped.shape[0] == 0 or cropped.shape[1] == 0:
        return None
    return cropped

# 프레임에서 눈 상태를 반환
# 랜드마크 탐지 실패 시 이전 프레임 좌표를 사용
def get_eye_states_from_frame(frame):
    global prev_left_eye_points, prev_right_eye_points

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    if len(faces) > 0:
        for face in faces:
            landmarks = predictor(gray, face)

            # 현재 프레임에서 눈 랜드마크 추출
            left_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
            right_eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])

            # 크롭된 눈 영역
            left_eye_crop = crop_eye_region(frame, left_eye_points)
            right_eye_crop = crop_eye_region(frame, right_eye_points)

            # 유효한 크롭된 영역이 있을 때
            if left_eye_crop is not None and right_eye_crop is not None:
                # 현재 좌표 저장
                prev_left_eye_points = left_eye_points
                prev_right_eye_points = right_eye_points
                return detect_eye_states(left_eye_crop, right_eye_crop)

    # 얼굴이 감지되지 않은 경우 이전 프레임 좌표를 사용
    if prev_left_eye_points is not None and prev_right_eye_points is not None:
        left_eye_crop = crop_eye_region(frame, prev_left_eye_points)
        right_eye_crop = crop_eye_region(frame, prev_right_eye_points)

        if left_eye_crop is not None and right_eye_crop is not None:
            return detect_eye_states(left_eye_crop, right_eye_crop)

    # 랜드마크도 감지되지 않고 이전 좌표도 없으면 기본값 반환
    return "Closed", "Closed"


def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)


def detect_drowsy_with_gaze(frame, ear_threshold=0.2):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    drowsiness_status = "None"
    ear = 0.0
    left_eye_status, right_eye_status = get_eye_states_from_frame(frame)

    if len(faces) == 0:
        # 얼굴이 없을 때 
        processed_frame = frame.copy()
        cv2.putText(
            processed_frame,
            "No face detected",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )
        # 빈 값을 반환
        return processed_frame, drowsiness_status, ear, "Closed", "Closed", [], []


    if left_eye_status == "Closed" and right_eye_status == "Closed":
        return frame, "Drowsy", 0.0, left_eye_status, right_eye_status, [], []

    for face in faces:
        landmarks = predictor(gray, face)

        # 눈 랜드마크 추출
        left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
        right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])

        # EAR 계산
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        # 졸음 상태 판단
        if ear < ear_threshold:
            drowsiness_status = "Little Drowsy"
        else:
            drowsiness_status = "Awake"

        # 눈 윤곽선 그리기
        cv2.drawContours(frame, [left_eye], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [right_eye], -1, (0, 255, 0), 1)

    return frame, drowsiness_status, ear, left_eye_status, right_eye_status, left_eye, right_eye