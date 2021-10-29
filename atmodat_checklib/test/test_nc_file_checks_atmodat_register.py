"""
test_nc_file_checks_atmodat_register.py
======================
Unit tests for the contents of the atmodat_checklib.register.nc_file_checks_atmodat_register module.
"""


import numpy as np
import pytest
import datetime
import pytz
import json
from netCDF4 import Dataset
import os
from atmodat_checklib.utils.env_util import set_env_variables


msgs_incorrect = "Incorrect output message"
attribute_list = ['featureType', 'frequency', 'nominal_resolution', 'realm', 'source_type']


udunits2_xml_path, pyessv_archive_home = set_env_variables()
os.environ['PYESSV_ARCHIVE_HOME'] = pyessv_archive_home
os.environ['UDUNITS2_XML_PATH'] = udunits2_xml_path
from atmodat_checklib.register.nc_file_checks_atmodat_register import ConventionsVersionCheck, \
    GlobalAttrTypeCheck, DateISO8601Check, GlobalAttrResolutionFormatCheck, GlobalAttrVocabCheckByStatus  # noqa: E402


@pytest.fixture(scope="session")
def empty_netcdf(tmpdir_factory):
    nc_file = tmpdir_factory.mktemp("netcdf").join("tmp.nc")
    Dataset(nc_file, 'w')
    return nc_file


def write_global_attribute(empty_netcdf, **kwargs):
    f = Dataset(empty_netcdf, 'w')
    for key, value in kwargs.items():
        f.setncattr(key, value)
    return f


def assert_output_msgs_len(resp_in):
    msgs = resp_in.msgs
    if resp_in.value[0] == resp_in.value[1]:
        assert(len(msgs) == 0)
    else:
        assert(len(msgs[0].split("'")) == 3), "Incorrect format of error message"


def load_cv_json(att_in):
    ipath_json = 'AtMoDat_CVs/AtMoDat_CV_json/'
    with open(ipath_json + 'AtMoDat_' + att_in + '.json') as jsonFile:
        json_object = json.load(jsonFile)
        jsonFile.close()
    return json_object[att_in]


def test_controlled_vocab_correct(empty_netcdf):
    for att in attribute_list:
        cv_elements = load_cv_json(att)
        for cv_element in cv_elements:
            ds = write_global_attribute(empty_netcdf, **{att: cv_element})
            x = GlobalAttrVocabCheckByStatus(kwargs={"attribute": att, "vocab_lookup": att + ":label",
                                                     "vocabulary_ref": "atmodat:atmodat", "status": "optional"})
            resp = x(ds)
            assert_output_msgs_len(resp)
            assert(resp.value == (2, 2)), resp.msgs
            ds.close()


def test_controlled_vocab_incorrect(empty_netcdf):
    for att in attribute_list:
        cv_elements = load_cv_json(att)
        for cv_element in cv_elements:
            ds = write_global_attribute(empty_netcdf, **{att: cv_element + 'bla'})
            x = GlobalAttrVocabCheckByStatus(kwargs={"attribute": att, "vocab_lookup": att + ":label",
                                                     "vocabulary_ref": "atmodat:atmodat", "status": "optional"})
            resp = x(ds)
            assert_output_msgs_len(resp)
            assert(resp.value == (1, 2)), resp.msgs
            ds.close()


def test_controlled_vocab_missing(empty_netcdf):
    for att in attribute_list:
        ds = write_global_attribute(empty_netcdf)
        x = GlobalAttrVocabCheckByStatus(kwargs={"attribute": att, "vocab_lookup": att + ":label",
                                                 "vocabulary_ref": "atmodat:atmodat", "status": "optional"})
        resp = x(ds)
        assert_output_msgs_len(resp)
        assert(resp.value == (0, 2)), resp.msgs
        ds.close()


def test_cf_conventions_in_range(empty_netcdf):
    min_range, max_range = 1.4, 1.8
    for val in np.linspace(min_range, max_range, 5):
        ds = write_global_attribute(empty_netcdf, Conventions='CF-' + str(val) + 'ATMODAT-1.0')
        x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "CF",
                                            "min_version": min_range, "max_version": max_range})
        resp = x(ds)
        assert_output_msgs_len(resp)
        assert(resp.value == (3, 3)), resp.msgs
        ds.close()


def test_cf_conventions_greater_than_range(empty_netcdf):
    min_range, max_range = 1.4, 1.8
    val = 1.9
    ds = write_global_attribute(empty_netcdf, Conventions='CF-' + str(val) + 'ATMODAT-1.0')
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "CF",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert_output_msgs_len(resp)
    assert(resp.value == (2, 3)), resp.msgs
    ds.close()


