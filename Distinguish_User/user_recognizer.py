# user_recognizer.py
import os
import numpy as np
import settings as s
from sklearn.metrics.pairwise import euclidean_distances
from embedding_img import *

# 디랙토리 생성
directory = f'{s.path_tpye['Mac']}recog_user'
try:
    os.mkdir(directory)
    #현재 폴더 경로; 작업 폴더 기준
    print(f"{directory} is made in {os.getcwd()}")
    work_place = os.getcwd()

except FileExistsError:
    print(f"{directory} already exist")

# 사용자 및 다른 인물 이미지 디렉토리
try:
    other_dir = f'{work_place}/recog_user/other'
    user_dir = f'{work_place}/recog_user/user'
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
new_image_path = f'{s.dataset_user['embedding']}.{s.file_type[1]}'  # 새로운 이미지 경로 수정
recognize_user(new_image_path)