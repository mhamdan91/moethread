import os, shutil, sys, time, random
sys.path.append('.')
from moecolor import print
from moethread import parallel_call, progress, mtdo, mtdo_from_json, mtdo_from_csv
from glob import glob
from pathlib import Path

top_dir = 'unittest'
curdir = os.path.dirname(os.path.abspath(__file__))
src, dst = os.path.join(curdir, 'src1'), os.path.join(curdir, 'dst')
delay = 0
dst_dir = Path(os.path.join(top_dir, dst))
dst_dir.mkdir(exist_ok=True, parents=True)
data = glob(os.path.join(top_dir, src, '*.*'))

replicate = False

if replicate:
    # Replicate data...
    for i in range(15):
        data += data


# mtdo_from_csv(os.path.join(curdir, "files", "data.csv"), os.path.join(curdir, "files", "csv_out"), 'IMG_URL', 'class_name')

# mtdo_from_json(os.path.join(curdir, "files", "data.json"), os.path.join(curdir, "files", "json_out"), 'IMG_URL', 'class_name', chunk_size=250)


mtdo(src, dst, op='rm', file_type='*.jpg', overwrite=True, threads=4)

# @parallel_call
# def copy_data(**kwargs):
#     if delay:
#         time.sleep(random.randint(delay//10, delay*2)/delay)
#     src_path = kwargs.get('data', {}).get('path', '')
#     dst_path = src_path.replace(src, dst)
#     shutil.copyfile(src_path, dst_path)

# data_dict = {'path': data}
# copy_data(data=data_dict, threads=16)

# print("*********************   Sequential Copy  *********************", color="blue")
# st = time.perf_counter()
# total = len(data)
# for i, file_path in enumerate(data):
#     filename = os.path.splitext(file_path.split(os.sep)[-1])[0]
#     shutil.copy(file_path, file_path.replace(src, dst))
#     print(progress(i+1, total, st, True), color='lime', end='\r')


# print("*********************   dup Sequential Copy  *********************", color="blue")
# st = time.perf_counter()
# total = len(data)
# for i, file_path in enumerate(data):
#     filename = os.path.splitext(file_path.split(os.sep)[-1])[0]
#     shutil.copy(file_path, file_path.replace(src, dst).replace(filename, f'{filename}_{i}'))
#     print(progress(i+1, total, st, True), color='lime', end='\r')