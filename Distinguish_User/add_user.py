import os
import cv2
import numpy as np
from mtcnn import MTCNN
from keras.models import load_model
from numpy import expand_dims

# FaceNet 모델과 MTCNN 로드
facenet_model = load_model('facenet_keras.h5')
mtcnn = MTCNN()

# 얼굴 임베딩 생성 함수
def get_embedding(model, face_pixels):
    face_pixels = face_pixels.astype('float32')
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    face_pixels = expand_dims(face_pixels, axis=0)
    embedding = model.predict(face_pixels)
    return embedding[0]

# 데이터셋에서 얼굴 임베딩을 추출하여 데이터베이스에 추가하는 함수
def add_user_from_dataset(dataset_path, user_name):
    embeddings = []
    for filename in os.listdir(dataset_path):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join(dataset_path, filename)
            image = cv2.imread(image_path)
            
            # 얼굴 탐지
            results = mtcnn.detect_faces(image)
            if results:
                x, y, width, height = results[0]['box']
                face = image[y:y+height, x:x+width]
                
                # 얼굴 크기 조정 (160x160, FaceNet 요구사항)
                face = cv2.resize(face, (160, 160))

                # 얼굴 임베딩 생성
                embedding = get_embedding(facenet_model, face)
                embeddings.append(embedding)

    # 여러 이미지에서 임베딩을 평균으로 결합하여 하나의 벡터로 저장
    user_embedding = np.mean(embeddings, axis=0)

    # 임베딩을 데이터베이스에 저장
    np.save(f'database/{user_name}.npy', user_embedding)
    print(f'{user_name} has been added to the database.')

# 유저 데이터셋 경로와 유저 이름 입력
user_name = 'new_user'
dataset_path = 'path_to_user_images'  # 유저 데이터셋 경로

# 유저 추가
add_user_from_dataset(dataset_path, user_name)