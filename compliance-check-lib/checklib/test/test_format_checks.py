"""
test_format_checks.py
===================

Unit tests for the contents of the checklib.register.format_checks_register module.

"""

from checklib.register.format_checks_register import *

TEST_FILES = [
    'checklib/test/example_data/nc_file_checks_data/temp-max_sres-a1b_ukcp18-land-prob-25km_sample_day_19981201-19991130.nc',
    'checklib/test/example_data/nc_file_checks_data/simple_nc4.nc'
    ]

def test_NCFileIsReadableCheck_NETCDF3_CLASSIC_success():
    x = NCFileIsReadableCheck(kwargs={'file_format': 'NETCDF3_CLASSIC'})
    resp = x(TEST_FILES[0])
    assert(resp.value == (1, 1))

def test_NCFileIsReadableCheck_NETCDF4_CLASSIC_success():
    x = NCFileIsReadableCheck(kwargs={'file_format': 'NETCDF4_CLASSIC'})
    resp = x(TEST_FILES[1])
    assert (resp.value == (1, 1))

def test_NCFileIsReadableCheck_NETCDF4_CLASSIC_fail():
    x = NCFileIsReadableCheck(kwargs={'file_format': 'NETCDF4_CLASSIC'})
    resp = x(TEST_FILES[0])
    assert(resp.value == (0, 1))

def test_NCFileIsReadableCheck_NETCDF3_CLASSIC_fail():
    x = NCFileIsReadableCheck(kwargs={'file_format': 'NETCDF3_CLASSIC'})
    resp = x(TEST_FILES[1])
    assert (resp.value == (0, 1))

def test_NCFileSoftwareCheck_success():
    x = NCFileSoftwareCheck(kwargs={})
    resp = x(TEST_FILES[1])
    assert (resp.value == (2, 2))

def test_NCFileSoftwareCheck_fail():
    x = NCFileSoftwareCheck(kwargs={})
    resp = x('checklib/test/example_data/nc_file_checks_data/simple_nc.cdl')
    assert (resp.value == (0, 2))
