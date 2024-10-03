import os
import numpy as np
import cv2

# 이미지 전처리 및 임베딩 생성 함수는 위에서 설명한 것과 동일해

# 모든 인물의 임베딩 생성
embeddings = []
labels = []

# 데이터셋 폴더 내의 각 인물 폴더를 순회
for person in os.listdir(dataset_dir):
    person_folder = os.path.join(dataset_dir, person)
    
    if os.path.isdir(person_folder):  # 폴더인 경우
        for filename in os.listdir(person_folder):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                image_path = os.path.join(person_folder, filename)
                embedding = get_embedding(model, image_path)
                embeddings.append(embedding)
                labels.append(person)  # 해당 인물의 이름을 레이블로 사용

# 임베딩 배열로 변환
embeddings = np.array(embeddings).reshape(len(embeddings), -1)