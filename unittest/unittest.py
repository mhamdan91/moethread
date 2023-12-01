import os, shutil, sys, time, random
sys.path.append('.')
from moecolor import print
from moethread import parallel_call, progress, mtdo
from glob import glob
from pathlib import Path

top_dir = 'unittest'
curdir = os.path.dirname(os.path.abspath(__file__))
src, dst = os.path.join(curdir, 'src'), os.path.join(curdir, 'dst')
delay = 0
dst_dir = Path(os.path.join(top_dir, dst))
dst_dir.mkdir(exist_ok=True, parents=True)
data = glob(os.path.join(top_dir, src, '*.*'))
# Replicate data...
for i in range(10):
    data += data

@parallel_call
def copy_data(**kwargs):
    if delay:
        time.sleep(random.randint(delay//10, delay*2)/delay)
    src_path = kwargs.get('data', {}).get('path', '')
    dst_path = src_path.replace(src, dst)
    shutil.copyfile(src_path, dst_path)

data_dict = {'path': data}
copy_data(data=data_dict, threads=16)


mtdo(src, dst, action='cp', prefix='tester', sep_folder='unittest', overwrite=True)

print("*********************   Sequential Copy  *********************", color="blue")
st = time.perf_counter()
total = len(data)
for i, file_path in enumerate(data):
    shutil.copy(file_path, file_path.replace(src, dst))
    print(progress(i+1, total, st, True), color='lime', end='\r')