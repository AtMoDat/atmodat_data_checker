"""module to create output directory"""

import os
from datetime import datetime
from pathlib import Path

global opath, opath_base

# Get current date and time
now = datetime.now()
now_formatted = now.strftime("%Y%m%d_%H%M") + '/'

# Get parent of parent directory of current file
opath_base = str(Path(__file__).resolve().parents[2])

# Define output path for result files
if opath_base:
    opath = opath_base + '/checker_output/' + now_formatted
else:
    opath = 'checker_output/' + now_formatted


def return_files_in_directory_tree(input_path):
    """return all files in directory tree"""
    file_names = []
    for root, d_names, f_names in os.walk(input_path):
        for f in f_names:
            file_names.append(os.path.join(root, f))

    return file_names


def create_directories():
    # Types of checks to be performed
    check_types = ["mandatory", "recommended", "optional", "CF"]
    # Create directory to store output from checker if it does not exist already
    if not os.path.isdir(opath):
        os.system('mkdir -p ' + opath)
        for check in check_types:
            os.system('mkdir -p ' + opath + '/' + check)
