import os
from scripts import login_platzi, download_course, download_class
from download import download_by_m3u8
from constants import EXEC_MODES, VALID_EXEC_MODES

def get_argvs():
    argvs = os.sys.argv
    exec_mode = None
    if len(argvs) > 1:
        exec_mode = argvs[1]
        if exec_mode not in EXEC_MODES:
            raise ValueError(f"Invalid execution mode - use {VALID_EXEC_MODES}")
    parameter = argvs[2] if len(argvs) > 2 else None
    return exec_mode, parameter

if __name__ == "__main__":
    [exec_mode, parameter] = get_argvs()

    if exec_mode == "login":
        login_platzi()
    elif exec_mode == "download-course":
        download_course(parameter)
    elif exec_mode == "download-class":
        download_class(parameter)
    elif exec_mode == "m3u8":
        download_by_m3u8(parameter)