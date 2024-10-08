import settings as s
import cv2
import numpy as np
import os

max_frame = 100

def is_blurry(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < 50 # 확인 후 조정

def is_over_exposed(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return np.mean(gray) > 250 # 너무 밝을 때

def main():
    cnt = 1

    cap = cv2.VideoCapture(1)

    save_dir = f'{s.dir_path['Mac']['cam']}' # /Users/wyatt/Desktop/CD2_project/cam_frame/
    print(f'Set save directory : {save_dir}')
    os.makedirs(save_dir, exist_ok=True)  # 폴더가 없으면 생성

    if not cap.isOpened():
        print("<Failure> Unable to access the cam\n\n")
        exit()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:  # 프레임 촬영 실패
                print("<Failure> frame capture failed, retrying...\n")
                continue  # 프레임 캡처를 재시도

            if not is_blurry(frame) and not is_over_exposed(frame):  # 유효이미지 일때
                file_name = os.path.join(save_dir, f'valid_frame_{cnt}.{s.file_type[2]}')
                
                if os.path.exists(file_name):
                    print(f"<Save> Frame {cnt} saved to {file_name}\n")
                    cnt += 1
                    if os.path.exists(file_name):
                        print("exist same name, delete existing file")
                        os.remove(file_name)
                    cv2.imwrite(file_name, frame)
                else:  # 프레임 저장 실패
                    print(f"<Failure> saving frame ({file_name}) failed\n\n")

            if cnt >= max_frame: # 목표 프레임 수집완료
                print(f"<DONE> Maximum frame limit reached: {max_frame}\n")
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("<DONE> User manually terminated the program\n")
                break

    finally:
        cap.release() # 카메라 해제
        cv2.destroyAllWindows() # 모든 opencv 윈도우 종료
        print("<PROGRAM OFF> Image frame capture done\n\n")

if __name__ == "__main__":
    main()