import os
from run_checks import run_checks
import atmodat_checklib.result_output.output_directory as output_directory
from atmodat_checklib.result_output.summary_creation import extract_overview_output_json, \
    extracts_error_summary_cf_check
import pandas as pd
from atmodat_checklib.utils.env_util import set_env_variables
from git import Repo
from pathlib import Path


prio_dict = {'high_priorities': 'Mandatory', 'medium_priorities': 'Recommended', 'low_priorities': 'Optional'}
udunits2_xml_path, pyessv_archive_home = set_env_variables()
os.environ['PYESSV_ARCHIVE_HOME'] = pyessv_archive_home
os.environ['UDUNITS2_XML_PATH'] = udunits2_xml_path


def run_checks_on_files(tmpdir, ifiles):
    atmodat_base_path = os.path.join(str(Path(__file__).resolve().parents[2]), '')
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
    file_list = [os.path.join(str(tmpdir_demo), f) for f in os.listdir(tmpdir_demo) if f.endswith('.nc')]
    passed_json_checks = run_checks_on_files(tmp_dir_test, file_list)

    file_check = {}
    file_check['ALL_ATMODAT_ATTRIBUTES.nc'] = {}
    file_check['ALL_ATMODAT_ATTRIBUTES.nc']['high_priorities'] = [5, 5]
    file_check['ALL_ATMODAT_ATTRIBUTES.nc']['medium_priorities'] = [19, 19]
    file_check['ALL_ATMODAT_ATTRIBUTES.nc']['low_priorities'] = [9, 9]
    file_check['NO_ATTRIBUTES.nc'] = {}
    file_check['NO_ATTRIBUTES.nc']['high_priorities'] = [3, 0]
    file_check['NO_ATTRIBUTES.nc']['medium_priorities'] = [19, 0]
    file_check['NO_ATTRIBUTES.nc']['low_priorities'] = [9, 0]
    file_check['CMIP6_ATTRIBUTES.nc'] = {}
    file_check['CMIP6_ATTRIBUTES.nc']['high_priorities'] = [5, 4]
    file_check['CMIP6_ATTRIBUTES.nc']['medium_priorities'] = [19, 10]
    file_check['CMIP6_ATTRIBUTES.nc']['low_priorities'] = [9, 2]
    file_check['MINUM_ATMODAT_ATTRIBUTES.nc'] = {}
    file_check['MINUM_ATMODAT_ATTRIBUTES.nc']['high_priorities'] = [5, 5]
    file_check['MINUM_ATMODAT_ATTRIBUTES.nc']['medium_priorities'] = [19, 0]
    file_check['MINUM_ATMODAT_ATTRIBUTES.nc']['low_priorities'] = [9, 0]
    file_check['WRONG_STANDARDNAME.nc'] = {}
    file_check['WRONG_STANDARDNAME.nc']['high_priorities'] = [5, 5]
    file_check['WRONG_STANDARDNAME.nc']['medium_priorities'] = [19, 0]
    file_check['WRONG_STANDARDNAME.nc']['low_priorities'] = [9, 0]

    for file in file_check.keys():
        for json_file in passed_json_checks.keys():
            if file.rstrip('.nc') in json_file:
                for prio_check in file_check[file].keys():
                    error_string_out = 'Number of expected ' + prio_dict[prio_check] + ' checks to pass in ' \
                                       + file + ' incorrect'
                    assert(passed_json_checks[json_file][prio_check] == file_check[file][prio_check]), error_string_out
