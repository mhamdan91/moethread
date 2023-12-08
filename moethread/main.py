# @mhamdan
# MIT License

# Copyright (c) 2022 Muhammad Hamdan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time, os, sys
import csv, json
import math, shutil
from copy import deepcopy
from itertools import islice
from typing import Dict, List
from pathlib import Path
from glob import glob
from moecolor import print
from moecolor import FormatText as ft
from concurrent.futures import ThreadPoolExecutor

GLOBAL_COUNT = 0
STDOUT = None

################## HELPER FUNCTIONS START... ##################
def _chunk_dict(in_dict: Dict, size: int=5000):
    it = iter(in_dict.items())
    chunks = [{k:v for k, v in islice(it, size)} for _ in range((len(in_dict) + size - 1) // size)]
    return chunks

def _chunk_list(in_list, size: int=5000):
    return [in_list[i:i + size] for i in range(0, len(in_list), size)]

def _chunk_data(data: Dict, size: int, chunked_data: List=[]):
    chunked_dict = {}
    for k, v in data.items():
        chunked_dict[k] = _chunk_list(v, size)
    num_chunks = len(list(chunked_dict.values())[0])
    for i in range(num_chunks):
        tmp_dict = {}
        for k, v in chunked_dict.items():
            tmp_dict[k] = v[i]
        chunked_data.append(deepcopy(tmp_dict))
    del chunked_dict
    return chunked_data

def _csv_to_dict(csv_file):
    data: Dict[str, List] = {}
    with open(csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for key, value in row.items():
                keys = key.split('\t')
                values = value.split('\t')
                for k, v in zip(keys, values):
                    if k not in data:
                        data[k] = []
                    data[k].append(v)
    return data

################## HELPER FUNCTIONS END.... ##################


def func_status(func):
    def _wrapper(*args, **kwargs):
        global STDOUT, GLOBAL_COUNT
        _verbose = kwargs.get('verbose')
        if _verbose is not None and _verbose in [0, -1, False, 'false']:
            STDOUT = sys.stdout
            sys.stdout = None
        print('********************* MultiThreading Start *********************', color='#FFFF99')
        result = func(*args, **kwargs)
        print('********************* MultiThreading End *********************', color='#FFFF99')
        # Reset some globals after completing job...
        GLOBAL_COUNT = 0
        if STDOUT is not None:
            sys.stdout = STDOUT
        return result
    return _wrapper

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        _time = f"{int(hours):02d}:{int(minutes):02d}:{seconds:0.2f}"
    elif minutes > 0:
        _time = f"{int(minutes):02d}:{seconds:0.2f}"
    else:
        _time = f"{seconds:0.3f}s"
    return _time

def format_latency(tmp):
    if tmp < 0.001:
        latency = f"{1e6*tmp:0.2f} us/item"
    elif tmp < 1:
        latency = f"{1e3*tmp:0.2f} ms/item"
    else:
        latency = f"{tmp:0.2f} s/item"
    return latency

def progress(count, total, st, return_str=False):
        # This is like mutex...
        global GLOBAL_COUNT
        if count < GLOBAL_COUNT:
            return
        GLOBAL_COUNT = count
        elapsed_time = time.perf_counter() - st
        completed = count / total
        completed_percent = completed * 100
        eta = (100.0 * elapsed_time)/ completed_percent -  elapsed_time
        latency = format_latency(elapsed_time/count)
        eta_str = f'ETA: {format_time(eta)}'
        elt_str = f'Elapsed-time: {format_time(elapsed_time)}'
        msg = f"\r[ STATUS ] Progress: {completed:0.2%} | Processed: {count}/{total} | " \
              f"{elt_str} | {eta_str} ~ {count/elapsed_time:0.1f} items/s @ {latency}"
        if return_str:
            return msg
        else:
            sys.stdout.write(ft(msg, color='lime').text)
            sys.stdout.flush()
            if count >= total:
                print("") # Needed after completing job...

def parallel_call(func):
    def processor(*args, **kwargs):
        global count, st
        total = kwargs.get('total')
        # Before call
        func(*args, **kwargs)
        # After call
        count += 1
        progress(count, total, st)

    @func_status
    def wrapper(*args, **kwargs):
        # Parallelize task...
        global count, st
        try:
            count = 0
            _data: Dict = kwargs.get('data')
            if not _data:
                print("[  WARN  ] Recieved empty list or invalid argument. Make sure to "\
                      "provide data as a kwarg [data=your_data_dict]. Early termination...", color='orange')
                return
            total = len(list(_data.values())[0])
            _chunk_size = kwargs.get('chunk_size', min(5000, total))
            # Check if all values have the same length, and raise exception if not...
            for key in _data:
                if total != len(_data[key]):
                    raise Exception("Dictionary values are inconsistent. All values must have the same length...")
            # End of prechecks...
            _data = _chunk_data(_data, _chunk_size)
            _threads = kwargs.get('threads', -1) or kwargs.get('thread', -1)
            thread_limit = kwargs.get('thread_limit', 0)
            thread_count = (int(math.sqrt(total)) + 1) * int(math.log(total, 10)) if math.log(total, 10) >= 1 else 1
            thread = thread_count if _threads < 1 else _threads
            threads = min(4096, thread) if thread_limit == 0 else thread
            print(f"[  INFO  ] Launching: {threads} threads...", color='blue')
            st = time.perf_counter()
            for chunk in _data:
                chunk_size = len(list(chunk.values())[0])
                with ThreadPoolExecutor(threads) as exe:
                    # Iterate over data...
                    for i in range(chunk_size):
                        data = {key: list(chunk[key])[i] for key in chunk}
                        exe.submit(processor, *args, data=data, total=total)
        except Exception as e:
            print(f"[  ERROR  ] {e}.", color='red')
            return
    return wrapper



################## READY TO GO FUNCTIONS START... ##################
def mtdo(src_dir: str, dst_dir: str='', op: str='cp', file_type: str='*.*',
         sep_folder: str='', overwrite: bool=False, prefix: str='', threads:int=8, **kwargs) -> None:
    """Performs a multithreaded data operation.

    Args:
        src_dir (str): source directory containing data to copy.
        dst_dir (str): destination directory to copy data to.
        op (str): operation type [cp: copy, mv: move, rm: delete, ren: rename].
        file_type (str, optional): type of data to copy, e.g '*.json' - copies json files only. Defaults to all data types '*.*'.
        sep_folder (str, optional): separation folder where right side directory structure is appended to destination directory,
                                    e.g. app/data/src/files, sep_folder='data', dest path -> os.path.join(dest_dir, 'src/files'). Defaults to ''.
        overwrite (bool, optional): whether to overwrite data in destination or skip already copied data on later trials. Defaults to False.
        prefix (str): prefix for image renaming, e.g prefix=data and image_name=im.jpg --> data_im.jpg
        threads (int, optional): number of threads to launch. Defaults to 8.
    """
    error_color = 'red'
    op = op.lower()
    rename_op = ['ren', 'rename']
    move_op = ['mv', 'move']
    delete_op = ['del', 'delete', 'remove', 'rm']
    copy_op =  ['cp', 'copy']
    _dd = Path(dst_dir)
    _dd.mkdir(exist_ok=True, parents=True)
    valid_ops = rename_op + move_op + delete_op + copy_op
    if op in (move_op + copy_op + rename_op) and not os.path.isdir(dst_dir):
        if not dst_dir:
            print(f"[  ERROR  ] op [{op}] requires a valid destination directory.", color=error_color)
        else:
            print(f"[  ERROR  ] destination directory does not exist.", color=error_color)
        return
    if op not in valid_ops:
        print(f"[  ERROR  ] received invalid op [{op}], choose from [mv (to move), cp (to copy), ren (to rename), rm (to delete)].", color=error_color)
        return
    if not prefix and op in rename_op:
        print(f"[  ERROR  ] rename op [{op}] requires `prefix` to be provided.", color=error_color)
        return

    data_paths = glob(os.path.join(src_dir, '**', file_type), recursive=True)
    if not data_paths:
        print(f"[  WARN  ] did not find any valid files of type [{file_type}] in source directory.", color='orange')
        return
    if sep_folder and sep_folder not in data_paths[0].split(os.sep):
        print(f"[  WARN  ] separation folder [{sep_folder}] does not exist in destination directory " \
              f"structure [{f'{os.sep}'.join(data_paths[0].split(os.sep)[:-1])}].", color='orange')
        print(f"[  WARN  ] will place data directly under [{dst_dir}]", color='orange')
        sep_folder = ''
    if not overwrite:
        dst_data_paths = glob(os.path.join(dst_dir, '**', file_type), recursive=True)
        dst_data = [_.split(os.sep)[-1] for _ in dst_data_paths]
        data_paths = [_ for _ in data_paths if _.split(os.sep)[-1] not in dst_data]
        if not data_paths:
            print(f"[  INFO  ] data in source directory already exist in " \
                  f"destination directory, nothing to do here.", color='blue')
            return

    @parallel_call
    def _process_data(**kwargs):
        data_path: str = kwargs.get('data', {}).get('data_path', '')
        if sep_folder:
            tmp = data_path.split(sep_folder)[-1].split(os.sep)
            dst_folders, filename = tmp[1:-1], tmp[-1]
            _dst_dir = Path(os.path.join(dst_dir, *dst_folders))
        else:
            filename = data_path.split(os.sep)[-1]
            _dst_dir = Path(dst_dir)
        _dst_dir.mkdir(parents=True, exist_ok=True)
        if prefix:
            filename = f'{prefix}_{filename}'
        if op in (move_op + rename_op):
            shutil.move(data_path, os.path.join(_dst_dir, filename))
        elif op in delete_op:
            os.remove(data_path)
        else:
            shutil.copyfile(data_path, os.path.join(_dst_dir, filename))
    _process_data(data={'data_path': data_paths}, threads=threads, **kwargs)

def mtdo_from_json(file_path: str, dst_dir: str, data_key: str,
                   label_key: str='', op:str='cp', threads:int=8, **kwargs):
    """Performs a multithreaded data operation for paths in json file.

    Args:
        file_path (str): input json file containing paths
        data_key (str): dictionary key holding file paths
        label_key (str): (optional) dictionary key holding labels for folders name to copy/move data to (classifying copied/moved data based on labels)
        op (str): operation type [cp: copy, mv: move].
        threads (int, optional): number of threads to launch. Defaults to 8.
        **kwargs: Extra keywords such as (chunk_size: split data into equal sized chunks, verbose: supress moethread stdout), defaults to (chunk_size=5000, verbose=True)
    """
    _mtdo_from_file(file_path, dst_dir, data_key, label_key, op, file_type='json', threads=threads, **kwargs)

def mtdo_from_csv(file_path: str, dst_dir: str, data_key: str,
                  label_key: str='', op:str='cp', threads:int=8, **kwargs):
    """Performs a multithreaded data operation for paths in csv file.

    Args:
        file_path (str): input json file containing paths
        data_key (str): dictionary key holding file paths
        label_key (str): (optional) dictionary key holding labels for folders name to copy/move data to (classifying copied/moved data based on labels)
        op (str): operation type [cp: copy, mv: move].
        threads (int, optional): number of threads to launch. Defaults to 8.
        **kwargs: Extra keywords such as (chunk_size: split data into equal sized chunks, verbose: supress moethread stdout), defaults to (chunk_size=5000, verbose=True)
    """
    _mtdo_from_file(file_path, dst_dir, data_key, label_key, op, file_type='csv', threads=threads, **kwargs)

def _mtdo_from_file(file_path: str, dst_dir: str, data_key: str, label_key: str='',
                    op:str='cp', file_type: str='json', threads:int=8, **kwargs):
    """Performs a multithreaded data operation on data in file

    Args:
        file_path (str): file path
        dst_dir (str): destination directory where to dump data to
        data_key (str): Key/identifier of data path in file
        label_key (str, optional): Labels/subfolder classes key of data path in file. Defaults to ''.
        op (str, optional): operation to carry on [copy `cp` or move `mv`]. Defaults to 'cp'.
        file_type (str, optional): Type of file to process [json or csv]. Defaults to 'json'.
        threads (int, optional): number of threads to launch. Defaults to 8.
        **kwargs: Extra keywords such as (chunk_size: split data into equal sized chunks, verbose: supress moethread stdout), defaults to (chunk_size=5000, verbose=True)
    """
    error_color = 'red'
    _dst_dir = Path(dst_dir)
    _dst_dir.mkdir(parents=True, exist_ok=True)
    filename = file_path.split(os.sep)[-1]
    if os.path.splitext(filename)[-1].lower().replace('.', '') != file_type:
        print(f"[  ERROR  ] expected `*.{file_type}` file, but invalid " \
              f"file type provided [{filename}].", color=error_color)
        return
    if not os.path.exists(file_path):
        print(f"[  ERROR  ] provided file [{filename}] does not exist.", color=error_color)
        return
    st = time.perf_counter()
    print("[  INFO  ] Reading data from file, please wait...", color='blue')
    if file_type == 'json':
        with open(file_path) as f:
            data = json.load(f)
    else:
        data = _csv_to_dict(file_path)
    et = time.perf_counter()
    print(f"[  INFO  ] Finished reading data in {et-st:0.2f} seconds...", color='blue')

    valid_ops = ['cp', 'copy', 'mv', 'move']
    if op not in valid_ops:
        print(f"[  ERROR  ] received invalid op [{op}], choose from [mv (to move), " \
              f"cp (to copy), ren (to rename), rm (to delete)].", color=error_color)
        return

    @parallel_call
    def _process_data(**kwargs):
        url_idn = 'location='
        subfolder: str = kwargs.get('data', {}).get('label', 'unclassified')
        _path: str = kwargs.get('data', {}).get('path')
        if url_idn in _path:
            _path = _path.split(url_idn)[-1].split("&")[0]
        filename = _path.split(os.sep)[-1]
        if filename:
            dst_folder = Path(os.path.join(_dst_dir, subfolder))
            dst_folder.mkdir(parents=True, exist_ok=True)
        if op in ['mv', 'move']:
            shutil.move(_path, os.path.join(dst_folder, filename))
        else:
            shutil.copyfile(_path, os.path.join(dst_folder, filename))

    keys = list(data.keys())
    if data_key not in keys:
        print(f"[  ERROR  ] Data_Key [{data_key}] does not exist in keys [{keys}]", color=error_color)
        return
    if label_key and label_key not in keys:
        print(f"[  ERROR  ] Label_Key [{label_key}] does not exist in keys [{keys}]", color=error_color)
        return

    data_paths = data[data_key]
    if label_key:
        labels = data[label_key]
        _process_data(data={'path': data_paths, 'label': labels}, threads=threads, **kwargs)
    else:
        _process_data(data={'path': data_paths}, threads=threads, **kwargs)
################## READY TO GO FUNCTIONS END.... ##################
