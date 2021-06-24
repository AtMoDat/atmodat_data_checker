#!/usr/bin/env python

import argparse
import os
import time

import atmodat_checklib.result_output.output_directory as output_directory
import atmodat_checklib.result_output.summary_creation as summary_creation


def run_checks(ifile_in, verbose_in):
    """run all checks"""

    # Get base filename and output path
    filename_base = ifile_in.split("/")[-1].rstrip('.nc')

    # AtMoDat-Checker
    os.system(
            'cchecker.py --y ' + output_directory.opath_base
            + '/atmodat_standard_checks.yml -f json_new -o ' + output_directory.opath + '/atmodat/' + filename_base +
            '_result.json --test atmodat_standard:3.0 ' + ifile_in)
    if verbose_in:
        os.system('cchecker.py --y ' + output_directory.opath_base +
                  '/atmodat_standard_checks.yml --test atmodat_standard:3.0 ' + ifile_in)

    # CF-Checker
    os.system(
        'cfchecks -v auto ' + ifile_in + '>> ' + output_directory.opath + 'CF/' + filename_base
        + '_cfchecks_result.txt')
    if verbose_in:
        os.system('cfchecks -v auto ' + ifile_in)
    return


def command_line_parse():
    """parse command line input"""
    # Parser for command line options
    parser = argparse.ArgumentParser(description="Run the AtMoDat checks suits.")
    parser.add_argument("-v", "--verbose",
                        help="Print output of checkers (longer runtime due to double call of "
                             "checkers)",
                        action="store_true",
                        default=False)
    parser.add_argument("-s", "--summary", help="Create summary of checker output.",
                        action="store_true",
                        default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", help="Processes the given file")
    group.add_argument("-p", "--path", help="Processes all files in a given directory")

    return parser.parse_args()


if __name__ == "__main__":

    # start timer
    start_time = time.time()

    # read command line input
    args = command_line_parse()

    verbose = args.verbose
    ifile = args.file
    ipath = args.path
    parsed_summary = args.summary

    # Check that either ifile or ipath exist
    if not ifile and not ipath:
        raise AssertionError('No file and path given')

    # Create directory for checker output
    output_directory.create_directories()

    # Run checks
    file_counter = 0
    if ifile and not ipath:
        if ifile.endswith(".nc"):
            run_checks(ifile, verbose)
            file_counter = file_counter + 1
        else:
            print('Skipping ' + ifile + ' as it does not end with ".nc'"")
    elif ipath and not ifile:
        files = output_directory.return_files_in_directory_tree(ipath)
        for file in files:
            if file.endswith(".nc"):
                run_checks(file, verbose)
                file_counter = file_counter + 1

    # Create summary of results if specified
    if parsed_summary:
        summary_creation.create_output_summary(file_counter)

    # Calculate run time of this script
    print("--- %s seconds ---" % (time.time() - start_time))

    exit()
