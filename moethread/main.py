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

import time
import sys, os
import math, shutil
from pathlib import Path
from glob import glob
from moecolor import print
from moecolor import FormatText as ft
from concurrent.futures import ThreadPoolExecutor

GLOBAL_COUNT = 0

def func_status(func):
    def _wrapper(*args, **kwargs):
        print('********************* MultiThreading Start *********************', color='#FFFF99')
        result = func(*args, **kwargs)
        print('********************* MultiThreading End *********************', color='#FFFF99')
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
        global count, st, GLOBAL_COUNT
        try:
            count = 0
            _data = kwargs.get('data')
            if not _data:
                print("[  WARN  ] Recieved empty list or invalid argument. Make sure to "\
                      "provide data as a kwarg [data=your_data_dict]. Early termination...", color='orange')
                return
            total = len(list(_data.values())[0])
            _threads = kwargs.get('threads', -1) or kwargs.get('thread', -1)
            thread_limit = kwargs.get('thread_limit', 0)
            thread_count = (int(math.sqrt(total)) + 1) * int(math.log(total, 10)) if math.log(total, 10) >= 1 else 1
            thread = thread_count if _threads < 1 else _threads
            threads = min(4096, thread) if thread_limit == 0 else thread
            print(f"[  INFO  ] Launching: {threads} threads...", color='blue')
            # Check if all values have the same length, and raise exception if not...
            for key in _data:
                if total != len(_data[key]):
                    raise Exception("Dictionary values are inconsistent. All values must have the same length...")
                st = time.perf_counter()
            with ThreadPoolExecutor(threads) as exe:
                # Iterate over data...
                for i in range(total):
                    data = {key: list(_data[key])[i] for key in _data}
                    exe.submit(processor, *args, data=data, total=total)
        except Exception as e:
            print(f"[ ERROR ] {e}.", color='red')
            return
        # Reset count after completing job...
        GLOBAL_COUNT = 0
    return wrapper

def mtdo(src_dir: str, dst_dir: str='', action: str='cp', create_dst_dir: str=False,
         file_type: str='*.*', sep_folder: str='', overwrite: bool=False,
         prefix: str='', threads: int=64) -> None:
    """Performs a multithreaded data operation.

    Args:
        src_dir (str): source directory containing data to copy.
        dst_dir (str): destination directory to copy data to.
        action (str): transfer type [cp: copy, mv: move, del: delete, ren: rename].
        create_dst_dir (str): force the creation of destination directory if it does not exist.
        file_type (str, optional): type of data to copy, e.g '*.json' - copies json files only. Defaults to all data types '*.*'.
        sep_folder (str, optional): separation folder where right side directory structure is appended to destination directory,
                                    e.g. app/data/src/files, sep_folder='data', dest path -> os.path.join(dest_dir, 'src/files'). Defaults to ''.
        overwrite (bool, optional): whether to overwrite data in destination or skip already copied data on later trials. Defaults to False.
        prefix (str): prefix for image renaming, e.g prefix=data and image_name=im.jpg --> data_im.jpg
    """
    invalid_color = 'red'
    action = action.lower()
    rename_action = ['ren', 'rename']
    move_action = ['mv', 'move']
    delete_action = ['del', 'delete', 'remove']
    copy_action =  ['cp', 'copy']
    if create_dst_dir:
        _dd = Path(dst_dir)
        _dd.mkdir(exist_ok=True, parents=True)
    valid_actions = rename_action + move_action + delete_action + copy_action
    if not os.path.isdir(src_dir):
        print(f"[ INVALID ] source directory does not exist. Set `create_dst_dir` if you wish to force create destination directory", color=invalid_color)
        return
    if action in (move_action + copy_action + rename_action) and not os.path.isdir(dst_dir):
        if not dst_dir:
            print(f"[ INVALID ] action [{action}] requires a valid destination directory.", color=invalid_color)
        else:
            print(f"[ INVALID ] destination directory does not exist.", color=invalid_color)
        return
    if action not in valid_actions:
        print(f"[ INVALID ] received invalid action [{action}], choose from [mv (to move), cp (to copy), ren (to rename), del (to delete)].", color=invalid_color)
        return
    if not prefix and action in rename_action:
        print(f"[ INVALID ] rename action [{action}] requires `prefix` to be provided.", color=invalid_color)
        return
    data_paths = glob(os.path.join(src_dir, '**', file_type), recursive=True)
    if not data_paths:
        print(f"[ WARNING ] did not find any valid files of type [{file_type}] in source directory.", color='orange')
        return
    if sep_folder and sep_folder not in data_paths[0].split(os.sep):
        print(f"[ WARNING ] separation folder [{sep_folder}] does not exist in destination directory " \
              f"structure [{f'{os.sep}'.join(data_paths[0].split(os.sep)[:-1])}].", color='orange')
        print(f"[ WARNING ] will place data directly under [{dst_dir}]", color='orange')
        sep_folder = ''
    if not overwrite:
        dst_data_paths = glob(os.path.join(dst_dir, '**', file_type), recursive=True)
        dst_data = [_.split(os.sep)[-1] for _ in dst_data_paths]
        data_paths = [_ for _ in data_paths if _.split(os.sep)[-1] not in dst_data]
        if not data_paths:
            print(f"[ INFO ] data in source directory already exist in destination directory, nothing to do here.", color='yellow')
            return
    @parallel_call
    def _copy_images(**kwargs):
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
        if action in (move_action + rename_action):
            shutil.move(data_path, os.path.join(_dst_dir, filename))
        elif action in delete_action:
            os.remove(data_path)
        else:
            shutil.copyfile(data_path, os.path.join(_dst_dir, filename))
    _copy_images(data={'data_path': data_paths}, threads=1)