def test_cf_conventions_less_than_range(empty_netcdf):
    min_range, max_range = 1.4, 1.8
    val = 1.3
    ds = write_global_attribute(empty_netcdf, Conventions='CF-' + str(val) + 'ATMODAT-1.0')
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "CF",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert_output_msgs_len(resp)
    assert(resp.value == (2, 3)), resp.msgs
    ds.close()


def test_cf_conventions_conventions_missing(empty_netcdf):
    min_range, max_range = 1.4, 1.8
    ds = write_global_attribute(empty_netcdf)
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "CF",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp is None), resp.msgs
    ds.close()


def test_atmodat_conventions_not_present(empty_netcdf):
    min_range, max_range = 3.0, 3.0
    ds = write_global_attribute(empty_netcdf)
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "ATMODAT",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp is None), resp.msgs
    ds.close()


def test_atmodat_conventions_version_match(empty_netcdf):
    min_range, max_range = 3.0, 3.0
    val = 3.0
    ds = write_global_attribute(empty_netcdf, Conventions='ATMODAT-' + str(val) + 'CF-1.0')
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "ATMODAT",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert_output_msgs_len(resp)
    assert(resp.value == (3, 3)), resp.msgs
    ds.close()


def test_atmodat_conventions_version_no_match(empty_netcdf):
    min_range, max_range = 3.0, 3.0
    val = 2.0
    ds = write_global_attribute(empty_netcdf, Conventions='ATMODAT-' + str(val) + 'CF-1.0')
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "ATMODAT",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert_output_msgs_len(resp)
    assert(resp.value == (2, 3)), resp.msgs
    ds.close()


def test_global_attr_type_check_missing(empty_netcdf):
    ds = write_global_attribute(empty_netcdf)
    x = GlobalAttrTypeCheck(kwargs={"status": "mandatory", "attribute": "foo", "type": "str"})
    resp = x(ds)
    assert_output_msgs_len(resp)
    assert(resp.value == (0, 4)), resp.msgs
    ds.close()


def test_global_attr_type_unsupported_type(empty_netcdf):
    ds = write_global_attribute(empty_netcdf, foo='bar')
    x = GlobalAttrTypeCheck(kwargs={"status": "mandatory", "attribute": "foo", "type": "foobar"})
    resp = x(ds)
    assert_output_msgs_len(resp)
    assert(resp.value == (1, 4)), resp.msgs
    ds.close()


def test_global_attr_type_check_empty(empty_netcdf):
    ds = write_global_attribute(empty_netcdf, foo='')
    x = GlobalAttrTypeCheck(kwargs={"status": "mandatory", "attribute": "foo", "type": "str"})
    resp = x(ds)
    assert_output_msgs_len(resp)
    assert(resp.value == (2, 4)), resp.msgs
    ds.close()


def test_global_attr_type_check_wrong_type(empty_netcdf):
    type_dict = {"int": ['foo', 1.0], "str": [1, 1.0], "float": ['foo', 1]}
    for key, values in type_dict.items():
        for value in values:
            ds = write_global_attribute(empty_netcdf, foo=value)
            x = GlobalAttrTypeCheck(kwargs={"status": "mandatory", "attribute": "foo", "type": key})
            resp = x(ds)
            assert_output_msgs_len(resp)
            assert(resp.value == (3, 4)), resp.msgs
            ds.close()


def test_global_attr_type_check_correct_type(empty_netcdf):
    type_dict = {"str": 'bar', "int": 1, "float": 1.0}
    for key, value in type_dict.items():
        ds = write_global_attribute(empty_netcdf, foo=value)
        x = GlobalAttrTypeCheck(kwargs={"status": "mandatory", "attribute": "foo", "type": key})
        resp = x(ds)
        assert_output_msgs_len(resp)
        assert(resp.value == (4, 4)), resp.msgs
        ds.close()


def test_date_iso8601_check_missing(empty_netcdf):
    ds = write_global_attribute(empty_netcdf)
    x = DateISO8601Check(kwargs={"status": "recommended", "attribute": "creation_date"})
    resp = x(ds)
    assert_output_msgs_len(resp)
    assert(resp.value == (0, 2)), resp.msgs
    ds.close()


