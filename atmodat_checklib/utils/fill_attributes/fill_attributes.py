import argparse
import os
from netCDF4 import Dataset
import numpy as np
import json
import pandas as pd
import warnings
import datetime


def main():

    args = command_line_parse()

    att_dir = args.attr_files_path
    ifile = args.file
    ipath = args.path
    restore = args.restore

    # Check if path to attribute is given and if CSVs exit
    assert att_dir, "No path to attribute CSV files provided"

    # Which attributes csv files are available
    fill_csv_file = {}

    status_list = ['mandatory', 'recommended', 'optional']

    for att_csv_file in os.listdir(att_dir):
        for fill_type in status_list:
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
        f = Dataset(ifile, 'a')

        # Check if file has already been processed. Else backup of global attributes exits
        if os.path.isfile(savegattr_file):
            attrs_dict = json.loads(open(savegattr_file, 'r').read())
        else:
            attrs_dict = {}
            attrs_dict['global_attr'] = f.__dict__
            for var in f.variables.keys():
                attrs_dict[var] = {}
                for var_attr in f.variables[var].ncattrs():
                    attrs_dict[var][var_attr] = f.variables[var].getncattr(var_attr)
            open(savegattr_file, 'w').write(json.dumps(attrs_dict, cls=NumpyEncoder))

        # Delete all preexisting global attributes
        for gattr in f.ncattrs():
            f.delncattr(gattr)

        if restore:
            f.setncatts(attrs_dict['global_attr'])
            continue

        # Prepare global attributes to be written
        global_attrs_write = {}
        for status in status_list:
            global_attrs_write = prepare_global_attributes(os.path.join(att_dir, status+'_attributes.csv'),
                                                           attrs_dict['global_attr'], global_attrs_write)

        # Write new/modified global attributes
        f.setncatts(global_attrs_write)


def prepare_global_attributes(ifile_csv_in, gattrs_old_in, gattrs_new_in):
    # Read csv and compare to attributes already present
    df_gattrs = pd.read_csv(ifile_csv_in, header=0, na_values='None')

    for row in df_gattrs.itertuples(index=False):
        attribute, use, append, string = row[:]
        string_old, string_out = None, None
        if not bool(use):
            if not pd.isna(string):
                warnings.warn('Global attribute "' + attribute.strip() + '" should not be used but entry provided.')
        else:
            if pd.isna(string) and not append:
                warnings.warn('Global attribute "' + attribute.strip() + '" should be used but empty entry provided.')
            if append:
                try:
                    string_old = gattrs_old_in[attribute]
                except KeyError:
                    string_old = None
            if attribute == 'Conventions':
                string_out = append_string(string, string_old, delimiter=' ')
            elif attribute == 'history':
                time_string = datetime.datetime.strftime(datetime.datetime.now(tz=datetime.timezone.utc),
                                                         "%Y-%m-%d %H:%M:%S")+'Z; '
                history_string = time_string+str(string)+'\n'
                string_out = append_string(history_string, string_old, delimiter=' ')
            else:
                string_out = append_string(string, string_old, delimiter=' ')
        gattrs_new_in[attribute] = string_out
    return gattrs_new_in


def append_string(string_in, string_old_in, **kwargs):
    delimiter = ' '
    if 'delimiter' in kwargs:
        delimiter = kwargs['delimiter']
    if string_old_in:
        out_string = delimiter.join([str(string_in), string_old_in])
    else:
        out_string = string_in
    return out_string


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int32):
            return int(obj)
        if isinstance(obj, np.float32):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def files_to_process(ipath_in, ifile_in):
    file_list_out = []
    if ifile_in and not ipath_in:
        if ifile_in.endswith(".nc"):
            if os.path.isfile(ifile_in):
                file_list_out.append(ifile_in)
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
    parser.add_argument("-r", "--restore", help="Restore variable/global attributes",
                        action="store_true", default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--path", help="Add new attributes to all NetCDF in given directory "
                                            "(including sub-directories)")
    group.add_argument("-f", "--file", help="Add new attributes to given file")
    return parser.parse_args()


if __name__ == "__main__":
    main()
