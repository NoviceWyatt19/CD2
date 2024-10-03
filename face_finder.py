from mtcnn.mtcnn import MTCNN
import cv2, time, os

detector = MTCNN()
img = cv2.imread('/Users/wyatt/Desktop/CD2_project/valid_frame_1.jpeg') # input img path or img name
result = detector.detect_faces(img)

detected = len(result) > 0

for person in result:
    bounding_box = person['box']
    cv2.rectangle(img,
                  (bounding_box[0], bounding_box[1]),
                  (bounding_box[0]+bounding_box[2], bounding_box[1] + bounding_box[3]),
                  (255, 0, 0), 2)

output_path = '/Users/wyatt/Desktop/CD2_project/detected_faces.jpg'
print("Checking if file exists:", output_path)

if os.path.exists(output_path):
    print("exist same name, delete existing file")
    os.remove(output_path)  # 파일이 존재하면 삭제
else:
    print("File does not exist.")

cv2.imwrite(output_path, img)

if detected:
    print("Success detecting!")
else:
    print("Fail")

# cv2.waitKey(0)  # 키 입력이 있을 때까지 대기
# cv2.destroyAllWindows()  # 모든 OpenCV 창 종료
time.sleep(2)