"""
format_checks_register.py
=========================

A register of checks at the file-level that test the format of the file
given the file path.

"""

from compliance_checker.base import Result
from atmodat_checklib.register.nc_file_checks_atmodat_register import NCFileCheckBase
from netCDF4 import Dataset


class FileIsNetCDF(NCFileCheckBase):
    """
    Data file is recognised as a valid netCDF file.
    """
    short_name = "File is netCDF"
    message_templates = ["File is not in required netCDF format."]

    def _get_result(self, primary_arg):
        self._atmodat_status_to_level(self.kwargs["status"])
        messages = []
        try:
            Dataset(self._get_filepath(primary_arg))
            score = self.out_of
        except Exception:
            score = 0
            messages.append(self.get_messages()[0])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)
