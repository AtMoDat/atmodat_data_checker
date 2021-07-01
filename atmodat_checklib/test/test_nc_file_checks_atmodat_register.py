"""
test_nc_utils.py
======================
Unit tests for the contents of the atmodat_checklib.register.nc_file_checks_atmodat_register module.
"""
import numpy as np
import pytest
from atmodat_checklib.register.nc_file_checks_atmodat_register import *
import datetime
import pytz


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


def test_cf_conventions_in_range(empty_netcdf):
    min_range, max_range = 1.4, 1.8
    for val in np.linspace(min_range, max_range, 5):
        ds = write_global_attribute(empty_netcdf, Conventions='CF-' + str(val) + 'ATMODAT-1.0')
        x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "CF",
                                            "min_version": min_range, "max_version": max_range})
        resp = x(ds)
        assert(resp.value == (2, 2)), resp.msgs
        ds.close()


def test_cf_conventions_greater_than_range(empty_netcdf):
    min_range, max_range = 1.4, 1.8
    val = 1.9
    ds = write_global_attribute(empty_netcdf, Conventions='CF-' + str(val) + 'ATMODAT-1.0')
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "CF",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp.value == (1, 2)), resp.msgs
    ds.close()


def test_cf_conventions_less_than_range(empty_netcdf):
    min_range, max_range = 1.4, 1.8
    val = 1.3
    ds = write_global_attribute(empty_netcdf, Conventions='CF-' + str(val) + 'ATMODAT-1.0')
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "CF",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp.value == (1, 2)), resp.msgs
    ds.close()


def test_cf_conventions_conventions_missing(empty_netcdf):
    min_range, max_range = 1.4, 1.8
    ds = write_global_attribute(empty_netcdf)
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "CF",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp.value == (0, 2)), resp.msgs
    ds.close()


def test_atmodat_conventions_not_present(empty_netcdf):
    min_range, max_range = 3.0, 3.0
    ds = write_global_attribute(empty_netcdf)
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "ATMODAT",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp.value == (0, 2)), resp.msgs
    ds.close()


def test_atmodat_conventions_version_match(empty_netcdf):
    min_range, max_range = 3.0, 3.0
    val = 3.0
    ds = write_global_attribute(empty_netcdf, Conventions='ATMODAT-' + str(val) + 'CF-1.0')
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "ATMODAT",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp.value == (2, 2)), resp.msgs
    ds.close()


def test_atmodat_conventions_version_no_match(empty_netcdf):
    min_range, max_range = 3.0, 3.0
    val = 2.0
    ds = write_global_attribute(empty_netcdf, Conventions='ATMODAT-' + str(val) + 'CF-1.0')
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "ATMODAT",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp.value == (1, 2)), resp.msgs
    ds.close()


def test_global_attr_type_check_missing(empty_netcdf):
    ds = write_global_attribute(empty_netcdf)
    x = GlobalAttrTypeCheck(kwargs={"status": "mandatory", "attribute": "foo", "type": str})
    resp = x(ds)
    assert(resp.value == (0, 3)), resp.msgs
    ds.close()


def test_global_attr_type_check_empty(empty_netcdf):
    ds = write_global_attribute(empty_netcdf, foo='')
    x = GlobalAttrTypeCheck(kwargs={"status": "mandatory", "attribute": "foo", "type": str})
    resp = x(ds)
    assert(resp.value == (1, 3)), resp.msgs
    ds.close()


def test_global_attr_type_check_wrong_type(empty_netcdf):
    type_dict = {str: [1, 1.0], int: ['foo', 1.0], float: ['foo', 1]}
    for key, values in type_dict.items():
        for value in values:
            ds = write_global_attribute(empty_netcdf, foo=value)
            x = GlobalAttrTypeCheck(kwargs={"status": "mandatory", "attribute": "foo", "type": key})
            resp = x(ds)
            assert(resp.value == (2, 3)), resp.msgs
            ds.close()


def test_global_attr_type_check_correct_type(empty_netcdf):
    type_dict = {str: 'bar', int: 1, float: 1.0}
    for key, value in type_dict.items():
        ds = write_global_attribute(empty_netcdf, foo=value)
        x = GlobalAttrTypeCheck(kwargs={"status": "mandatory", "attribute": "foo", "type": key})
        resp = x(ds)
        assert(resp.value == (3, 3)), resp.msgs
        ds.close()


def test_date_iso8601_check_missing(empty_netcdf):
    ds = write_global_attribute(empty_netcdf)
    x = DateISO8601Check(kwargs={"status": "recommended", "attribute": "creation_date"})
    resp = x(ds)
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
        assert(resp.value == (1, 2)), resp.msgs
        ds.close()