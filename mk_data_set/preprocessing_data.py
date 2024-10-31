import cv2
import os
import numpy as np
from facenet.src import facenet, align  # MTCNN 정렬을 위한 모듈
import configuration as con
import random

# 경로 설정
input_dir = con.dir_path['Mac']['preprocessing']
output_dir = con.dir_path['Mac']['comp_db']

image_size = 160
margin = 32
random_order = True
gpu_memory_fraction = 0.25

# MTCNN으로 얼굴 정렬 및 정제
def align_faces(input_dir, output_dir, image_size, margin, random_order, gpu_memory_fraction):
    align.align_dataset_mtcnn(
        input_dir, 
        output_dir, 
        image_size, 
        margin, 
        random_order, 
        gpu_memory_fraction
    )
    print("MTCNN으로 얼굴 정렬 완료")

# 이미지 밝기 조절
def adjust_brightness(image, factor):
    return cv2.convertScaleAbs(image, alpha=factor, beta=0)

# 가우시안 노이즈 추가
def add_gaussian_noise(image, mean=0, var=10):
    row, col, ch = image.shape
    sigma = var ** 0.5
    gauss = np.random.normal(mean, sigma, (row, col, ch))
    noisy = image + gauss
    return np.clip(noisy, 0, 255).astype(np.uint8)

# 이미지 회전
def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated

# 이미지 마스킹
# def mask_image(image, start_point=None, end_point=None, mask_size=(100, 100)):
#     (h, w) = image.shape[:2]
#     if not start_point or not end_point:
#         x1, y1 = w // 4, h // 4  # 기본 위치
#         x2, y2 = x1 + mask_size[0], y1 + mask_size[1]
#         start_point, end_point = (x1, y1), (x2, y2)
#     masked_image = image.copy()
#     cv2.rectangle(masked_image, start_point, end_point, (0, 0, 0), -1)
#     return masked_image
def mask_image(image):
    masked_image = image.copy()
    h, w = image.shape[:2]

    # 시작점과 마스크 크기를 랜덤하게 설정
    x1, y1 = random.randint(0, w // 2), random.randint(0, h // 2)
    mask_width, mask_height = random.randint(50, w // 4), random.randint(50, h // 4)
    x2, y2 = x1 + mask_width, y1 + mask_height
    start_point, end_point = (x1, y1), (x2, y2)
    
    # 마스크 색상도 랜덤으로 설정 (RGB)
    mask_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    # 마스크 적용
    cv2.rectangle(masked_image, start_point, end_point, mask_color, -1)
    return masked_image

# 이미지 수평 반전
def horizontal_flip(image):
    dst_image = image.copy()
    _, width, _ = dst_image.shape
    flipped_left = cv2.flip(dst_image[:, :width // 2], 1)
    flipped_right = cv2.flip(dst_image[:, width // 2:], 1)
    return {"left": flipped_left, "right": flipped_right}

# RGB 필터링 함수 (채널 강도 조절 방식)
def rgb_filter(image, r_factor=1.0, g_factor=1.0, b_factor=1.0):
    """각 채널의 강도를 조정하여 특정 채널을 강조하거나 약화시킵니다."""
    filtered_image = image.copy()
    
    # R, G, B 채널 각각에 필터 적용 (각각 2, 1, 0 인덱스)
    filtered_image[:, :, 2] = np.clip(filtered_image[:, :, 2] * r_factor, 0, 255)  # Red 채널
    filtered_image[:, :, 1] = np.clip(filtered_image[:, :, 1] * g_factor, 0, 255)  # Green 채널
    filtered_image[:, :, 0] = np.clip(filtered_image[:, :, 0] * b_factor, 0, 255)  # Blue 채널
    
    return filtered_image.astype(np.uint8)

# 전처리된 이미지 저장
def save_image(image, output_path, prefix, idx):
    filename = f"{prefix}_{idx}.jpg"
    cv2.imwrite(os.path.join(output_path, filename), image)

# 이미지 증강
def augment_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
            input_path = os.path.join(input_folder, filename)
            image = cv2.imread(input_path)

            # 가우시안 노이즈 추가
            noisy_image = add_gaussian_noise(image)
            save_image(noisy_image, output_folder, 'noisy', 1)

            # 회전 (5, 10, 15, 20, 25)
            for i, angle in enumerate([5, 10, 15, 20, 25]):
                rotated_image = rotate_image(image, angle)
                save_image(rotated_image, output_folder, 'rotated', angle)

            # 밝기 조절 (10단계)
            for i, factor in enumerate(np.linspace(0.5, 1.5, 10)):
                brightness_adjusted = adjust_brightness(image, factor)
                save_image(brightness_adjusted, output_folder, 'brightness', i)

            # 마스킹 (중간 부분 가리기)
            masked_image = mask_image(image)
            save_image(masked_image, output_folder, 'masked', 1)

            # 수평 반전
            flipped = horizontal_flip(image)
            flipped_left_filename = f"{filename.split('.')[0]}_flipped_left.png"
            flipped_right_filename = f"{filename.split('.')[0]}_flipped_right.png"
            cv2.imwrite(os.path.join(output_folder, flipped_left_filename), flipped['left'])
            cv2.imwrite(os.path.join(output_folder, flipped_right_filename), flipped['right'])

            # RGB 필터를 3:1:1 비율로 적용하여 저장
            for i in range(3):
                r_image = rgb_filter(image, r_factor=1.5, g_factor=1.0, b_factor=1.0)
                save_image(r_image, output_folder, 'R_filtered', f"{filename.split('.')[0]}_R_{i+1}")
                
            green_filtered = rgb_filter(image, r_factor=0.5, g_factor=1.5, b_factor=0.5)
            save_image(green_filtered, output_folder, 'green_filtered', 1)

            blue_filtered = rgb_filter(image, r_factor=0.5, g_factor=0.5, b_factor=1.5)
            save_image(blue_filtered, output_folder, 'blue_filtered', 1)

            print(f"Processed: {filename}")

# 얼굴 정렬 및 데이터 증강 실행
def main():
    # MTCNN을 이용한 얼굴 정렬
    align_faces(input_dir, output_dir, image_size, margin, random_order, gpu_memory_fraction)

    # 데이터 증강
    augment_images(output_dir, output_dir)

if __name__ == "__main__":
    main()