"""module to create summary of results from output of atmodat data checker"""

import json
import os
from atmodat_checklib import __version__
import pandas as pd
import atmodat_checklib.utils.output_directory_util as output_directory
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


def extracts_error_summary_cf_check(ifile_in, cf_verion_in, errors_in, warn_in, incorrect_formula_term_error_in):
    """extracts information from given txt file and returns them as a string"""
    std_name = 'Using Standard Name Table Version '
    with open(ifile_in) as f:
        data = f.read()
        for line in data.strip().split('\n'):
            if std_name in line:
                std_name_table_out = line.replace(std_name, '').split(' ')[0]
            if line.startswith('ERROR:'):
                if '4.3.3' not in line:
                    errors_in += 1
                else:
                    incorrect_formula_term_error_in = True
            elif line.startswith('WARN:'):
                warn_in += 1
            elif line.startswith('Checking against CF Version '):
                cf_verion_in.append(line.split('Checking against CF Version ')[1])

    return cf_verion_in, errors_in, warn_in, std_name_table_out, incorrect_formula_term_error_in


def write_short_summary(json_summary, cf_version, cf_errors, cf_warns, incorrect_formula_term_error_in,
                        file_counter, std_name_table_in, opath_in):
    """create file which contains the short version of the summary"""
    prio_dict = {'high_priorities': 'Mandatory', 'medium_priorities': 'Recommended', 'low_priorities': 'Optional'}
    passed_checks = {'all': [0, 0, 0, 0]}  # all, failed, missing, error
    license_list = []
    if isinstance(json_summary, pd.DataFrame):
        for prio in prio_dict.keys():
            passed_checks[prio] = [0, 0, 0, 0]  # all, failed, missing, error
            checks_prio = json_summary[prio]
            for checks in checks_prio:
                for check in checks:
                    passed_checks[prio][0] += 1
                    passed_checks['all'][0] += 1
                    if check['value'][0] == check['value'][1]:
                        passed_checks[prio][1] += 1
                        passed_checks['all'][1] += 1

                        # Find used license information
                        if check['name'] == 'Global attribute: license':
                            license_list.append(check['msgs'][0])

                    elif check['value'][0] in [0, 1]:
                        passed_checks[prio][2] += 1
                    else:
                        passed_checks[prio][3] += 1

    # write summary of results into summary file
    with open(os.path.join(opath_in, 'short_summary.txt'), 'w+') as f:
        f.write("=== Short summary === \n \n")
        f.write(f"ATMODAT Standard Compliance Checker Version: {str(__version__)}\n")
        if isinstance(json_summary, pd.DataFrame):
            cf_verion_list = list(set(cf_version))
            if len(cf_verion_list) == 1:
                cf_version_string = f"CF Version {cf_verion_list[0].split('-')[1]}"
            else:
                cf_version_string = 'multiple CF versions'
            text_out = f"Checking against: ATMODAT Standard {list(set(json_summary['testname']))[0].split(':')[1]}" \
                       f", {cf_version_string}\n"
            f.write(text_out)
        f.write(f"Checked at: {datetime.datetime.now().isoformat(timespec='seconds')}\n \n")
        f.write(f"Number of checked files: {str(file_counter)}\n")
        if isinstance(json_summary, pd.DataFrame):
            for prio in prio_dict.keys():
                f.write(f"{prio_dict[prio]} checks passed: "
                        f"{str(passed_checks[prio][1])}/{str(passed_checks[prio][0])} ({passed_checks[prio][2]} "
                        f"missing, {passed_checks[prio][3]} error(s))\n")
        if cf_version_string == 'multiple CF versions':
            f.write("!!! Checking against multiple CF Versions !!!")
        if cf_errors is not None:
            if incorrect_formula_term_error_in:
                f.write(f"CF checker errors: {str(cf_errors)} (Ignoring errors related to formula_terms in boundary "
                        f"variables. See Known Issues sections in the README.md)\n")
            else:
                f.write(f"CF checker errors: {str(cf_errors)}\n")
        if cf_warns is not None:
            f.write(f"CF checker warnings: {str(cf_warns)}")

    license_list = list(set(license_list))
    if len(license_list) != 0:
        with open(os.path.join(opath_in, 'summary_used_licences.txt'), 'w+') as f_lic:
            for license_str in license_list:
                f_lic.write(f"{license_str} \n")


def write_long_summary(json_summary_in, opath_in):

    if json_summary_in is None:
        return

    prio_cat_all = ['high_priorities', 'medium_priorities', 'low_priorities']
    prio_dict = {'high_priorities': 'mandatory', 'medium_priorities': 'recommended', 'low_priorities': 'optional'}
    files_check = list(json_summary_in['file'])

    data_table = {}
    for prio_cat in prio_cat_all:
        data_table[prio_cat] = {}
        data_prio = json_summary_in[prio_cat]
        data_table[prio_cat] = {'File': [], 'Check level': [], 'Global Attribute': [], 'Error Message': []}
        file_name_old = []
        for nf, file in enumerate(files_check):
            file_name = file.split('/')[-1].replace('_atmodat_result.json', '.nc')
            for checks in data_prio:
                for check in checks:
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

        with open(os.path.join(opath_in, 'long_summary_' + prio_dict[prio_cat] + '.csv'), 'w', newline='') as file:
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
        incorrect_formula_term_error = False
        cf_errors, cf_warns = 0, 0
        cf_version = []
    else:
        cf_errors, cf_warns = None, None
        incorrect_formula_term_error = None
        cf_version = None

    files = output_directory.return_files_in_directory_tree(opath)
    for file in files:
        if file.endswith("_result.json") and isinstance(json_summary, pd.DataFrame):
            json_summary = pd.concat([json_summary, pd.DataFrame.from_dict(extract_overview_output_json(file),
                                                                           orient='index').transpose()], axis=0)
        elif file.endswith("_CF_result.txt"):
            cf_version, cf_errors, cf_warns, std_name_table, incorrect_formula_term_error = \
                extracts_error_summary_cf_check(file, cf_version, cf_errors, cf_warns, incorrect_formula_term_error)

    write_short_summary(json_summary, cf_version, cf_errors, cf_warns, incorrect_formula_term_error, file_counter,
                        std_name_table, opath)
    write_long_summary(json_summary, opath)
    return
