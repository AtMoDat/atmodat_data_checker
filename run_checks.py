#!/usr/bin/env python

import argparse
import os
from datetime import datetime
from pathlib import Path
import atmodat_checklib.result_output.output_directory as output_directory
import atmodat_checklib.result_output.summary_creation as summary_creation

idiryml = str(Path(__file__).resolve().parents[0])


def run_checks(ifile_in, verbose_in, check_types_in, cfversion_in):
    """run all checks"""
    # Get base filename and output path
    filename_base = ifile_in.split("/")[-1].rstrip('.nc')
    for check in check_types_in:
        if check != 'CF':
            os.system(
                'cchecker.py --y ' + idiryml
                + '/atmodat_standard_checks.yml -f json_new -o ' + opath
                + '/' + check + '/' + filename_base + '_' + check
                + '_result.json --test atmodat_standard:3.0 ' + ifile_in)
            if verbose_in:
                os.system('cchecker.py --y ' + idiryml
                          + '/atmodat_standard_checks.yml --test atmodat_standard:3.0 ' + ifile_in)
                if 'CF' in check_types_in:
                    print('')
                    print('')
                    print('==============================================================================')
                    print('===============================CF-Checker=====================================')
                    print('==============================================================================')
                    print('')
        else:
            os.system(
                'cfchecks -v ' + cfversion_in + ' ' + ifile_in + '>> ' + opath + '/CF/' + filename_base
                + '_cfchecks_result.txt')
            if verbose_in:
                os.system('cfchecks -v ' + cfversion_in + ' ' + ifile_in)
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
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", help="Processes the given file")
    group.add_argument("-p", "--path", help="Processes all files in a given directory")

    return parser.parse_args()


if __name__ == "__main__":

    # record start time
    start_time = datetime.now()

    # read command line input
    args = command_line_parse()
    verbose = args.verbose
    ifile = args.file
    ipath = args.path
    opath_in = args.opath
    cfversion = args.cfversion
    whatchecks = args.whatchecks
    parsed_summary = args.summary

    # Define output path for checker output
    if opath_in:
        # user-defined path
        opath = opath_in
    else:
        # default path with subdirectory containing timestamp of check
        opathe = start_time.now().strftime("%Y%m%d_%H%M") + '/'
        opath = idiryml + '/checker_output/' + opathe

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
    if not ifile and not ipath:
        raise RuntimeError('No file and path given')

    check_types = ['atmodat', 'CF']
    if whatchecks == 'CF':
        check_types.remove('atmodat')
    elif whatchecks == 'AT':
        check_types.remove('CF')

    # Create directory for checker output
    output_directory.create_directories(opath, check_types)

    # Run checks
    file_counter = 0
    if ifile and not ipath:
        if ifile.endswith(".nc"):
            if os.path.isfile(ifile):
                run_checks(ifile, verbose, check_types, cfversion)
                file_counter = file_counter + 1
            else:
                raise RuntimeError('File: ' + ifile + ' does not exist')
        else:
            print('Skipping ' + ifile + ' as it does not end with ".nc'"")
    elif ipath and not ifile:
        files = output_directory.return_files_in_directory_tree(ipath)
        for file in files:
            if file.endswith(".nc"):
                run_checks(file, verbose, check_types, cfversion)
                file_counter = file_counter + 1

    # Create summary of results if specified
    if parsed_summary:
        summary_creation.create_output_summary(file_counter, opath, check_types)

    # Calculate run time of this script
    print("--- %.4f seconds for checking %s files---" % ((datetime.now() - start_time).total_seconds(), file_counter))

    exit()
