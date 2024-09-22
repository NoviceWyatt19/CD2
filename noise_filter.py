import cv2
import numpy as np

def is_blurry( img ):
    gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )
    laplacian_var = cv2.Laplacian( gray, cv2.CV_64F ).var()

    return laplacian_var < 100 # 확인 후 조정

def is_over_exposed( img ):
    gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )

    return np.mean( gray ) > 200 # 너무 밝을 때

file_type = ['jpeg', 'jpg', 'png']
cnt = 1
max_frame = 200

cap = cv2.VideoCapture( 0 )

if not cap.isOpened():
    print( "<Failure> Unable to access the cam\n\n" )
    exit()

try:

    while True:
        ret, frame = cap.read()
        if not ret: # 프레임 촬영 실패
            print( "<Failure> frame capture failed\n\n" )
            break

        if not is_blurry( frame ) and not is_over_exposed( frame ): # 유효이미지 일때
            file_name = f'valid_frame_{cnt}.{file_type[0]}'
            
            if cv2.imwrite( file_name, frame ):
                print( f"<Save> Frame {cnt} saved\n" )
                cnt += 1
            else: # 프레임 저장 실패
                print( f"<Failure> saving frame ({file_name}) failed\n\n" )

        if cnt <= max_frame: # 목표 프레임 수집완료
            print( f"<DONE> Maximum frame limit reached: {max_frame}\n" )
            break
        
        # if cnt % 10 == 0: # 10 프레임마다
        #     cv2.imshow("Frame", frame) # 시각화
        
        if cv2.waitKey( 1 ) & 0xFF == ord( 'q' ):
            print( "<DONE> User manually terminated the program\n")
            break

finally:
    cap.release() # 카메라 해제
    cv2.destroyAllWindows() # 모든 opencv 윈도우 종료
    print( "<PROGRAM OFF> Image frame capture done\n\n")
