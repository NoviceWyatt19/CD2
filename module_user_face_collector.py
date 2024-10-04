import face_finder as ff
import noise_filter as nf
import time

cnt = 1
nf.max_frame = 200

try:
    nf.main
except Exception as e:
    print(f"An error occurred: {e}")

try:    
    while cnt <= nf.max_frame:
        ff.face_marker(cnt)
        cnt += 1
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    time.sleep(2)
