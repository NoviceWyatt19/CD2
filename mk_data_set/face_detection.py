from mtcnn.mtcnn import MTCNN
import sys
import cv2
import os
import numpy as np

# main folder 경로를 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import configuration as con
from frame_utils import get_frame  # frame_utils에서 get_frame 가져오기

def resize_N_pad(img, size=(160, 160)):
    h, w, _ = img.shape
    target_h, target_w = size

    # Scaling
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Padding
    delta_w = target_w - new_w
    delta_h = target_h - new_h
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)
    color = [0, 0, 0]  # Black padding

    new_img = cv2.copyMakeBorder(resized_img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return new_img

def crop_face_with_margin(image, x, y, width, height, target_size=160, margin=0.1):
    # 마진 추가
    margin_x = int(width * margin)
    margin_y = int(height * margin)
    
    # 마진을 적용한 새로운 박스 좌표
    new_x = max(x - margin_x, 0)
    new_y = max(y - margin_y, 0)
    new_width = min(width + 2 * margin_x, image.shape[1] - new_x)
    new_height = min(height + 2 * margin_y, image.shape[0] - new_y)
    
    # 박스가 target_size보다 작으면 중심을 기준으로 확장
    if new_width < target_size or new_height < target_size:
        center_x = x + width // 2
        center_y = y + height // 2
        
        half_size = target_size // 2
        new_x = max(center_x - half_size, 0)
        new_y = max(center_y - half_size, 0)
        new_width = target_size
        new_height = target_size

        # 이미지 경계 체크
        if new_x + new_width > image.shape[1]:
            new_width = image.shape[1] - new_x
        if new_y + new_height > image.shape[0]:
            new_height = image.shape[0] - new_y

    # 얼굴 크롭
    cropped_face = image[new_y:new_y + new_height, new_x:new_x + new_width]
    
    # 리사이즈
    resized_face = resize_N_pad(cropped_face, size=(target_size, target_size))
    return resized_face

# detect_N_mark_face 함수에서 crop_face_with_margin을 호출하도록 수정
def detect_N_mark_face(frame, cnt, d_type='img'):
    detector = MTCNN()

    if d_type == 'img':
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = detector.detect_faces(img_rgb)
        detected = len(result) > 0

        if detected:
            for person in result:
                bounding_box = person['box']
                x, y, width, height = bounding_box
                face_160x160 = crop_face_with_margin(img_rgb, x, y, width, height)

                # Save the cropped face
                output_path = os.path.join(con.dir_path["Mac"]["mctnn"], f'cropped_face_{cnt}.png')
                cv2.imwrite(output_path, cv2.cvtColor(face_160x160, cv2.COLOR_RGB2BGR))
                print(f"Cropped face saved at {output_path}")
        else:
            print("No face detected.")

if __name__ == "__main__":
    d_type = 'img'  # 'img' or 'webcam'으로 변경 가능
    cnt = 0

    if d_type == 'webcam':
        # VideoCapture 객체 생성
        capture = cv2.VideoCapture(0)  # 0은 기본 웹캠, 필요에 따라 다른 장치 인덱스 사용
        try:
            while cnt <= 200:
                frame = get_frame(capture)  # VideoCapture 객체에서 프레임 가져오기
                detect_N_mark_face(frame, cnt, d_type='webcam')
                cnt += 1
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # VideoCapture 객체 해제
            capture.release()
            cv2.destroyAllWindows()

    elif d_type == 'img':
        try:
            while cnt <= 300:
                # 이미지 파일 경로 지정
                image_path = os.path.join(con.dir_path['Mac']['cam'], f'valid_frame_{cnt}.png')  # 각 이미지 파일 경로
                frame = cv2.imread(image_path)  # 이미지를 로드
                if frame is not None:
                    detect_N_mark_face(frame, cnt, d_type='img')
                else:
                    print(f"Image not found: {image_path}")
                    break  # 이미지가 없으면 반복을 중단합니다
                cnt += 1
        except Exception as e:
            print(f"An error occurred: {e}")