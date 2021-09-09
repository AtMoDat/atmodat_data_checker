"""module to create summary of results from output of atmodat data checker"""

import json
import os
from atmodat_checklib import __version__
import pandas as pd
import atmodat_checklib.result_output.output_directory as output_directory
import datetime
import csv


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
        summary['file'] = ifile_in

    return summary


def extracts_error_summary_cf_check(ifile_in, errors_in):
    """extracts information from given txt file and returns them as a string"""
    std_name = 'Using Standard Name Table Version '
    with open(ifile_in) as f:
        data = f.read()
        for line in data.strip().split('\n'):
            if std_name in line:
                std_name_table_out = line.replace(std_name, '').split(' ')[0]
            if 'ERRORS detected:' in line:
                errors_detected = errors_in + int(line.split(':')[-1].strip())
    return errors_detected, std_name_table_out


def write_short_summary(json_summary, cf_errors, file_counter, std_name_table_in, opath_in):
    """create file which contains the short version of the summary"""
    prio_dict = {'high_priorities': 'Mandatory', 'medium_priorities': 'Recommended', 'low_priorities': 'Optional'}
    passed_checks = {'all': [0, 0]}
    if isinstance(json_summary, pd.DataFrame):
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
    with open(opath_in + '/short_summary.txt', 'w+') as f:
        f.write("Short summary of checks: \n \n")
        if isinstance(json_summary, pd.DataFrame):
            text_out = "Checking against: " + json_summary['testname'][0]
            if std_name_table_in is not None:
                text_out = text_out + ", CF table version: " + std_name_table_in + "\n"
            else:
                text_out = text_out + "\n"
            f.write(text_out)
            f.write("Version of the AtMoDat checker: " + str(__version__) + "\n")
        f.write("Checked at: " + datetime.datetime.now().isoformat(timespec='seconds') + "\n \n")
        f.write("Number of checked files: " + str(file_counter) + '\n')
        if isinstance(json_summary, pd.DataFrame):
            for prio in prio_dict.keys():
                f.write(prio_dict[prio] + " checks passed: " + str(passed_checks[prio][1]) + '/'
                        + str(passed_checks[prio][0]) + '\n')
        if cf_errors is not None:
            f.write("CF checker errors: " + str(cf_errors))


def write_long_summary(json_summary_in, opath_in):

    if json_summary_in is None:
        return

    prio_cat_all = ['high_priorities', 'medium_priorities', 'low_priorities']
    prio_dict = {'high_priorities': 'mandatory', 'medium_priorities': 'recommended', 'low_priorities': 'optional'}
    files_check = json_summary_in['file']

    data_table = {}
    for prio_cat in prio_cat_all:
        data_table[prio_cat] = {}
        data_prio = json_summary_in[prio_cat]
        data_table[prio_cat] = {'File': [], 'Check level': [], 'Global Attribute': [], 'Error Message': []}
        file_name_old = []
        for nf, file in enumerate(files_check):
            file_name = file.split('/')[-1].replace('_atmodat_result.json', '.nc')
            for check in data_prio[nf]:
                if check['value'][0] != check['value'][1]:
                    if file_name_old != file_name:
                        for key in data_table[prio_cat].keys():
                            data_table[prio_cat][key].append('')
                    data_table[prio_cat]['File'].append(file_name)
                    msgs = check['msgs'][0].split("'")
                    data_table[prio_cat]['Global Attribute'].append(msgs[1])
                    data_table[prio_cat]['Error Message'].append(msgs[2].lstrip())
                    data_table[prio_cat]['Check level'].append(prio_dict[prio_cat])
                    file_name_old = file_name

        with open(opath_in + '/long_summary_' + prio_dict[prio_cat] + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(list(data_table[prio_cat].keys()))
            for row in zip(data_table[prio_cat]['File'], data_table[prio_cat]['Check level'],
                           data_table[prio_cat]['Global Attribute'], data_table[prio_cat]['Error Message']):
                writer.writerow((list(row)))
    return


def create_output_summary(file_counter, opath, check_types_in):
    """main function to create summary output"""

    if 'atmodat' in check_types_in:
        json_summary = pd.DataFrame()
    else:
        json_summary = None

    std_name_table = None
    if 'CF' in check_types_in:
        cf_errors = 0
    else:
        cf_errors = None

    files = output_directory.return_files_in_directory_tree(opath)
    for file in files:
        if file.endswith("_result.json") and isinstance(json_summary, pd.DataFrame):
            json_summary = json_summary.append(extract_overview_output_json(file),
                                               ignore_index=True)
        elif file.endswith("_CF_result.txt"):
            cf_errors, std_name_table = extracts_error_summary_cf_check(file, cf_errors)

    write_short_summary(json_summary, cf_errors, file_counter, std_name_table, opath)
    write_long_summary(json_summary, opath)
    return
