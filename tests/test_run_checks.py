import os
from run_checks import run_checks
import atmodat_checklib.result_output.output_directory as output_directory
from atmodat_checklib.result_output.summary_creation import extract_overview_output_json, \
    extracts_error_summary_cf_check
import pandas as pd
from atmodat_checklib.utils.env_util import set_env_variables
from git import Repo
from pathlib import Path
import json


prio_dict = {'high_priorities': 'Mandatory', 'medium_priorities': 'Recommended', 'low_priorities': 'Optional'}
udunits2_xml_path, pyessv_archive_home = set_env_variables()
os.environ['PYESSV_ARCHIVE_HOME'] = pyessv_archive_home
os.environ['UDUNITS2_XML_PATH'] = udunits2_xml_path


def run_checks_on_files(tmpdir, ifiles):
    atmodat_base_path = os.path.join(str(Path(__file__).resolve().parents[1]), '')
    run_checks(ifiles, False, ['atmodat', 'CF'], 'auto', tmpdir, atmodat_base_path)
    json_summary, cf_errors = create_output_summary(tmpdir)

    passed_checks = {}
    for file_json in json_summary.keys():
        passed_checks[file_json] = {}
        if isinstance(json_summary[file_json], pd.DataFrame):
            for prio in prio_dict.keys():
                passed_checks[file_json][prio] = [0, 0]
                checks_prio = json_summary[file_json][prio]
                for checks in checks_prio:
                    for check in checks:
                        passed_checks[file_json][prio][0] += 1
                        if check['value'][0] == check['value'][1]:
                            passed_checks[file_json][prio][1] += 1
    return passed_checks


def create_output_summary(opath):
    """main function to create summary output"""
    json_summary_out, cf_errors_out, incorrect_formula_term_error = {}, {}, None
    files = output_directory.return_files_in_directory_tree(opath)
    for file in files:
        if file.endswith("_result.json"):
            json_summary_out[file] = pd.DataFrame()
            json_summary_out[file] = json_summary_out[file].append(extract_overview_output_json(file),
                                                                   ignore_index=True)
        elif file.endswith("_CF_result.txt"):
            cf_errors_out[file] = 0
            cf_errors_out[file], std_name_table, incorrect_formula_term_error = \
                extracts_error_summary_cf_check(file, cf_errors_out[file], incorrect_formula_term_error)
    return json_summary_out, cf_errors_out


def test_expected_attributes_present(tmpdir):

    for check in ['atmodat', 'CF']:
        tmpdir.mkdir(check)
    tmp_dir_test = os.path.join(str(tmpdir), '')

    tmpdir_demo = tmpdir.mkdir('demo_data')
    git_url = 'https://github.com/AtMoDat/demo_data.git'
    Repo.clone_from(git_url, tmpdir_demo)
    with open(os.path.join(str(tmpdir_demo), 'test_results_atmodat_standard_latest.json'), 'r') as json_file:
        file_check = json.load(json_file)
    file_list = [os.path.join(str(tmpdir_demo), f) for f in os.listdir(tmpdir_demo) if f.endswith('.nc')]
    passed_json_checks = run_checks_on_files(tmp_dir_test, file_list)

    for file in file_check.keys():
        for json_file in passed_json_checks.keys():
            if file.rstrip('.nc') in json_file:
                for prio_check in file_check[file].keys():
                    error_string_out = 'Number of expected ' + prio_dict[prio_check] + ' checks to pass in ' \
                                       + file + ' incorrect!'
                    assert(passed_json_checks[json_file][prio_check] == file_check[file][prio_check]), error_string_out
