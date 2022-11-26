import time
import sys
import math
from concurrent.futures import ThreadPoolExecutor

def parallel_call(func):
    def eta_estimator(completed_percent, current_time):
        rem =  (100.0 * current_time)/ completed_percent -  current_time
        return rem

    def processor(*args, **kwargs):
        global count, st
        total = kwargs.get('total')
        # Before call
        func(*args, **kwargs)
        # After call
        count += 1
        et = time.perf_counter()
        lapsed_time = et-st
        completed = count/total
        eta = eta_estimator(completed * 100, lapsed_time)
        msg = f"\r[ STATUS ] Progress: {completed:0.2%} | Processed: {count}/{total} | Elapsed-time: {lapsed_time:0.2f}s | ETA: {eta:0.3f}s"
        sys.stdout.write(msg)
        sys.stdout.flush()

    def wrapper(*args, **kwargs):
        # Parallelize task...
        global count, st
        count = 0
        _data = kwargs.get('data')
        total = len(list(_data.values())[0])
        if not total:
            print("[  WARNING  ] Recieved empty list. Early termination...")
            return
        thread_limit = kwargs.get('thread_limit', 0)
        thread_count = (int(math.sqrt(total)) + 1) * int(math.log(total, 10)) if math.log(total, 10) >= 1 else 1
        thread = thread_count if kwargs.get('threads') < 1 else kwargs.get('threads')
        threads = min(4096, thread) if thread_limit == 0 else thread
        print('********************* MultiThreading Start *********************')
        print(f"[  INFO  ] Launching: {threads} threads...")
        # Check if all values have the same length, and raise exception if not...
        for key in _data:
            if total != len(_data[key]):
                raise "Dictionary values are inconsistent. All values must have the same length..."
        st = time.perf_counter()
        with ThreadPoolExecutor(threads) as exe:
            # Iterate over data...
            for i in range(total):
                data = {key: _data[key][i] for key in _data}
                exe.submit(processor, *args, data=data, total=total)
        print('\n********************* MultiThreading End *********************')
    return wrapper
