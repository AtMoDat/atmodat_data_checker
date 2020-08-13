"""
nc_file_checks_register.py
==========================

A register of checks for NetCDF4 files.

"""

import os
from netCDF4 import Dataset

from compliance_checker.base import BaseCheck, Result

from checklib.register.callable_check_base import CallableCheckBase
from atmodat_checklib.utils import nc_util
# from checklib.code import nc_util, util
# from checklib.cvs.ess_vocabs import ESSVocabs
# from checklib.code.errors import FileError, ParameterError


class NCFileCheckBase(CallableCheckBase):
    "Base class for all NetCDF4 File Checks (that work on a file path."

    def _check_primary_arg(self, primary_arg):
        if not isinstance(primary_arg, Dataset):
            raise FileError("Object for testing is not a netCDF4 Dataset: {}".format(str(primary_arg)))

class GlobalAttrTypeCheck(NCFileCheckBase):
    """
    The global attribute '{attribute}' must have a valid type '{type}'.
    """
    short_name = "Global attribute: {attribute}"
    defaults = {}
    required_args = ['attribute', 'type', 'status']
    message_templates = ["'{status}' '{attribute}' global attribute is not present.",
                         "'{status}' '{attribute}' global attribute value does not match "
                         "type '{type}'."]
    level = "HIGH"

    def _get_result(self, primary_arg):
        ds = primary_arg

        score = nc_util.check_global_attr_type(ds, self.kwargs["attribute"], self.kwargs["type"],
                                                     self.kwargs["status"],)
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)

        

class DateISO8601Check(NCFileCheckBase):
    """
    The global attribute '{attribute}' must be a valid ISO 8601 date.
    """
    short_name = "Global attribute: {attribute}"
    defaults = {}
    required_args = ['attribute']
    message_templates = ["'{attribute}' global attribute value does not match ISO 8601 format"]
    level = "HIGH"

    def _get_result(self, primary_arg):
        ds = primary_arg

        score = nc_util.check_global_attr_ISO8601(ds, self.kwargs["attribute"])
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)
