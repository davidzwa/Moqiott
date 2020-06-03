import sys
import time
from datetime import datetime


def set_stdout_utf8():
    # Fix with export PYTHONIOENCODING=utf-8:surrogateescape
    # utils.set_stdout_utf8()
    # print("✓")
    # Test with: print("日本語 ✓")
    # sys.stdout = open(sys.stdout.fileno(), mode='w',
    #                   encoding='utf8', buffering=1)
    pass


def now_time():
    return str(datetime.now().strftime("%H:%M:%S"))


def logname_timestamp():
    return str(datetime.now().strftime("%Y_%m_%d_%A_%H_%M"))


def get_millis():
    milliseconds = int(round(time.time() * 1000))
    print(milliseconds)
