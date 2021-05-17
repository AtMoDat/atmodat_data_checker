#!/usr/bin/env python
import os
import warnings
import argparse
import pandas as pd
from netCDF4 import Dataset


def command_line_parse():
    """parse command line input"""
    # Parser for command line options
    parser = argparse.ArgumentParser(description="Fill global attributes of a NetCDF file with predifined data from "
                                                 "csv files.")
    parser.add_argument("-a", "--attribute_file", help="Path to csv file the contains variable attributes to be filled")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--path", help="Add newly defined variable attributes to all NetCDF in given "
                                            "directory (including sub-directories)")
    group.add_argument("-f", "--file", help="Add newly defined variable attributes to single file")
    return parser.parse_args()


if __name__ == "__main__":

    args = command_line_parse()
    att_file = args.attribute_file
    ifile = args.file
    ipath = args.path

    # Check if path to attribute is given and if CSVs exit
    assert att_file, "No attribute CSV files provided"

    ifile_list = []
    if ifile and not ipath:
        if ifile.endswith(".nc"):
            ifile_list = [ifile]
        else:
            warnings.warn(ifile + ' not a NetCDF file')
    else:
        for root, dirs, files in os.walk(ipath):
            for file in files:
                if file.endswith(".nc"):
                    ifile_list.append(os.path.join(root, file))

    # Read CSVs
    df_varatts = pd.read_csv(att_file, header=0, na_values='None')
    var_att_in = {}
    for row in df_varatts.itertuples(index=False):
        assert not pd.isna(row[0]), "Attributes to be changed are given but no variable to be modified is provided"
        var_att_in[row[0]] = {}
        for natt, attribute in enumerate(['var_new', 'long_name', 'standard_name', 'units']):
            if pd.isna(row[natt+1]):
                var_att_in[row[0]][attribute] = None
            else:
                var_att_in[row[0]][attribute] = str(row[natt+1])

    var_att_list = var_att_in.keys()
    var_att_modify = ['long_name', 'standard_name', 'units']
    var_olddir_list = []
    for ifile in ifile_list:
        f = Dataset(ifile, 'a')
        for var in list(f.variables):
            if var in var_att_list:
                for att in var_att_modify:
                    if var_att_in[var][att]:
                        f.variables[var].setncattr(att, var_att_in[var][att])
                if var_att_in[var]['var_new']:
                    f.renameVariable(var, var_att_in[var]['var_new'])
        for var in var_att_list:
            if var in ifile and var_att_in[var]['var_new']:
                var_olddir = ifile.rstrip(ifile.split('/')[-1])
                var_olddir_list.append(var_olddir)
                var_newdir = var_olddir.replace(var, var_att_in[var]['var_new'])
                if not os.path.isdir(var_newdir):
                    os.makedirs(var_newdir)
                ifile_new = ifile.replace(var, var_att_in[var]['var_new'])
                os.rename(ifile, ifile_new)
    for olddir in set(var_olddir_list):
        os.rmdir(olddir)
                
    exit()