def test_date_iso8601_check_valid_timestring(empty_netcdf):
    timestring_list = [datetime.datetime.now().isoformat(),
                       datetime.datetime.now().replace(microsecond=0).isoformat(),
                       datetime.datetime.now().now().strftime('%Y-%m-%d'),
                       datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                       datetime.datetime.now().astimezone(pytz.timezone("US/Eastern")).isoformat(),
                       datetime.datetime.now().astimezone(pytz.timezone("Europe/Berlin")).isoformat()]
    for timestring in timestring_list:
        ds = write_global_attribute(empty_netcdf, creation_date=timestring)
        x = DateISO8601Check(kwargs={"status": "recommended", "attribute": "creation_date"})
        resp = x(ds)
        assert_output_msgs_len(resp)
        assert(resp.value == (2, 2)), resp.msgs
        ds.close()


def test_date_iso8601_check_invalid_timestring(empty_netcdf):
    # More example can be added here
    timestring_list = ['01.01.2021', '01/01/2021', 'Monday, June 15, 2009 1:45', '2009/6/15 13:45:30',
                       'Mon, 15 Jun 2009 20:45:30 GMT']
    for timestring in timestring_list:
        ds = write_global_attribute(empty_netcdf, creation_date=timestring)
        x = DateISO8601Check(kwargs={"status": "recommended", "attribute": "creation_date"})
        resp = x(ds)
        assert_output_msgs_len(resp)
        assert(resp.value == (1, 2)), resp.msgs
        ds.close()


def test_gobal_attr_resolution_format_check_missing(empty_netcdf):
    for attr in ['geospatial_lon_resolution', 'geospatial_lat_resolution', 'geospatial_vertical_resolution']:
        ds = write_global_attribute(empty_netcdf)
        x = GlobalAttrResolutionFormatCheck(kwargs={"status": "recommended", "attribute": attr})
        resp = x(ds)
        assert_output_msgs_len(resp)
        assert(resp.value == (0, 4)), resp.msgs
        ds.close()


def test_gobal_attr_resolution_format_check_no_value(empty_netcdf):
    for attr in ['geospatial_lon_resolution', 'geospatial_lat_resolution', 'geospatial_vertical_resolution']:
        for unit in ['W', ' W', 'W ']:
            attr_dict = {attr: unit}
            ds = write_global_attribute(empty_netcdf, **attr_dict)
            x = GlobalAttrResolutionFormatCheck(kwargs={"status": "recommended", "attribute": attr})
            resp = x(ds)
            assert_output_msgs_len(resp)
            assert(resp.value == (1, 4)), resp.msgs
            ds.close()


def test_gobal_attr_resolution_format_check_no_unit(empty_netcdf):
    for val in [1, 1.0]:
        for attr in ['geospatial_lon_resolution', 'geospatial_lat_resolution', 'geospatial_vertical_resolution']:
            attr_dict = {attr: str(val)}
            ds = write_global_attribute(empty_netcdf, **attr_dict)
            x = GlobalAttrResolutionFormatCheck(kwargs={"status": "recommended", "attribute": attr})
            resp = x(ds)
            assert_output_msgs_len(resp)
            assert(resp.value == (2, 4)), resp.msgs
            ds.close()


def test_gobal_attr_resolution_format_check_invalid_unit(empty_netcdf):
    for val in [1, 1.0]:
        for unit in ['m/ss', 'Ai']:
            for attr in ['geospatial_lon_resolution', 'geospatial_lat_resolution', 'geospatial_vertical_resolution']:
                attr_dict = {attr: str(val) + ' ' + unit}
                ds = write_global_attribute(empty_netcdf, **attr_dict)
                x = GlobalAttrResolutionFormatCheck(kwargs={"status": "recommended", "attribute": attr})
                resp = x(ds)
                assert_output_msgs_len(resp)
                assert(resp.value == (3, 4)), resp.msgs
                ds.close()


def test_gobal_attr_resolution_format_check_correct(empty_netcdf):
    for val in [1, 1.0]:
        for unit in ['W', 'J', 'm/s']:
            for attr in ['geospatial_lon_resolution', 'geospatial_lat_resolution', 'geospatial_vertical_resolution']:
                attr_dict = {attr: str(val) + ' ' + unit}
                ds = write_global_attribute(empty_netcdf, **attr_dict)
                x = GlobalAttrResolutionFormatCheck(kwargs={"status": "recommended", "attribute": attr})
                resp = x(ds)
                assert_output_msgs_len(resp)
                assert(resp.value == (4, 4)), resp.msgs
                ds.close()
