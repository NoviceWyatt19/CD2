import os
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image

# MTCNN과 Inception Resnet V1 모델 초기화
mtcnn = MTCNN(image_size=160, margin=0)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

def register_user_embedding(img_folder, save_path='user_embedding.pt'):
    embeddings = []

    # 이미지 파일 목록 가져오기 (.jpg, .png 파일만)
    file_names = [f for f in os.listdir(img_folder) if f.endswith(('.jpg', '.png'))]

    for file_name in file_names:
        img_path = os.path.join(img_folder, file_name)
        
        # 이미지 열기
        try:
            img = Image.open(img_path)
        except (IOError, UnidentifiedImageError):
            print(f"이미지 파일을 열 수 없습니다: {img_path}")
            continue

        # MTCNN으로 얼굴 검출 및 크롭
        img_cropped = mtcnn(img)
        if img_cropped is not None:
            # 얼굴 임베딩 생성
            embedding = resnet(img_cropped.unsqueeze(0))
            embeddings.append(embedding)

    if embeddings:
        # 여러 장의 임베딩 평균 계산
        user_embedding = torch.mean(torch.stack(embeddings), dim=0)
        
        # 평균 임베딩 저장
        torch.save(user_embedding, save_path)
        print(f"평균 유저 임베딩이 {save_path}에 저장되었습니다.")
    else:
        print("얼굴이 감지된 이미지가 없습니다.")

# 유저 이미지 폴더 경로
image_folder = '/Users/wyatt/Desktop/inst_CD2/detect_face_user'
register_user_embedding(image_folder)