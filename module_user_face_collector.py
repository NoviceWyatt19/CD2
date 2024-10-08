import face_finder as ff
import noise_filter as nf
import time

cnt = 1
nf.max_frame = 200

# take a picture
try:
    nf.main()
    while cnt <= nf.max_frame:
        ff.face_marker(cnt) # d_type : img, webcam
        cnt += 1
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    time.sleep(2)

# frame preprocessing
