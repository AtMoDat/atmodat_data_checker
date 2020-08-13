"""
test_nc_var_checks.py
======================

Unit tests for the contents of the checklib.register.nc_var_checks_register module.

"""

from checklib.code.errors import ParameterError
from checklib.register.nc_var_checks_register import *
from netCDF4 import Dataset


def test_NCArrayMatchesVocabTermsCheck_success():
    x = NCArrayMatchesVocabTermsCheck(kwargs={'var_id': 'geo_region',
                                              'pyessv_namespace': 'river_basin'},
                                      vocabulary_ref='ukcp:ukcp18')
    resp = x(Dataset('checklib/test/example_data/river_basin_good_order.nc'))
    assert(resp.value == (1, 1)), resp.msgs


def test_NCArrayMatchesVocabTermsCheck_fail():
    x = NCArrayMatchesVocabTermsCheck(kwargs={'var_id': 'geo_region',
                                              'pyessv_namespace': 'river_basin'},
                                      vocabulary_ref='ukcp:ukcp18')
    resp = x(Dataset('checklib/test/example_data/river_basin_bad_order.nc'))
    assert(resp.value == (0, 1)), resp.msgs
