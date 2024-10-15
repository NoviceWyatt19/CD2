import settings as s
import cv2
import numpy as np
from mtcnn import MTCNN
from keras.models import load_model
from sklearn.preprocessing import Normalizer
from numpy import expand_dims
from scipy.spatial.distance import cosine
import os

# FaceNet 모델과 MTCNN 로드
facenet_model = load_model('facenet_keras.h5')
mtcnn = MTCNN()

# 새로운 유저를 추가
def add_new_user(embedding, name):
    # 새로운 유저의 임베딩을 저장
    np.save(f'database/{name}.npy', embedding)
    database[name] = embedding
    print(f'{name} has been added to the database.')

# 얼굴 임베딩 생성 함수
def get_embedding(model, face_pixels):
    face_pixels = face_pixels.astype('float32')
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    face_pixels = expand_dims(face_pixels, axis=0)
    embedding = model.predict(face_pixels)
    return embedding[0]

# 코사인 유사도 계산 함수
def is_match(known_embedding, candidate_embedding, threshold=0.5):
    score = cosine(known_embedding, candidate_embedding)
    return score <= threshold

# 임베딩을 데이터베이스에서 로드
database = s.dir_path["preprocessing"]
if os.path.exists('database'):
    for filename in os.listdir('database'):
        if filename.endswith('.npy'):
            name = filename.replace('.npy', '')
            database[name] = np.load(os.path.join('database', filename))

# 웹캡 캡처 시작
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 얼굴 탐지
    results = mtcnn.detect_faces(frame)
    if results:
        for result in results:
            x, y, width, height = result['box']
            face = frame[y:y+height, x:x+width]

            # 얼굴 크기 조정 (160x160, FaceNet 요구사항)
            face = cv2.resize(face, (160, 160))

            # 얼굴 임베딩 생성
            embedding = get_embedding(facenet_model, face)

            # 데이터베이스와 비교
            match = False
            for name, db_embedding in database.items():
                if is_match(db_embedding, embedding):
                    match = True
                    print(f'User matched: {name}')
                    break

            if not match:
                print('Unknown user')
                user_input = input('New user detected. Would you like to add this user? (y/n): ')
                if user_input.lower() == 'y':
                    new_user_name = input('Enter new user name: ')
                    add_new_user(embedding, new_user_name)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()