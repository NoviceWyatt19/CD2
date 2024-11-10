from mtcnn import MTCNN
import cv2

# MTCNN 초기화
detector_mtcnn = MTCNN()

def process_image_mtcnn(image):
    frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = detector_mtcnn.detect_faces(frame_rgb)
    
    for result in results:
        x, y, width, height = result['box']
        cv2.rectangle(image, (x, y), (x + width, y + height), (0, 255, 0), 2)
    
    return image, results