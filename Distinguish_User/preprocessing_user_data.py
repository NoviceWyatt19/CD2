# for N in {1..4}; do \
# python src/align/align_dataset_mtcnn.py \
# ~/datasets/lfw/raw \
# ~/datasets/lfw/lfw_mtcnnpy_160 \
# --image_size 160 \
# --margin 32 \
# --random_order \
# --gpu_memory_fraction 0.25 \
# & done

from facenet.src import facenet, align
import settings as s
import cv2
import numpy as np
import os

input_dir = s.dir_path['Mac']['preprocessing']
output_dir = s.dir_path['Mac']['comp_db']

image_size = 160
margin = 32
random_order = True
gpu_memory_fraction = 0.25

# MTCNN으로 얼굴 정렬 및 정제
align.align_dataset_mtcnn(
    input_dir, 
    output_dir, 
    image_size, 
    margin, 
    random_order, 
    gpu_memory_fraction
    )

# 가우시안 노이즈
def add_gaussian_noise(image, mean=0, var=10):
    row, col, ch = image.shape
    sigma = var ** 0.5
    gauss = np.random.normal(mean, sigma, (row, col, ch))
    noisy = image + gauss
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy

# 이미지를 회전
def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (w, h))
    return rotated

# 이미지 블라인딩
def mask_image(image, start_point, end_point):
    masked_image = image.copy()
    cv2.rectangle(masked_image, start_point, end_point, (0, 0, 0), -1)  # 사각형 부분을 검은색으로
    return masked_image


# 데이터 증강
def augment_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".png"):
            img_path = os.path.join(input_folder, filename)
            image = cv2.imread(img_path)

            if image is None:
                continue

            # RGB 채널 분리
            (B, G, R) = cv2.split(image)

            # 이미지 회전: 30도, 90도, 180도, 200도
            angles = [30, 90, 180, 200]
            for angle in angles:
                rotated = rotate_image(image, angle)
                rotated_filename = f"{filename.split('.')[0]}_rotated_{angle}.png"
                cv2.imwrite(os.path.join(output_folder, rotated_filename), rotated)

            # 가우시안 노이즈 추가
            noisy_image = add_gaussian_noise(image)
            noisy_filename = f"{filename.split('.')[0]}_noisy.png"
            cv2.imwrite(os.path.join(output_folder, noisy_filename), noisy_image)

            # RGB 채널 저장 (각각 분리된 채널로 저장)
            cv2.imwrite(os.path.join(output_folder, f"{filename.split('.')[0]}_R.png"), R)
            cv2.imwrite(os.path.join(output_folder, f"{filename.split('.')[0]}_G.png"), G)
            cv2.imwrite(os.path.join(output_folder, f"{filename.split('.')[0]}_B.png"), B)

            # 이미지의 일부분을 검게 가리기 (이미지 중간 부분을 예시로 마스킹)
            h, w = image.shape[:2]
            start_point = (int(w * 0.25), int(h * 0.25))  # 사각형 시작 좌표
            end_point = (int(w * 0.75), int(h * 0.75))  # 사각형 끝 좌표
            masked_image = mask_image(image, start_point, end_point)
            masked_filename = f"{filename.split('.')[0]}_masked.png"
            cv2.imwrite(os.path.join(output_folder, masked_filename), masked_image)

    print("데이터 증강이 완료되었습니다.")

# 폴더 경로 설정
input_folder = s.dir_path['mtcnn']  # 원본 이미지 폴더 경로
output_folder = s.dir_path['preprocessing']  # 증강된 이미지 저장 폴더 경로

augment_images(input_folder, output_folder)