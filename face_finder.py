from mtcnn.mtcnn import MTCNN
import cv2

detector = MTCNN()
img = cv2.imread('image.jpg') # input img path or img name
result = detector.detect_faces(img)

for person in result:
    bounding_box = person['box']
    cv2.rectangle(img,
                  (bounding_box[0], bounding_box[1]),
                  (bounding_box[0]+bounding_box[2], bounding_box[1] + bounding_box[3]),
                  (255, 0, 0), 2)
    
cv2.imshow('img', img)
cv2.waitKey()