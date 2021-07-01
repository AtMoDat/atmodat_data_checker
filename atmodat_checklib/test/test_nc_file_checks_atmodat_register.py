"""
test_nc_utils.py
======================
Unit tests for the contents of the atmodat_checklib.register.nc_file_checks_atmodat_register module.
"""
import numpy as np
import pytest
from atmodat_checklib.register.nc_file_checks_atmodat_register import *


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


def test_cf_conventions_less_than_range(empty_netcdf):
    min_range, max_range = 1.4, 1.8
    val = 1.3
    ds = write_global_attribute(empty_netcdf, Conventions='CF-' + str(val) + 'ATMODAT-1.0')
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "CF",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp.value == (1, 2)), resp.msgs


def test_cf_conventions_conventions_not_present(empty_netcdf):
    min_range, max_range = 1.4, 1.8
    ds = write_global_attribute(empty_netcdf)
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "CF",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp.value == (0, 2)), resp.msgs


def test_atmodat_conventions_not_present(empty_netcdf):
    min_range, max_range = 3.0, 3.0
    ds = write_global_attribute(empty_netcdf)
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "ATMODAT",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp.value == (0, 2)), resp.msgs


def test_atmodat_conventions_version_match(empty_netcdf):
    min_range, max_range = 3.0, 3.0
    val = 3.0
    ds = write_global_attribute(empty_netcdf, Conventions='ATMODAT-' + str(val) + 'CF-1.0')
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "ATMODAT",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp.value == (2, 2)), resp.msgs


def test_atmodat_conventions_version_no_match(empty_netcdf):
    min_range, max_range = 3.0, 3.0
    val = 2.0
    ds = write_global_attribute(empty_netcdf, Conventions='ATMODAT-' + str(val) + 'CF-1.0')
    x = ConventionsVersionCheck(kwargs={"status": "mandatory", "attribute": "Conventions", "convention_type": "ATMODAT",
                                        "min_version": min_range, "max_version": max_range})
    resp = x(ds)
    assert(resp.value == (1, 2)), resp.msgs
