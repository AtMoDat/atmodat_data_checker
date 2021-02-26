import os
import argparse
from datetime import date
import pandas as pd
import json


def create_output_directory():
    global opath, opath_base
    # Define output path
    today = date.today()
    today_formatted = today.strftime("%Y%m%d") + '/'

    opath_base = os.path.dirname(__file__)
    if opath_base:
        opath = opath_base + '/checker_output/' + today_formatted
    else:
        opath = 'checker_output/' + today_formatted

    # Create output directory if it does not exist already
    if not os.path.isdir(opath):
        os.system('mkdir -p ' + opath)


def run_checks(ifile_in, verbose_in):
    # Types of checks to be performed
    check_types = ["mandatory", "recommended", "optional"]

    # Get base filename and output path
    filename_base = ifile_in.split("/")[-1].rstrip('.nc')

    # Run checks
    for check in check_types:
        os.system(
            'cchecker.py --y ' + opath_base + '/atmodat_data_checker_' + check + '.yml -f json_new -o '
            + opath + filename_base + '_' + check + '_result.json --test atmodat_data_checker_'
            + check + ':1.0 ' + ifile_in)
        if verbose_in:
            os.system('cchecker.py --y ' + opath_base + '/atmodat_data_checker_'
                      + check + '.yml --test atmodat_data_checker_' + check + ':1.0 ' + ifile_in)
    os.system(
        'cfchecks -v auto ' + ifile_in + '>> ' + opath + filename_base + '_cfchecks_result.txt')
    if verbose_in:
        os.system('cfchecks -v auto ' + ifile_in)
    return


def extract_overview_output_json(ifile_in):
    summary = {}
    with open(opath + ifile_in) as f:
        data = json.load(f)
        for key, value in data.items():
            summary['data_file'] = key
            for key_1, value_1 in value.items():
                summary['check_type'] = key_1.split("_")[-1].split(':')[0]
                for key_2, value_2 in value_1.items():
                    if key_2 == 'scored_points':
                        summary['scored_points'] = value_2
                    elif key_2 == 'possible_points':
                        summary['possible_points'] = value_2
    return summary


def extracts_error_summary_cf_check(ifile_in):
    substr = 'ERRORS detected:'
    with open(opath + ifile_in) as f:
        data = f.read()
        for line in data.strip().split('\n'):
            if substr in line:
                return line.split(':')[-1].strip()


def create_output_summary():
    json_summary = pd.DataFrame()
    cf_errors = 0
    for file in os.listdir(opath):
        if file.endswith(".json"):
            json_summary = json_summary.append(extract_overview_output_json(file),
                                               ignore_index=True)
        if file.endswith("result.txt"):
            cf_errors = cf_errors + int(extracts_error_summary_cf_check(file))

    scored_points = [str(int(json_summary['scored_points'].sum()))]
    possible_points = [str(int(json_summary['possible_points'].sum()))]

    check_types = ["mandatory", "recommended", "optional"]

    with open(opath + 'short_summary.txt', 'w+') as f:
        f.write("This is a summary of the results from the atmodat data checker. \n")
        f.write("Version of the checker: " + str(1.0) + "\n")
        f.write("Total scored points: " + scored_points[0] + '/' + possible_points[0] + '\n')

        for index, check in enumerate(check_types):
            scored_points.append(str(
                int(json_summary['scored_points'].loc[json_summary['check_type'] == check].sum())))
            possible_points.append(str(int(
                json_summary['possible_points'].loc[json_summary['check_type'] == check].sum())))
            f.write("Total scored " + check + " points: " + scored_points[index + 1] + '/' +
                    possible_points[index + 1] + '\n')

        f.write("Total number CF checker errors: " + str(cf_errors))


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

# Create output directory
create_output_directory()

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

create_output_summary()

exit()
