import cv2
import os
import numpy as np

def adjust_brightness(image, factor):
    # 이미지 밝기 조절 (0.0 ~ 1.0은 어둡게, 1.0 ~ 그 이상은 밝게)
    return cv2.convertScaleAbs(image, alpha=factor, beta=0)

def add_gaussian_noise(image, mean=0, var=10):
    # 가우시안 노이즈 추가
    row, col, ch = image.shape
    sigma = var ** 0.5
    gauss = np.random.normal(mean, sigma, (row, col, ch))
    gauss = gauss.reshape(row, col, ch)
    noisy = image + gauss
    return np.clip(noisy, 0, 255).astype(np.uint8)

def apply_rotation(image, angle):
    # 이미지 회전
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated

def apply_mask(image, mask_size=(100, 100)):
    # 이미지에 특정 부분 가리기
    (h, w) = image.shape[:2]
    x1, y1 = w // 4, h // 4  # 임의의 위치 선정
    x2, y2 = x1 + mask_size[0], y1 + mask_size[1]
    masked_image = image.copy()
    cv2.rectangle(masked_image, (x1, y1), (x2, y2), (0, 0, 0), -1)
    return masked_image

def save_image(image, output_path, prefix, idx):
    # 전처리된 이미지 저장
    filename = f"{prefix}_{idx}.jpg"
    cv2.imwrite(os.path.join(output_path, filename), image)

def augment_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.jpg') or filename.endswith('.jpeg'):
            input_path = os.path.join(input_folder, filename)
            image = cv2.imread(input_path)
            
            # R, G, B 스케일을 10단계로 조절하여 저장
            for r_scale in np.linspace(0, 1, 10):
                for g_scale in np.linspace(0, 1, 10):
                    for b_scale in np.linspace(0, 1, 10):
                        modified_image = image.copy()
                        modified_image[:, :, 0] = (modified_image[:, :, 0] * b_scale).astype(np.uint8)
                        modified_image[:, :, 1] = (modified_image[:, :, 1] * g_scale).astype(np.uint8)
                        modified_image[:, :, 2] = (modified_image[:, :, 2] * r_scale).astype(np.uint8)
                        save_image(modified_image, output_folder, 'RGB_scaled', f"{r_scale}_{g_scale}_{b_scale}")

            # 특정 부분 가리기 (마스킹)
            masked_image = apply_mask(image)
            save_image(masked_image, output_folder, 'masked', 1)

            # 밝기 조절 (10단계)
            for i, factor in enumerate(np.linspace(0.5, 1.5, 10)):
                brightness_adjusted = adjust_brightness(image, factor)
                save_image(brightness_adjusted, output_folder, 'brightness', i)

            # 가우시안 노이즈 추가
            noisy_image = add_gaussian_noise(image)
            save_image(noisy_image, output_folder, 'noisy', 1)

            # 회전 (30도, 90도, 135도, 180도, 270도)
            for i, angle in enumerate([30, 90, 135, 180, 270]):
                rotated_image = apply_rotation(image, angle)
                save_image(rotated_image, output_folder, 'rotated', angle)

            print(f"Processed: {filename}")


input_folder = 'input_images'  # 원본 이미지 폴더 경로
output_folder = 'augmented_images'  # 증강 후 이미지 저장할 폴더 경로

augment_images(input_folder, output_folder)
