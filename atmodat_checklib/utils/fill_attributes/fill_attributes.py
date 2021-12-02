import argparse
import os
from netCDF4 import Dataset
import numpy as np
import json
import pandas as pd
import warnings
import datetime


def main():

    # Command line parsing
    args = command_line_parse()
    att_dir = args.attr_files_path
    ifile = args.file
    ipath = args.path
    restore = args.restore

    # Check if path to attribute is given and if CSVs exit
    assert att_dir, "No path to attribute CSV files provided"

    # Find all available attribute files
    fill_csv_file = {}
    status_list = ['mandatory', 'recommended', 'optional']
    for att_csv_file in os.listdir(att_dir):
        for fill_type in status_list:
            if fill_type in att_csv_file:
                fill_csv_file[fill_type] = os.path.join(att_dir, att_csv_file)
        if 'variable' in att_csv_file:
            fill_csv_file['variable'] = os.path.join(att_dir, att_csv_file)

    # Check if csv files are provided and create directory for backup files
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
        savegattr_file = os.path.join(backup_dir, ifile_name.split('.nc')[0] + '_attsave.json')

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

        # Prepare global attributes to be written
        global_attrs_write, var_attrs_write = {}, {}
        for fill_type in fill_csv_file.keys():
            if fill_type in status_list:
                global_attrs_write = prepare_global_attributes(fill_csv_file[fill_type], attrs_dict['global_attr'],
                                                               global_attrs_write)
            else:
                var_attrs_write = prepare_variable_attributes(fill_csv_file[fill_type], attrs_dict)

        # Delete all preexisting global attributes
        for gattr in f.ncattrs():
            f.delncattr(gattr)
            
        # Write new/modified global attributes
        f.setncatts(attrs_dict['global_attr'])
        if not restore:
            f.setncatts(global_attrs_write)

        # Write new/modified variable attribute
        for var in f.variables:
            for var_attr in f.variables[var].ncattrs():
                f.variables[var].delncattr(var_attr)

        # First restore original variable information
        var_keys = list(f.variables.keys())
        for var in var_keys:
            if var in attrs_dict.keys():
                for attr, val_attrs in attrs_dict[var].items():
                    if attr not in ['varname_new', '_FillValue']:
                        f.variables[var].setncattr(attr, val_attrs)
            else:
                for var_old, attr_dict in var_attrs_write.items():
                    if 'varname_new' in attr_dict:
                        if var == attr_dict['varname_new']:
                            f.renameVariable(var, var_old)
                            for attr, val_attrs in attrs_dict[var_old].items():
                                if attr not in ['varname_new', '_FillValue']:
                                    f.variables[var_old].setncattr(attr, val_attrs)

        # Write new variable attributes into file
        if not restore:
            for var, attr_dict in var_attrs_write.items():
                if 'varname_new' in attr_dict:
                    if attr_dict['varname_new'] != var:
                        if var in f.variables:
                            f.renameVariable(var, attr_dict['varname_new'])
                        var = attr_dict['varname_new']
                for attr, val_attrs in attr_dict.items():
                    if attr not in ['varname_new', '_FillValue']:
                        f.variables[var].setncattr(attr, val_attrs)

        f.close()

        # Rename file name that contains a variable if a new variable name is provided
        for var, attr_dict in var_attrs_write.items():
            if 'varname_new' in attr_dict and var != attr_dict['varname_new']:
                if restore:
                    if attr_dict['varname_new'] in ifile:
                        rename_path_file(ifile, attr_dict['varname_new'], var, savegattr_file)
                else:
                    if var in ifile:
                        rename_path_file(ifile, var, attr_dict['varname_new'], savegattr_file)


def rename_path_file(ifile_in, var_in, var_new_in, attr_file):
    # Rename file with backed up attributes
    attr_file_filepath = os.path.split(attr_file)
    attr_file_new = os.path.join(attr_file_filepath[0], attr_file_filepath[1].replace(var_in, var_new_in))
    os.rename(attr_file, attr_file_new)

    # Rename netCDF file itself
    file_path_old, file_old = os.path.split(ifile_in)
    file_path_new = file_path_old.replace(var_in, var_new_in)
    file_new = file_old.replace(var_in, var_new_in)
    if file_path_new != file_path_old:
        if not os.path.isdir(file_path_new):
            os.makedirs(file_path_new)
            os.rename(ifile_in, os.path.join(file_path_new, file_new))
            os.rmdir(file_path_old)
    else:
        os.rename(ifile_in, os.path.join(file_path_new, file_new))


def prepare_variable_attributes(ifile_csv_in, attrs_old_in):
    # Read CSVs
    varattrs_dict = pd.read_csv(ifile_csv_in, na_values='None').to_dict(orient='list')
    var_info = {}
    for var in attrs_old_in.keys():
        if var != 'global_attr':
            var_info[var] = attrs_old_in[var]
            if var in varattrs_dict['varname_old']:
                ind_var = varattrs_dict['varname_old'].index(var)
                varname_new = varattrs_dict['varname_new'][ind_var]
                if isinstance(varname_new, str):
                    if len(varname_new.strip()) != 0:
                        var_info[var]['varname_new'] = varname_new
            elif var not in varattrs_dict['varname_old'] and var in varattrs_dict['varname_new']:
                ind_var = varattrs_dict['varname_new'].index(var)
            else:
                continue
            for tmp in varattrs_dict.keys():
                if 'varname_old' not in tmp:
                    att_fill = varattrs_dict[tmp][ind_var]
                    if not pd.isna(att_fill) and len(att_fill.strip()) != 0:
                        var_info[var][tmp] = varattrs_dict[tmp][ind_var]
    return var_info


def prepare_global_attributes(ifile_csv_in, gattrs_old_in, gattrs_new_in):
    # Read csv and compare attributes to those already present
    df_gattrs = pd.read_csv(ifile_csv_in, header=0, na_values='None')

    for row in df_gattrs.itertuples(index=False):
        attribute, use, append, string = row[:]
        string_old, string_out = None, None
        if not bool(use):
            if not pd.isna(string):
                warnings.warn('Global attribute ' + attribute.strip() + ' should not be used but entry provided.')
        else:
            if pd.isna(string) and not append:
                warnings.warn('Global attribute ' + attribute.strip() + ' should be used but empty entry provided.')
            if append:
                try:
                    string_old = gattrs_old_in[attribute]
                except KeyError:
                    string_old = None
            if attribute == 'Conventions':
                string_out = append_string(string, string_old, delimiter=' ')
            elif attribute == 'history':
                time_string = datetime.datetime.strftime(datetime.datetime.now(tz=datetime.timezone.utc),
                                                         "%Y-%m-%d %H:%M:%S") + 'Z; '
                history_string = time_string + str(string) + '\n'
                string_out = append_string(history_string, string_old, delimiter=' ')
            else:
                string_out = append_string(string, string_old, delimiter=' ')
        if string_out:
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
                                            "(including subdirectories)")
    group.add_argument("-f", "--file", help="Add new attributes to given file")
    return parser.parse_args()


if __name__ == "__main__":
    main()
