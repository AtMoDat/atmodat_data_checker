"""module output_directory.py to create output directory"""

import os
import shutil


def create_directories(opath, check_types):
    # Create directory to store output from checker if it does not exist already
    if not os.path.isdir(opath):
        os.makedirs(opath)
    else:
        shutil.rmtree(opath + '/')
        os.makedirs(opath)
    for check in check_types:
        os.makedirs(opath + '/' + check)


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
