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
import sys
import math
from moecolor import print
from moecolor import FormatText as ft
from concurrent.futures import ThreadPoolExecutor

def func_status(func):
    def _wrapper(*args, **kwargs):
        print('********************* MultiThreading Start *********************', color='#FFFF99')
        result = func(*args, **kwargs)
        print('********************* MultiThreading End *********************', color='#FFFF99')
        return result
    return _wrapper

def progress(count, total, st, return_str=False):
        elapsed_time = time.perf_counter() - st
        completed = count / total
        completed_percent = completed * 100
        eta = (100.0 * elapsed_time)/ completed_percent -  elapsed_time
        tmp = elapsed_time/count
        if tmp < 0.001:
            latency = f"{1000000*tmp:0.2f} us/item"
        elif tmp < 1:
            latency = f"{1000*tmp:0.2f} ms/item"
        else:
            latency = f"{tmp:0.2f} s/item"
        msg = f"\r[ STATUS ] Progress: {completed:0.2%} | Processed: {count}/{total} | " \
              f"Elapsed-time: {elapsed_time:0.2f}s | ETA: {eta:0.3f}s ~ " \
              f"{round(count/elapsed_time)} items/s @ {latency}"
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
        try:
            global count, st
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
    return wrapper
