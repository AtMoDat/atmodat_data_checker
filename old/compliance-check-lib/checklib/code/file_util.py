"""
file_util.py
============

Utilities for interrogating files (without reading them).

"""

import os

def _get_file_size(fpath):
    "Returns size of file (in bytes)."
    return os.path.getsize(fpath)


def _is_file_size_less_than(fpath, n):
    """
    Checks file size of `fpath` and returns True if its size is less than `n` MBs.

    :param fpath: file path [string]
    :param n: size in Mbytes [float]
    :return: boolean
    """
    n = float(n)
    size_in_mbs = _get_file_size(fpath) / (2.**20)

    if size_in_mbs <= n:
        return True

    return False


