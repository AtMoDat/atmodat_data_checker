"""
test_nc_coords_checks.py
======================

Unit tests for the contents of the checklib.register.nc_coords_checks_register module.

"""

import pytest
from netCDF4 import Dataset

from checklib.register.nc_coords_checks_register import *


def test_NCCoordVarHasBoundsCheck_success_1():
    x = NCCoordVarHasBoundsCheck(kwargs={"var_id": "lat"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/cmip5_example_1.nc'))
    assert(resp.value == (2, 2))


def test_NCCoordVarHasBoundsCheck_fail_1():
    x = NCCoordVarHasBoundsCheck(kwargs={"var_id": "RUBBISH"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/cmip5_example_1.nc'))
    assert(resp.value == (0, 2))

    x = NCCoordVarHasBoundsCheck(kwargs={"var_id": "height"})
    resp = x(Dataset('checklib/test/example_data/nc_file_checks_data/cmip5_example_1.nc'))
    assert(resp.value == (1, 2))


def test_NCCoordVarHasValuesInVocabCheck_success_1():
    x = NCCoordVarHasValuesInVocabCheck(kwargs={"var_id": "percentile"},
                                 vocabulary_ref="ukcp:ukcp18")
    resp = x(Dataset('checklib/test/example_data/tasAnom_rcp85_land-prob_uk_25km_percentile_mon_20001201-20011130_good_pcs.nc'))
    assert(resp.value == (2, 2))

def test_NCCoordVarHasValuesInVocabCheck_fail_1():
    x = NCCoordVarHasValuesInVocabCheck(kwargs={"var_id": "percentile"},
                                 vocabulary_ref="ukcp:ukcp18")
    resp = x(Dataset('checklib/test/example_data/tasAnom_rcp85_land-prob_uk_25km_percentile_mon_20001201-20011130_bad_pcs.nc'))
    assert(resp.value == (1, 2))


def test_NCCoordVarHasLengthInVocabCheck_success_1():
    x = NCCoordVarHasLengthInVocabCheck(kwargs={"var_id": "percentile"},
                                 vocabulary_ref="ukcp:ukcp18")
    resp = x(Dataset('checklib/test/example_data/tasAnom_rcp85_land-prob_uk_25km_percentile_mon_20001201-20011130_good_pcs.nc'))
    assert(resp.value == (2, 2))

def test_NCCoordVarHasLengthInVocabCheck_fail_1():
    x = NCCoordVarHasLengthInVocabCheck(kwargs={"var_id": "percentile"},
                                 vocabulary_ref="ukcp:ukcp18")
    resp = x(Dataset('checklib/test/example_data/tasAnom_rcp85_land-prob_uk_25km_percentile_mon_20001201-20011130_bad_pcs.nc'))
    assert(resp.value == (1, 2))