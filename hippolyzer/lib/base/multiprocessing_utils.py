import ctypes
import multiprocessing
import os
import sys
import time

SYNCHRONIZE = 0x100000


def _windows_pid_alive(pid: int):
    # https://stackoverflow.com/a/17645146
    # This is not quite right and https://stackoverflow.com/a/23409343 would
    # be better, but GetExitCodeProcess is always failing for me. Without
    # it we'll incorrectly treat a pid as alive for a few seconds after
    # it dies, but that's not a problem.
    kernel32 = ctypes.windll.kernel32
    process = kernel32.OpenProcess(SYNCHRONIZE, 0, pid)
    if process != 0:
        kernel32.CloseHandle(process)
        return True
    return False


class ParentProcessWatcher:
    def __init__(self, shutdown_signal: multiprocessing.Event):
        self._orig_ppid = os.getppid()
        self._win_last_pid_check = time.time()
        self._shutdown_signal = shutdown_signal

    def check_shutdown_needed(self) -> bool:
        if self._shutdown_signal.is_set():
            return True
        # Parent process died and we got reparented, set the shutdown signal
        # Even though we're a daemonized child process the parent doesn't get a chance
        # to kill us when it segfaults or gets a SIGKILL. prctl() is an option, but
        # *NIX-only. atexit() hooks also won't work here. Oh well.
        if os.getppid() != self._orig_ppid:
            self._shutdown_signal.set()
            return True
        # ppid won't change when parent dies on windows. have to do something worse.
        if sys.platform == "win32":
            # Only once per second, ctypes is slow.
            if self._win_last_pid_check + 1.0 < time.time():
                if not _windows_pid_alive(os.getppid()):
                    self._shutdown_signal.set()
                    return True
                self._win_last_pid_check = time.time()
        return False
