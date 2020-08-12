"""
test_ess_vocab_checks.py
========================

Unit tests for the contents of the checklib.cvs.ess_vocabs module.

"""

# Set local directory as store for `pyessv-archive` controlled vocabs
# MUST DO THIS BEFORE other imports
import os
os.environ['PYESSV_ARCHIVE_HOME'] = 'cc-vocab-cache/pyessv-archive-eg-cvs'

import pyessv
import pytest
from checklib.cvs.ess_vocabs import *
from netCDF4 import Dataset


def test_get_value_string_lookup_success_1():
    x = ESSVocabs('ukcp', 'ukcp18')
    resp = x.get_value('variable:tasAnom')
    assert(resp == 'tasAnom')

    # Check full term path works
    resp = x.get_value('ukcp:ukcp18:variable:tasAnom')
    assert(resp == 'tasAnom')


def test_get_value_string_lookup_data_success_2():
    x = ESSVocabs('ukcp', 'ukcp18')
    resp = x.get_value('coordinate:time', property='data')

    assert("units" in resp)
    assert(resp['units'] == 'days since 1970-01-01 00:00:00')


def test_get_value_string_lookup_failure_1():
    x = ESSVocabs('ukcp', 'ukcp18')
    lookup = 'domain:dog'
    try:
        x.get_value(lookup)
    except Exception as err:
        assert(str(err) == "Could not get value of term based on vocabulary lookup: '{}'.".format(lookup))


def test_get_terms():
    x = ESSVocabs('ukcp', 'ukcp18')
    collection = 'river_basin'
    terms = x.get_terms(collection)

    assert(str(terms[-1]) == 'ukcp:ukcp18:river-basin:western-wales')
    assert(isinstance(terms[-1], pyessv.Term))

    # Check alphabetical
    terms_strings = [str(term) for term in terms]
    alpha_terms_strings = sorted(terms_strings)
    assert(terms_strings == alpha_terms_strings)


def test_get_terms_fail():
    x = ESSVocabs('ukcp', 'ukcp18')
    collection = 'RUBBISH'
    with pytest.raises(Exception):
        x.get_terms(collection)
