#!/usr/bin/env python

import argparse
import os
from datetime import datetime
import subprocess
import numpy as np

import atmodat_checklib.utils.output_directory_util as output_directory
import atmodat_checklib.utils.summary_creation_util as summary_creation
from atmodat_checklib.utils.env_util import set_env_variables
from atmodat_checklib import __version__


def main():

    # Set environment variables
    udunits2_xml_path, atmodat_cvs = set_env_variables()
    os.environ['PYESSV_ARCHIVE_HOME'] = os.path.join(atmodat_cvs, 'pyessv-archive')
    os.environ['UDUNITS2_XML_PATH'] = udunits2_xml_path

    idiryml = os.path.join(atmodat_cvs, '')

    # record start time
    start_time = datetime.now()

    # read command line input
    args = command_line_parse()
    verbose = args.verbose
    ifile = args.file
    ipath = args.path
    ipath_norec = args.path_no_recursive
    opath_in = args.opath
    cfversion = args.cfversion
    whatchecks = args.whatchecks
    parsed_summary = args.summary

    # Define output path for checker output
    # user-defined opath
    if opath_in:
        if opath_in.strip() == '/':
            raise RuntimeError('Root directory should not be defined as output path!')
        opath = os.path.abspath(opath_in)
    # predefined opath
    else:
        # default path with subdirectory containing timestamp of check
        opath = os.getcwd()
    opath = os.path.join(opath, 'atmodat_checker_output', '')

    # Define version of CF table against which the files shall be checked.
    # Default is auto --> CF table version parsed from global attribute 'Conventions'.
    if cfversion != 'auto':
        if cfversion not in ('1.4', '1.5', '1.6', '1.7', '1.8'):
            print('User-defined -cfv option invalid; using \'auto\' instead')
            cfversion = 'auto'

    # Let user choose if files shall be checked against (AT) the ATMODAT metadata specifications
    # (excluding the CF checker), (CF) the CF Conventions or (both) against both. Default is both.
    if whatchecks != 'both':
        if whatchecks not in ('AT', 'CF'):
            print('User-defined -check option invalid; using \'both\' instead')
            whatchecks = 'both'

    # Check that either ifile or ipath exist
    if not ifile and not ipath and not ipath_norec:
        raise RuntimeError('No file and path given')

    check_types = ['atmodat', 'CF']
    if whatchecks == 'CF':
        check_types.remove('atmodat')
    elif whatchecks == 'AT':
        check_types.remove('CF')

    # Create directory for checker output
    opath_run = output_directory.create_directories(opath, check_types)

    # Single file
    if ifile and not (ipath or ipath_norec):
        # Check for file ending and add file to list
        files_check = check_file_suffix([ifile])

    # Multiple files
    elif (ipath or ipath_norec) and not ifile:
        # Look for files in given directory
        if ipath:
            files_all = output_directory.return_files_in_directory_tree(ipath)
        else:
            files_all = output_directory.return_files_in_directory(ipath_norec)
        # Check for file ending and add file to list
        files_check = check_file_suffix(files_all)

    # Run global attribute checks
    file_counter = len(files_check)
    run_checks(files_check, verbose, check_types, cfversion, opath_run, idiryml)

    # Create summary of results if specified
    if parsed_summary:
        summary_creation.create_output_summary(file_counter, opath_run, check_types)

    # Create a symbolic link to latest checker output
    latest_link = os.path.join(opath, 'latest')
    if os.path.isdir(latest_link):
        os.unlink(latest_link)
    os.symlink(opath_run, os.path.join(opath, 'latest'))

    # Calculate run time of this script
    print("--- %.4f seconds for checking %s files---" % ((datetime.now() - start_time).total_seconds(), file_counter))


def check_file_suffix(ifiles):
    files_to_check = []
    for file in ifiles:
        if not os.path.isfile(file):
            if not os.path.isdir(file):
                raise RuntimeError(f'File: {file} does not exist')
        else:
            if file.endswith(".nc"):
                files_to_check.append(file)
            elif file.endswith(".NC"):
                raise RuntimeError(f'NetCDF file suffix in {file} must be lower case. Please verify for other files')
    return files_to_check


def utf8len(string_in):
    return len(string_in.encode('utf-8'))


def cmd_string_checker(io_in, idiryml_in):
    # String of input and output files
    ifile_in_string = " ".join(io_in[0])
    ofiles_checker_string = " ".join(io_in[1])

    # Output string creation
    return 'compliance-checker --y ' + idiryml_in + 'atmodat_standard_checks.yml -f json_new -f text ' + \
           ofiles_checker_string + ' --test atmodat_standard:3.0 ' + ifile_in_string


def cmd_string_cf(ifiles_in, cf_version_in):
    ifile_in_string = " ".join(ifiles_in)
    return 'cfchecks -v ' + cf_version_in + ' ' + ifile_in_string


