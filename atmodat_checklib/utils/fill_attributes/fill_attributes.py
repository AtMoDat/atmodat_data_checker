import argparse
import os
from netCDF4 import Dataset
import pandas as pd
import json
import datetime


def main():

    args = command_line_parse()

    att_dir = args.attr_files_path
    ifile = args.file
    ipath = args.path

    # Check if path to attribute is given and if CSVs exit
    assert att_dir, "No path to attribute CSV files provided"

    # Which attributes csv files are available
    fill_csv_file = {}

    for att_csv_file in os.listdir(att_dir):
        for fill_type in ['variable', 'mandatory', 'recommended', 'optional']:
            if fill_type in att_csv_file:
                fill_csv_file[fill_type] = os.path.join(att_dir, att_csv_file)

    if not fill_csv_file:
        raise AssertionError('No csv files with attributes to fill were found in ' + att_dir)
    else:
        backup_dir = os.path.join(att_dir, 'attr_backup')
        os.makedirs(backup_dir, exist_ok=True)

    # Find files to process
    file_list = files_to_process(ipath, ifile)

    for ifile in file_list:

        # File name of backup file
        ifile_name = str(ifile.split('/')[-1])
        savegattr_file = os.path.join(backup_dir, ifile_name.split('.nc')[0]+'_attsave.json')

        # Open file
        f = Dataset(ifile, 'r')

        # # Check if file has already been processed and backup of global attributes exits
        # if os.path.isfile(savegattr_file):
        #     continue
        #     attrs_dict_old = pd.read_json(savegattr_file).to_dict()
        #     for key in attrs_dict_old.keys():
        #         attrs_dict_old[key] = attrs_dict_old[key][0]
        # else:
        #     attrs_dict_old = {}
        #     attrs_dict_old['global_attr'] = f.__dict__
        #     for var in f.variables.keys():
        #         attrs_dict_old[var] = {}
        #         for var_attr in f.variables[var].ncattrs():
        #             attrs_dict_old[var][var_attr] = f.variables[var].getncattr(var_attr)
        #     pd.DataFrame(attrs_dict_old).to_csv(path_or_buf=savegattr_file)

        tmp = pd.read_json(savegattr_file).to_dict()

        break

def files_to_process(ipath_in, ifile_in):
    file_list_out = []
    if ifile_in and not ipath_in:
        if ifile_in.endswith(".nc"):
            if os.path.isfile(ifile_in):
                ifile_list_out = [ifile_in]
            else:
                raise RuntimeError('File: ' + ifile_in + ' does not exist')
        else:
            print('Skipping ' + ifile_in + ' as it does not end with ".nc'"")
    elif ipath_in and not ifile_in:
        for root, dirs, files in os.walk(ipath_in):
            for file in files:
                if file.endswith(".nc"):
                    file_list_out.append(os.path.join(root, file))
    else:
        raise RuntimeError('No path or file given')

    return file_list_out


def command_line_parse():
    """parse command line input"""
    # Parser for command line options
    parser = argparse.ArgumentParser(description="Fill variable/global attributes of a NetCDF file with "
                                                 "predefined data from csv files.")
    parser.add_argument("-a", "--attr_files_path", help="Path where csv files for attribute to be filled are located")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--path", help="Add new attributes to all NetCDF in given directory "
                                            "(including sub-directories)")
    group.add_argument("-f", "--file", help="Add new attributes to given file")
    return parser.parse_args()


if __name__ == "__main__":
    main()
