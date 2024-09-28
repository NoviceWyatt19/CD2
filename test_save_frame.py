import os
import cv2

# 저장할 폴더 경로 설정
save_dir = '/Users/wyatt/Desktop/CD2_project/cam_frame'
os.makedirs(save_dir, exist_ok=True)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("<Failure> Unable to access the cam\n")
    exit()

cnt = 1
max_frame = 200

try:
    while cnt <= max_frame:
        ret, frame = cap.read()
        if not ret:  # 프레임 촬영 실패
            print("<Failure> frame capture failed\n")
            break
        
        # 모든 프레임 저장 (유효성 검사 임시 제거)
        file_name = os.path.join(save_dir, f'frame_{cnt}.jpg')
        if cv2.imwrite(file_name, frame):
            print(f"<Save> Frame {cnt} saved to {file_name}\n")
            cnt += 1
        else:
            print(f"<Failure> saving frame ({file_name}) failed\n")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("<DONE> User manually terminated the program\n")
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("<PROGRAM OFF> Image frame capture done\n")