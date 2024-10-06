# user_recognizer.py
import os
import numpy as np
import settings as s
from sklearn.metrics.pairwise import euclidean_distances

# 디랙토리 생성
directory = f'{s.dir_path['Mac']['comp_db']}'

print(f"{directory} is in {os.getcwd()}")

if not os.path.exists(directory):
    print(f"{directory} dosen't exist")

# 사용자 및 다른 인물 이미지 디렉토리
try:
    # other_dir -> kaggle에서 jpg 긁어오기
    # user_dir -> 전처리 파일에서 가져오기
    other_dir = f'{directory}/other'
    user_dir = f'{directory}/user'
    
except FileExistsError:
    print("<ERROR> please, check your directory")

# 임베딩 생성
user_embeddings, other_embeddings = create_embeddings(user_dir, other_dir)

# 새로운 이미지의 임베딩 생성
def recognize_user(new_image_path):
    new_embedding = get_embedding(model, new_image_path)  # facenet_embedding 모듈에서 get_embedding 함수 호출

    # 사용자와 다른 인물 임베딩 간의 거리 계산
    user_distances = euclidean_distances(new_embedding, user_embeddings)
    other_distances = euclidean_distances(new_embedding, other_embeddings)

    # 거리 계산 및 결과 확인
    user_min_distance = np.min(user_distances)
    other_min_distance = np.min(other_distances)

    threshold = 0.5  # 임계값 설정

    if user_min_distance < threshold:
        print("사용자입니다.")
    else:
        print("사용자가 아닙니다.")

# 새로운 이미지 경로
embeded_img_path = f'{s.dir_path['Mac']['embedding']}.{s.file_type[1]}'  # 새로운 이미지 경로 수정
recognize_user(embeded_img_path)