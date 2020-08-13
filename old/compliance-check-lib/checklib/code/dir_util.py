"""
dir_util.py
===========

Utilities for interrogating collections of files based on a single directory
that gets scanned for its contents.

"""

import os

def get_files_in_dir(dr):
    """
    Returns paths to all the files under directory `dr`.

    :param dr: directory path [string]
    :return: list of file paths
    """
    files = []

    for root, dirs, files in os.walk(dr):
        for filename in files:
            files.append(os.path.join(root, filename))
    return files


def has_too_many_files(dr, n):
    """
    Returns True if more files in `dr` than threshold `n`.

    :param dr: directory [string]
    :param n:  threshold for number of files in directory [integer]
    :return: boolean
    """
    if len(get_files_in_dir(dr)) > n:
        return True
    return False
