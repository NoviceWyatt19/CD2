import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from PIL import Image
import numpy as np

# MTCNN, Inception Resnet V1 모델
mtcnn = MTCNN(image_size=160, margin=0)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

# 등록된 유저 임베딩
user_embedding = torch.load('/Users/wyatt/Desktop/CD2_project/user_embedding.pt')
def recognize_user_from_frame(frame):
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    img_cropped = mtcnn(img)
    
    if img_cropped is not None:
        # 실시간 얼굴 임베딩
        current_embedding = resnet(img_cropped.unsqueeze(0))

        # 유사도 계산
        distance = (user_embedding - current_embedding).norm().item()
        if distance < 0.85:  
            return "User recognized"
        else:
            return "User not recognized"
    else:
        return "No face detected"
    
