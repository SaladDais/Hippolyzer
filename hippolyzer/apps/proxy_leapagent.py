"""
Stub for forwarding LEAP stdin/stdout to hippolyzer over TCP using netcat.

To be replaced with a nicer thing later.

Really not much use to anyone but me until viewers correctly un-gate LEAP access :)
Hint: uncomment https://vcs.firestormviewer.org/phoenix-firestorm/files/cf85e854/indra/newview/llappviewer.cpp#L1398-1420

Usage: While hippolyzer-leapreceiver is running
  ./firestorm --leap hippolyzer-leapagent
"""
import multiprocessing
import os
import shutil


def agent_main():
    nc_exe = None
    for possible_cat in ["nc", "ncat", "netcat"]:
        if cat_path := shutil.which(possible_cat):
            nc_exe = cat_path

    if not nc_exe:
        raise ValueError("Couldn't find an acceptable netcat in PATH!")

    os.execv(nc_exe, [nc_exe, "127.0.0.1", "9063"])


if __name__ == "__main__":
    multiprocessing.freeze_support()
    agent_main()
