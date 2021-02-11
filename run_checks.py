import os
import argparse


def run_checks(ifile_in, verbose_in):
    # Types of checks to be performed
    check_types = ["mandatory", "recommended", "optional"]

    # Get base filename and output path
    filename_base = ifile_in.split("/")[-1].rstrip('.nc')
    opath_base = os.path.dirname(__file__)
    if opath_base:
        opath = opath_base + '/checker_output/'
    else:
        opath = 'checker_output/'

    # Create outchecker_output/put directory and decide how to handle preexisiting checker output
    if not os.path.isdir(opath):
        os.system('mkdir -p ' + opath)

    # Run checks
    for check in check_types:
        os.system('cchecker.py --y ' + opath_base + '/atmodat_data_checker_' + check + '.yml -f json_new -o '
                  + opath + filename_base + '_' + check + '_result.json --test atmodat_data_checker_'
                  + check + ':1.0 ' + ifile_in)
        if verbose_in:
            os.system('cchecker.py --y ' + opath_base + '/atmodat_data_checker_'
                      + check + '.yml --test atmodat_data_checker_' + check + ':1.0 ' + ifile_in)
    os.system('cfchecks -v auto ' + ifile_in + '>> ' + opath + filename_base + '_cfchecks_result.txt')
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


args = comand_line_parse()

verbose = args.verbose
ifile = args.file
ipath = args.path

# Check that either ifile or ipath exist
if not ifile and not ipath:
    raise AssertionError('No file and path given')

# Run checks
if ifile and not ipath:
    if ifile.endswith(".nc"):
        run_checks(ifile, verbose)
    else:
        print('Skipping ' + ifile + ' as it does not end with ".nc'"")
elif ipath and not ifile:
    for file in os.listdir(ipath):
        if file.endswith(".nc"):
            if ipath.endswith('/'):
                run_checks(ipath + file, verbose)

            else:
                run_checks(ipath + '/' + file, verbose)

exit()