def cmd_string_creation(check_in, ifiles_in, opath_file_in, filenames_base_in, idiryml_in, cf_version_in):
    max_string_len = 131072
    cmd_out = []
    if check_in == 'atmodat':

        # List of output files
        ofiles_checker = ['-o ' + os.path.join(opath_file_in, check_in, filename_base + '_' + check_in + '_result.json')
                          for filename_base in filenames_base_in]

        # Output string creation
        tmp_cmd_out = cmd_string_checker((ifiles_in, ofiles_checker), idiryml_in)
        num_split = int(np.ceil(utf8len(tmp_cmd_out) / max_string_len))
        if num_split > len(ifiles_in):
            num_split = len(ifiles_in)

        # Split if size of string exceeds max_string_len
        if num_split < 2:
            cmd_out.append(tmp_cmd_out)
        else:
            for io_files in zip(np.array_split(ifiles_in, num_split), np.array_split(ofiles_checker, num_split)):
                cmd_out.append(cmd_string_checker(io_files, idiryml_in))

    elif check_in == 'CF':
        tmp_cmd_out = cmd_string_cf(ifiles_in, cf_version_in)
        num_split = int(np.ceil(utf8len(tmp_cmd_out) / max_string_len))
        if num_split > len(ifiles_in):
            num_split = len(ifiles_in)
        if num_split < 2:
            cmd_out.append(tmp_cmd_out)
        else:
            for split_ifiles in np.array_split(ifiles_in, num_split):
                cmd_out.append(cmd_string_cf(split_ifiles, cf_version_in))
    return cmd_out


def run_checks(ifile_in, verbose_in, check_types_in, cfversion_in, opath_file, idiryml_in):
    """run all checks"""
    # Get base filename and output path
    filenames_base = [os.path.basename(os.path.realpath(f)).rstrip('.nc') for f in ifile_in]
    for check in check_types_in:

        # Remove preexisting checker output
        opath_checks = os.path.join(opath_file, check, '')
        for old_file in os.listdir(opath_checks):
            os.remove(os.path.join(opath_checks, old_file))

        if check == 'atmodat':
            cmd_checker = cmd_string_creation(check, ifile_in, opath_file, filenames_base, idiryml_in, cfversion_in)
            for cmd in cmd_checker:
                subprocess.run(cmd, shell=True)
        elif check == 'CF':
            cmd_cf = cmd_string_creation(check, ifile_in, opath_file, filenames_base, idiryml_in, cfversion_in)
            output_string_all = []
            for cmd in cmd_cf:
                output_string_all.append(subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout)
            output_string = ''.join(output_string_all)
            split_string = 'CHECKING NetCDF FILE'
            output_string_files = output_string.split(split_string)[1::]
            for ofile_data_cf in zip(filenames_base, output_string_files):
                ofile_cf = os.path.join(opath_file, 'CF', '') + ofile_data_cf[0] + '_' + check + '_result.txt'
                with open(ofile_cf, 'w', encoding='utf-8') as f_cf:
                    f_cf.write(split_string + ofile_data_cf[1])
    for filename_base in filenames_base:
        for check in check_types_in:
            file_verbose = os.path.join(opath_file, check, '') + filename_base + '_' + check + '_result.txt'
            if verbose_in:
                with open(file_verbose, 'r', encoding='utf-8') as f_verbose:
                    if check == 'CF':
                        print('')
                        print('==============================================================================')
                        print('===============================CF-Checker=====================================')
                        print('==============================================================================')
                        print('')
                        print(f_verbose.read())
                    elif check == 'atmodat':
                        print('')
                        print('==============================================================================')
                        print('===============================AtMoDat-Checks=================================')
                        print('==============================================================================')
                        print('')
                        print(f_verbose.read())
            # Clean-up
            if check == 'atmodat':
                if os.path.isfile(file_verbose):
                    os.remove(file_verbose)
    return


def command_line_parse():
    """parse command line input"""
    # Parser for command line options
    parser = argparse.ArgumentParser(description="Run the AtMoDat checks suits.")
    parser.add_argument("-v", "--verbose",
                        help="Print output of checkers (longer runtime due to double call of checkers)",
                        action="store_true",
                        default=False)
    parser.add_argument("-op", "--opath", help="Define custom path where checker output shall be written",
                        default=False)
    parser.add_argument("-cfv", "--cfversion", help="Define custom CF table version against which the file shall be "
                                                    "checked. Valid are versions from 1.3 to 1.8.  "
                                                    "Example: \"-cfv 1.6\". Default is 'auto'",
                        default='auto')
    parser.add_argument("-check", "--whatchecks", help="Define if AtMoDat or CF check or both shall be executed. "
                                                       "Valid options: AT, CF, both. Example: \"-check CF\". "
                                                       "Default is 'both'",
                        default='both')
    parser.add_argument("-s", "--summary", help="Create summary of checker output",
                        action="store_true",
                        default=False)
    parser.add_argument('-V', '--version', action='version',
                        version=f'ATMODAT Standard Compliance Checker Version: {__version__}')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", help="Processes the given file")
    group.add_argument("-p", "--path", help="Processes all files in a given path and subdirectories "
                                            "(recursive file search)")
    group.add_argument("-pnr", "--path_no_recursive", help="Processes all files in a given directory")

    return parser.parse_args()


if __name__ == "__main__":
    main()
