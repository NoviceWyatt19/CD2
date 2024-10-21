import configuration as con
import cv2
import numpy as np
import os

max_frame = 100

def check_frame_blurriness(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < 50 # 확인 후 조정

def is_over_exposed(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return np.mean(gray) > 250 # 너무 밝을 때

def is_under_exposed(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return np.mean(gray) < 50  # 너무 어두울 때

def adjust_over_exposure(img):
    # 과다 노출된 이미지를 조정하기 위한 Gamma Correction
    gamma = 0.5  # 과다 노출 보정용 감마 값
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(img, table)

def adjust_under_exposure(img):
    # CLAHE를 이용한 저조도 보정
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

def main():
    cnt = 1
    cap = cv2.VideoCapture(1)

    save_dir = con.dir_path['Mac']['cam']  # /Users/wyatt/Desktop/CD2_project/cam_frame/
    print(f'Set save directory : {save_dir}')
    os.makedirs(save_dir, exist_ok=True)  # 폴더가 없으면 생성

    if not cap.isOpened():
        print("<Failure> Unable to access the cam\n\n")
        exit()

    try:
        while True:
            ret, frame = cap.read()
            cv2.imshow("Capture", frame)
            
            if not ret:  # 프레임 촬영 실패
                print("<Failure> frame capture failed, retrying...\n")
                continue  # 프레임 캡처 재시도

            if not check_frame_blurriness(frame):
                if is_over_exposed(frame):
                    frame = adjust_over_exposure(frame)  # over exposure 보정
                elif is_under_exposed(frame):
                    frame = adjust_under_exposure(frame)  # under exposure 보정
                
                file_name = os.path.join(save_dir, f'valid_frame_{cnt}.{con.file_type[2]}')
                
                if os.path.exists(file_name):
                    print(f"File with same name exists, deleting: {file_name}")
                    os.remove(file_name)

                cv2.imwrite(file_name, frame)
                print(f"<Save> Frame {cnt} saved to {file_name}\n")
                cnt += 1

            if cnt >= max_frame:  # 목표 프레임 수집 완료
                print(f"<DONE> Maximum frame limit reached: {max_frame}\n")
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("<DONE> User manually terminated the program\n")
                break

    finally:
        cap.release()  # 카메라 해제
        cv2.destroyAllWindows()  # 모든 OpenCV 윈도우 종료
        print("<PROGRAM OFF> Image frame capture done\n\n")

if __name__ == "__main__":
    main()