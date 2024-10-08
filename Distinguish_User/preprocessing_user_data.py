# for N in {1..4}; do \
# python src/align/align_dataset_mtcnn.py \
# ~/datasets/lfw/raw \
# ~/datasets/lfw/lfw_mtcnnpy_160 \
# --image_size 160 \
# --margin 32 \
# --random_order \
# --gpu_memory_fraction 0.25 \
# & done

from facenet.src import facenet, align
import settings as s

input_dir = s.dir_path['Mac']['preprocessing']
output_dir = s.dir_path['Mac']['comp_db']

image_size = 160
margin = 32
random_order = True
gpu_memory_fraction = 0.25

# MTCNN으로 얼굴 정렬 및 정제
align.align_dataset_mtcnn(
    input_dir, 
    output_dir, 
    image_size, 
    margin, 
    random_order, 
    gpu_memory_fraction
    )

