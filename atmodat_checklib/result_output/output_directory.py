"""module output_directory.py to create output directory"""

import os
from datetime import datetime


def create_directories(opath, check_types):
    opath = os.path.join(opath, datetime.now().strftime("%Y%m%d_%H%M"), "")
    # Create directory to store output from checker if it does not exist already
    if not os.path.isdir(opath):
        os.makedirs(opath)
    for check in check_types:
        check_dir = opath + check
        if not os.path.isdir(check_dir):
            os.makedirs(check_dir)
    return opath


def return_files_in_directory_tree(input_path):
    """return all files in directory tree"""
    file_names = []
    for root, d_names, f_names in os.walk(input_path):
        for f in f_names:
            file_names.append(os.path.join(root, f))
    if not file_names:
        raise RuntimeError('Given direcotry contains no netCDF files')

    return file_names


def return_files_in_directory(input_path):
    """return all files in directory tree"""
    file_names = []
    for f_names in os.listdir(input_path):
        file_names.append(os.path.join(input_path, f_names))
    if not file_names:
        raise RuntimeError('Given direcotry contains no netCDF files')

    return file_names
