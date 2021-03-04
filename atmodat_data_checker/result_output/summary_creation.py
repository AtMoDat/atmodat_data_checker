"""module to create summary of results from atmodat data checker"""

import os
import pandas as pd
import json

import atmodat_data_checker.result_output.output_directory as output_directory


def delete_file(file):
    """deletes given file"""
    os.remove(output_directory.opath + file)


def extract_overview_output_json(ifile_in):
    """extracts information from given json file and returns them as a dictionary"""
    keys = ['data_file','check_type','scored_points','possible_points','error','name', 'msgs']
    summary = {key: None for key in keys}

    summary['error'] = []
    summary['name'] = []
    summary['msgs'] = []

    summary['name'][0] = 1

    with open(output_directory.opath + ifile_in) as f:
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
                    elif key_2 == 'high_priorities':
                        for index, item in enumerate(value_2):
                            for key_3, value_3 in item.items():
                                if key_3 == 'value' and value_3[0] != value_3[0]:
                                    summary['error'][index] = True
                                elif key_3 == 'value':
                                    summary['error'][index] = False
                                elif key_3 == 'name':
                                    print(summary['name'])
                                    print(value_3)
                                    summary['name'][index] = str(value_3)
                                elif key_3 == 'msgs':
                                    summary['msgs'][index]= str(value_3)
    print(summary)
    if summary['error']:
        delete_file(ifile_in)

    return summary


def extracts_error_summary_cf_check(ifile_in):
    """extracts information from given txt file and returns them as a string"""
    substr = 'ERRORS detected:'
    with open(output_directory.opath + ifile_in) as f:
        data = f.read()
        for line in data.strip().split('\n'):
            if substr in line:
                return line.split(':')[-1].strip()


def create_output_summary():
    json_summary = pd.DataFrame()
    cf_errors = 0
    for file in os.listdir(output_directory.opath):
        print(file)
        if file.endswith("_result.json"):
            json_summary = json_summary.append(extract_overview_output_json(file),
                                               ignore_index=True)
        elif file.endswith("_cfchecks_result.txt"):
            cf_errors = cf_errors + int(extracts_error_summary_cf_check(file))

    scored_points = [str(int(json_summary['scored_points'].sum()))]
    possible_points = [str(int(json_summary['possible_points'].sum()))]

    check_types = ["mandatory", "recommended", "optional"]

    # Write summary of results into summary file 
    with open(output_directory.opath + 'short_summary.txt', 'w+') as f:
        f.write("This is a summary of the results from the atmodat data checker. \n")
        f.write("Version of the checker: " + str(1.0) + "\n \n")
        f.write("Total scored points: " + scored_points[0] + '/' + possible_points[0] + '\n')

        for index, check in enumerate(check_types):
            scored_points.append(str(
                int(json_summary['scored_points'].loc[json_summary['check_type'] == check].sum())))
            possible_points.append(str(int(
                json_summary['possible_points'].loc[json_summary['check_type'] == check].sum())))
            f.write("Total scored " + check + " points: " + scored_points[index + 1] + '/' +
                    possible_points[index + 1] + '\n')

        f.write("Total number CF checker errors: " + str(cf_errors))