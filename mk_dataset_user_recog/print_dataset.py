import os
import cv2

files = sorted(os.listdir('/Users/wyatt/Desktop/inst_CD2/detect_face_user'))


# 이미지 순회하며 확인
for file_name in files:
    # 전체 이미지 경로 생성
    img_path = os.path.join('/Users/wyatt/Desktop/inst_CD2/detect_face_user', file_name)

    # 이미지 읽기
    img = cv2.imread(img_path)
    if img is None:
        print(f"이미지를 불러올 수 없습니다: {img_path}")
        continue

    # 이미지 표시
    cv2.imshow('Image', img)
    print(f"이미지 확인 중: {img_path}")

    # 'q' 키를 누르면 다음 이미지로 넘어감
    key = cv2.waitKey(0)
    if key == ord('q'):
        cv2.destroyAllWindows()
        continue
    elif key == 27:  # ESC 키를 누르면 루프를 중단
        print("이미지 확인을 중단합니다.")
        break

# 모든 창 닫기
cv2.destroyAllWindows()