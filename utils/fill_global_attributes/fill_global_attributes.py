#!/usr/bin/env python

import argparse
import os
from netCDF4 import Dataset
import pandas as pd
import warnings
import datetime


def check_valid_entry(attribute_in, overwrite_in, string_in, gattrs_old_in):
    if not overwrite_in:
        try:
            gattrs_old_in[attribute_in]
        except KeyError:
            raise Exception('Overwrite flag is False but global attribute "' + attribute_in +
                            '" was previously undefined.') from None
        val_old = gattrs_old_in[attribute_in].strip()
        assert val_old != '', 'Cannot append given string to global attribute "' + attribute_in + '" as it is empty.'
    else:
        assert not pd.isna(string_in), 'Overwrite flag for global attribute "' + attribute_in.strip() + \
                                   '" is True, but string to overwrite is empty.'
    return


def prepare_global_attributes(ifile_csv_in, gattrs_old_in, gattrs_new_in):
    # Read csv and compare to attributes allready present
    df_gattrs = pd.read_csv(ifile_csv_in, header=0, na_values='None')
    for row in df_gattrs.itertuples(index=False):
        attribute, use, overwrite, string = row[:]
        if not bool(use):
            if not pd.isna(string):
                warnings.warn('Global attribute "' + attribute.strip() + '" should not be used but string is '
                                                                         'not empty.')
        else:
            check_valid_entry(attribute, overwrite, string, gattrs_old_in)
            if overwrite:
                assert attribute != 'history', 'Do not overwrite global attribute history! Overwrite flag should ' \
                                               'be set to false.'
                gattrs_new_in[attribute] = string
            else:
                if pd.isna(string):
                    string_append = gattrs_old_in[attribute]
                else:
                    if attribute == 'Conventions:':
                        string_append = ' '.join([str(string), gattrs_old_in[attribute]])
                    elif attribute == 'history':
                        time_string = datetime.datetime.strftime(datetime.datetime.now(tz=datetime.timezone.utc),
                                                                 "%Y-%m-%d %H:%M:%S")+'Z; '
                        history_string = time_string+str(string)
                        string_append = ', '.join([history_string, gattrs_old_in[attribute]])
                    else:
                        string_append = ', '.join([str(string), gattrs_old_in[attribute]])
                gattrs_new_in[attribute] = string_append
    return gattrs_new_in


def command_line_parse():
    """parse command line input"""
    # Parser for command line options
    parser = argparse.ArgumentParser(description="Fill global attributes of a NetCDF file with predifined data from "
                                                 "csv files.")
    parser.add_argument("-a", "--attribute_path", help="Path where csv for attribute to be filled are located")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--path", help="Add newly defined global attributes to all NetCDF in given "
                                            "directory (including sub-directories)")
    group.add_argument("-f", "--file", help="Add newly defined global attributes to single file")
    return parser.parse_args()


if __name__ == "__main__":

    status_list = ['mandatory', 'recommended', 'optional']

    args = command_line_parse()

    att_dir = args.attribute_path
    ifile = args.file
    ipath = args.path

    # Check if path to attribute is given and if CSVs exit
    assert att_dir, "No path to attribute CSV files provided"
    att_dir_list = os.listdir(att_dir)
    for status in status_list:
        status_csv_file = status+'_attributes.csv'
        if status_csv_file not in att_dir_list:
            raise AssertionError(status_csv_file+' not found in '+att_dir)
        else:
            os.makedirs(att_dir+'/savegattr', exist_ok=True)

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

    for ifile in ifile_list:
        # Check if file has allready been processed and backup of global attributes exits
        ifile_name = str(ifile.split('/')[-1])
        savegattr_file = att_dir+'/savegattr/'+ifile_name.split('.nc')[0]+'_attsave.csv'
        if os.path.isfile(savegattr_file):
            gattrs_dict_old = pd.read_csv(savegattr_file).to_dict()
            for key in gattrs_dict_old.keys():
                gattrs_dict_old[key] = gattrs_dict_old[key][0]
        else:
            gattrs_dict_old = {}

        # Open file
        f = Dataset(ifile, 'a')

        # Save preexisting global attributes before they will be deleted
        if not gattrs_dict_old.keys():
            for gattr in f.ncattrs():
                gattrs_dict_old[gattr] = str(f.getncattr(gattr))
            pd.DataFrame(gattrs_dict_old, index=[0]).to_csv(savegattr_file, index=False)

        # Prepare global attributes to be written
        gattrs_dict_new = {}
        for status in status_list:
            gattrs_dict_new = prepare_global_attributes(att_dir+'/'+status+'_attributes.csv', gattrs_dict_old,
                                                        gattrs_dict_new)

        # Delete all preexisiting global attributes
        for gattr in f.ncattrs():
            f.delncattr(gattr)

        # Write new/modified global attributes
        f.setncatts(gattrs_dict_new)

        # Close file
        f.close()

exit()
