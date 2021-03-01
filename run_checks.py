import os
import argparse
import time

import atmodat_data_checker.result_output.output_directory as output_directory
import atmodat_data_checker.result_output.summary_creation as summary_creation


def run_checks(ifile_in, verbose_in):
    # Types of checks to be performed
    check_types = ["mandatory", "recommended", "optional"]

    # Get base filename and output path
    filename_base = ifile_in.split("/")[-1].rstrip('.nc')

    # Run checks
    for check in check_types:
        os.system(
            'cchecker.py --y ' + output_directory.opath_base + '/atmodat_data_checker_' + check + '.yml -f json_new -o '
            + output_directory.opath + filename_base + '_' + check + '_result.json --test atmodat_data_checker_'
            + check + ':1.0 ' + ifile_in)
        if verbose_in:
            os.system('cchecker.py --y ' + output_directory.opath_base + '/atmodat_data_checker_'
                      + check + '.yml --test atmodat_data_checker_' + check + ':1.0 ' + ifile_in)
    os.system(
        'cfchecks -v auto ' + ifile_in + '>> ' + output_directory.opath + filename_base + '_cfchecks_result.txt')
    if verbose_in:
        os.system('cfchecks -v auto ' + ifile_in)
    return


def comand_line_parse():
    # Parser for command line options
    parser = argparse.ArgumentParser(description="Run the AtMoDat checks suits.")
    parser.add_argument("-v", "--verbose",
                        help="Print output of checkers (longer runtime due to double call of checkers)",
                        action="store_true",
                        default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", help="Processes the given file")
    group.add_argument("-p", "--path", help="Processes all files in a given directory")
    return parser.parse_args()


def return_files_in_directory_tree(ipath):
    file_names = []
    for root,d_names,f_names in os.walk(ipath):
        for f in f_names:
            file_names.append(os.path.join(root, f))

    return file_names


if __name__ == "__main__":

    # start timer
    start_time = time.time()

    # read comman line input
    args = comand_line_parse()

    verbose = args.verbose
    ifile = args.file
    ipath = args.path

    # Check that either ifile or ipath exist
    if not ifile and not ipath:
        raise AssertionError('No file and path given')

    # Create output directory if it does not exist already
    if not os.path.isdir(output_directory.opath):
        os.system('mkdir -p ' + output_directory.opath)

    # Run checks
    if ifile and not ipath:
        if ifile.endswith(".nc"):
            run_checks(ifile, verbose)
        else:
            print('Skipping ' + ifile + ' as it does not end with ".nc'"")
    elif ipath and not ifile:
        files = return_files_in_directory_tree(ipath)
        for file in files:
            if file.endswith(".nc"):
                run_checks(file, verbose)

    # Create summary of results
    summary_creation.create_output_summary()

    # Calculate run time of this script
    print("--- %s seconds ---" % (time.time() - start_time))

    exit()
