# facenet_embedding.py
import os
import numpy as np
import cv2
from tensorflow.keras.models import load_model

# FaceNet 모델 불러오기
model = load_model('facenet_keras.h5')  # 적절한 FaceNet 모델 경로로 수정

# 이미지 전처리 함수
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (160, 160))  # FaceNet 입력 크기로 조정
    img = img.astype('float32') / 255.0  # 정규화
    img = np.expand_dims(img, axis=0)  # 배치 차원 추가
    return img

# 이미지에서 임베딩 생성
def get_embedding(model, image_path):
    img = preprocess_image(image_path)
    embedding = model.predict(img)
    return embedding

# 데이터셋 임베딩 생성 함수
def create_embeddings(user_dir, other_dir):
    user_embeddings = []
    other_embeddings = []

    # 사용자 이미지 디렉토리
    for filename in os.listdir(user_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join(user_dir, filename)
            embedding = get_embedding(model, image_path)
            user_embeddings.append(embedding)

    # 다른 인물 이미지 디렉토리
    for filename in os.listdir(other_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join(other_dir, filename)
            embedding = get_embedding(model, image_path)
            other_embeddings.append(embedding)

    # 임베딩 배열로 변환
    user_embeddings = np.array(user_embeddings).reshape(len(user_embeddings), -1)
    other_embeddings = np.array(other_embeddings).reshape(len(other_embeddings), -1)
    
    return user_embeddings, other_embeddings