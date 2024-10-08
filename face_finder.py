from mtcnn.mtcnn import MTCNN
import settings as s
import cv2, os

def face_marker(cnt, d_type='img'):
    if d_type == 'img':
        cam_frame_path = f'{s.dir_path['Mac']['cam']}valid_frame_{cnt}.png'
        img = cv2.imread(cam_frame_path) # input img path or img name
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    elif d_type == 'webcam': # 아직 동작안됨
        img = cv2.VideoCapture(0)

    detector = MTCNN()
    
    print(f"Set path : {cam_frame_path}")
    
    result = detector.detect_faces(img_rgb)
    detected = len(result) > 0

    if detected:
        
        for person in result: # mark on the frame
            bounding_box = person['box']
            cv2.rectangle(img,
                    (bounding_box[0], bounding_box[1]),
                    (bounding_box[0]+bounding_box[2], bounding_box[1] + bounding_box[3]),
                    (0, 0, 255), 2)
            
        print("Success detecting!")
        # outpath를 while 또는 for문을 통해 cam_frame에 저장된 사진을 모두 돌게 만들면 됨
        # 이후 실시간 캠을 인식하도록 해서 눈감기 탐지 코드에도 활용할 계획
        output_path = f'{s.dir_path['Mac']['mctnn']}detected_faces_{cnt}.png'
        print("Checking if file exists:", output_path)

        if os.path.exists(output_path):
            print("exist same name, delete existing file")
            os.remove(output_path)  # 파일이 존재하면 삭제
        else:
            print("File does not exist. -> Just Save")

        cv2.imwrite(output_path, img)
    else:
        print("Fail")

if __name__ == "__main__":
    try:
        cnt =1
        while cnt <= 200:
            face_marker(cnt)
            cnt += 1
    except Exception as e:
        print(f"An error occurred: {e}")

# cv2.waitKey(0)  # 키 입력이 있을 때까지 대기
# cv2.destroyAllWindows()  # 모든 OpenCV 창 종료
