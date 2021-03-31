"""
format_checks_register.py
=========================

A register of checks at the file-level that test the format of the file
given the file path.

"""

from compliance_checker.base import Result
from checklib.register.file_checks_register import FileCheckBase


class FileIsNetCDF(FileCheckBase):
    """
    Data file is recognised as a valid netCDF file.
    """
    short_name = "File is netCDF"
    message_templates = ["File is not in required netCDF format."]
    level = "HIGH"

    def _get_result(self, primary_arg):
        from netCDF4 import Dataset

        try:
            Dataset(self._get_filepath(primary_arg))
            success = True
        except Exception:
            success = False

        messages = []

        if success:
            score = self.out_of
        else:
            score = 0
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)
