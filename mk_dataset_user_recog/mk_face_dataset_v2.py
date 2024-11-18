import os
import cv2
from facenet_pytorch import MTCNN
from PIL import Image

# MTCNN 모델 초기화
mtcnn = MTCNN()

def save_cropped_face_with_margin_from_frame(frame, save_path='cropped_user_image.jpg', margin=0.15, top_margin=0.15):
    # MTCNN으로 얼굴 탐지
    boxes, _ = mtcnn.detect(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
    
    if boxes is None:
        print("얼굴이 감지되지 않았습니다.")
        return False

    # 첫 번째로 감지된 얼굴 범위 사용
    x1, y1, x2, y2 = boxes[0]
    width = x2 - x1
    height = y2 - y1

    # 폭과 높이에 margin 적용 및 top_margin 추가
    x1 = max(int(x1 - width * margin), 0)
    y1 = max(int(y1 - height * (margin + top_margin)), 0)  # top_margin을 추가
    x2 = min(int(x2 + width * margin), frame.shape[1])
    y2 = min(int(y2 + height * margin), frame.shape[0])
    
    # 얼굴 영역 크롭
    cropped_face = frame[y1:y2, x1:x2]
    
    # 이미지 저장
    cropped_face_pil = Image.fromarray(cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB))
    cropped_face_pil.save(save_path)
    print(f"크롭된 얼굴 이미지가 {save_path}에 저장되었습니다.")
    return True

# 웹캠에서 프레임을 받아 얼굴 감지 및 저장
def capture_face_from_webcam():
    cap = cv2.VideoCapture(1)  # 0번 웹캠 사용
    cnt = 1
    
    while cnt <= 100:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 가져올 수 없습니다.")
            break
        
        # 프레임 출력
        cv2.imshow('Webcam', frame)
        
        # 특정 키 ('s')를 누르면 저장
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            dataset_path = f'/Users/wyatt/Desktop/inst_CD2/detect_face_user/cropped_user_image{cnt}.jpg'
            if save_cropped_face_with_margin_from_frame(frame, dataset_path):
                cnt += 1  # 저장할 때만 cnt 증가
            
        # 'q' 키를 누르면 종료
        elif key == ord('q'):
            break
    
    # 리소스 해제
    cap.release()
    cv2.destroyAllWindows()

# 실행
capture_face_from_webcam()