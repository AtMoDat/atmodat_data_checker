"""
test_file_checks.py
===================

Unit tests for the contents of the checklib.register.file_checks_register module.

"""

import re
from checklib.register.file_checks_register import *


def test_FileSizeCheck_soft_fail():
    x = FileSizeCheck(kwargs={"threshold": 1e-15, "severity": "soft"})
    resp = x('README.md')
    assert(resp.value == (0, 1))

def test_FileSizeCheck_soft_success():
    x = FileSizeCheck(kwargs={"severity": "soft"})
    resp = x('README.md')
    assert(resp.value == (1, 1))

def test_FileSizeCheck_hard_fail():
    x = FileSizeCheck(kwargs={"threshold": 1e-15, "severity": "hard"})
    resp = x('README.md')
    assert(resp.value == (0, 1))

def test_FileSizeCheck_hard_success():
    x = FileSizeCheck(kwargs={"threshold": 4, "severity": "hard"})
    resp = x('README.md')
    assert(resp.value == (1, 1))

def test_FileNameStructureCheck_regex():
    kwargs = {"delimiter": "_", "extension": ".nc", "AC": FileNameStructureCheck._ALLOWED_CHARACTERS}
    pattern = "{AC}+({delimiter}{AC}+)+\{extension}".format(**kwargs)
    regex = re.compile(pattern)

    for fpath in ("A_B.nc", "HadGEM2-ES_1990-199.a1_a-bhel_lo-2.nc",
                  "a-b_c.D3-2.1_hello-2.nc"):
        match = regex.match(fpath)
        assert(hasattr(match, "groups"))
        assert(match != None)


def test_FileNameStructureCheck_success():
    good = [
        ("checklib/test/example_data/file_checks_data/good_file.nc", {}),
        ("checklib/test/example_data/file_checks_data/good_file_as_text.txt", {"delimiter": "_",
                                                                               "extension": ".txt"}),
        ("checklib/test/example_data/file_checks_data/seaLevelAnom_marine-sim_rcp85_annual_2007-2100.nc",
         {"delimiter": "_", "extension": ".nc"})
        ]

    for fpath, kwargs in good:
        x = FileNameStructureCheck(kwargs)
        resp = x(fpath)
        assert(resp.value == (1, 1))

def test_FileNameStructureCheck_fail_1():
    bad = [
        ("checklib/test/example_data/file_checks_data/_bad_file1.nc", {}),
        ("checklib/test/example_data/file_checks_data/bad__file2.nc", {"delimiter": "_",
                                                                      "extension": ".nc"})
    ]
    for fpath, kwargs in bad:
        x = FileNameStructureCheck(kwargs)
        resp = x(fpath)
        assert(resp.value == (0, 1))

def test_FileNameRegexCheck_success():
    good = [
        ("checklib/test/example_data/file_checks_data/good_file.nc", "[a-z]+_[a-z]+\.nc"),
        ("checklib/test/example_data/file_checks_data/seaLevelAnom_marine-sim_rcp85_annual_2007-2100.nc",
         "[a-zA-Z0-9\-_]+\d{4,4}-\d{4,4}\.nc")
    ]

    for fpath, regex in good:
        x = FileNameRegexCheck({"regex": regex})
        resp = x(fpath)
        assert resp.value == (1, 1)

def test_FileNameRegexCheck_fail():
    bad = [
        ("checklib/test/example_data/file_checks_data/good_file.nc",
         "[a-zA-Z0-9\-_]+\d{4,4}-\d{4,4}\.nc"),
    ]

    for fpath, regex in bad:
        x = FileNameRegexCheck({"regex": regex})
        resp = x(fpath)
        assert resp.value == (0, 1)
