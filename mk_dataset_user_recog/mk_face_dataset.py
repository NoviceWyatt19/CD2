import os
import cv2
from facenet_pytorch import MTCNN
from PIL import Image

# MTCNN 모델
mtcnn = MTCNN()

def save_cropped_face_with_margin_from_frame(frame, save_path, margin=0.1):
    boxes, _ = mtcnn.detect(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
    
    if boxes is None:
        print("얼굴이 감지되지 않았습니다.")
        return False

    x1, y1, x2, y2 = boxes[0]
    width = x2 - x1
    height = y2 - y1
    
    # 폭과 높이에 margin 적용
    x1 = max(int(x1 - width * margin), 0)
    y1 = max(int(y1 - height * margin), 0)
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
def capture_face_from_webcam(save_path):
    cap = cv2.VideoCapture(0) 
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 가져올 수 없습니다.")
            break
        
        # 얼굴 감지 및 저장
        if save_cropped_face_with_margin_from_frame(frame, save_path):
            break 
        
        # 프레임 출력
        cv2.imshow('Webcam', frame)
        
       
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 리소스 해제
    cap.release()
    cv2.destroyAllWindows()

cnt = 1
while cnt < 100:
    dataset_path = f'/Users/wyatt/Desktop/inst_CD2/detect_face_user/cropped_user_image{cnt}.jpg'
    capture_face_from_webcam(save_path=dataset_path)
    cnt += 1