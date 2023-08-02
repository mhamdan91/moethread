import os, shutil, sys, time
sys.path.append('.')
from moecolor import print
from moethread import parallel_call, progress
from glob import glob
from pathlib import Path

top_dir = 'unittest'
src, dst = 'src', 'dst'
dst_dir = Path(os.path.join(top_dir, dst))
dst_dir.mkdir(exist_ok=True, parents=True)
data = glob(os.path.join(top_dir, src, '*.*'))
# Replicate data...
for i in range(10):
    data += data

@parallel_call
def copy_data(**kwargs):
    src_path = kwargs.get('data', {}).get('path', '')
    dst_path = src_path.replace(src, dst)
    shutil.copyfile(src_path, dst_path)

data_dict = {'path': data}
copy_data(data=data_dict, threads=1)

st = time.perf_counter()
total = len(data)
for i, file_path in enumerate(data):
    shutil.copy(file_path, file_path.replace(src, dst))
    print(progress(i+1, total, st, True), color='magenta', end='\r')