"""module to create summary of results from output of atmodat data checker"""

import json
import os
from atmodat_checklib import __version__
import pandas as pd
import atmodat_checklib.result_output.output_directory as output_directory


def delete_file(file):
    """deletes given file"""
    os.remove(file)


def extract_from_nested_json(obj, key):
    """Recursively fetch values from nested json file."""
    array = []

    def extract(obj, array, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    array.append(v)
                elif isinstance(v, (dict, list)):
                    extract(v, array, key)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, array, key)
        return array

    values = extract(obj, array, key)
    return values


def extract_overview_output_json(ifile_in):
    """extracts information from given json file and returns them as a dictionary"""

    with open(ifile_in) as f:
        data = json.load(f)

        # define keys and create empty directory
        summary_keys = ['source_name', 'testname', 'high_priorities', 'medium_priorities', 'low_priorities']
        summary = {key: None for key in summary_keys}

        # extract information from json file
        for sum_key in summary_keys:
            summary[sum_key] = extract_from_nested_json(data, sum_key)[0]

    return summary


def extracts_error_summary_cf_check(ifile_in):
    """extracts information from given txt file and returns them as a string"""
    substr = 'ERRORS detected:'
    with open(ifile_in) as f:
        data = f.read()
        for line in data.strip().split('\n'):
            if substr in line:
                return line.split(':')[-1].strip()


def write_short_summary(json_summary, cf_errors, file_counter):
    """create file which contains the short version of the summary"""

    prio_dict = {'high_priorities': 'Mandatory', 'medium_priorities': 'Recommended', 'low_priorities': 'Optional'}
    passed_checks = {'all': [0, 0]}
    for prio in prio_dict.keys():
        passed_checks[prio] = [0, 0]
        checks_prio = json_summary[prio]
        for checks in checks_prio:
            for check in checks:
                passed_checks[prio][0] += 1
                passed_checks['all'][0] += 1
                if check['value'][0] == check['value'][1]:
                    passed_checks[prio][1] += 1
                    passed_checks['all'][1] += 1

    # write summary of results into summary file
    with open(output_directory.opath + 'short_summary.txt', 'w+') as f:
        f.write("This is a short summary of the results from the atmodat data checker. \n")
        f.write("Version of the checker: " + str(__version__) + "\n")
        f.write("Checking against: " + json_summary['testname'][0] + "\n \n")
        f.write("Number of checked files: " + str(file_counter) + '\n \n')
        f.write("Total checks passed: " + str(passed_checks['all'][1]) + '/' + str(passed_checks['all'][0]) + '\n')
        for prio in prio_dict.keys():
            f.write(prio_dict[prio]+" checks passed: " + str(passed_checks[prio][1]) + '/' + str(passed_checks[prio][0]) + '\n')
        f.write("CF checker errors: " + str(cf_errors))


def write_detailed_json_summary(json_summary):
    """write detailed summary of results into summary file"""
    with open(output_directory.opath + 'detailed_summary.csv', 'w+') as f:
        f.write("This is a detailed summary of the results from the atmodat data checker. \n")
        f.write("Version of the checker: " + str(1.0) + "\n \n")
        json_summary.to_csv(f, index=False, header=True, sep=',')


def create_output_summary(file_counter):
    """main function to create summary output"""
    json_summary = pd.DataFrame()
    cf_errors = 0
    files = output_directory.return_files_in_directory_tree(output_directory.opath)
    for file in files:
        if file.endswith("_result.json"):
            json_summary = json_summary.append(extract_overview_output_json(file),
                                               ignore_index=True)
        elif file.endswith("_cfchecks_result.txt"):
            cf_errors = cf_errors + int(extracts_error_summary_cf_check(file))

    write_short_summary(json_summary, cf_errors, file_counter)
    
    # This is disabled for now
    # write_detailed_json_summary(json_summary)
