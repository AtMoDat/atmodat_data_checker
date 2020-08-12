"""
file_checks_register.py
=======================

A register of checks at the file-level.

"""

import os, re

from compliance_checker.base import Result, GenericFile

from .callable_check_base import CallableCheckBase

from checklib.code import file_util

class FileCheckBase(CallableCheckBase):
    "Base class for all File Checks (that work on a file path."

    def _get_filepath(self, primary_arg):
        """
        Return the path on disk to the dataset
        :param primary_arg: Dataset to check -- can be an instance of Dataset,
                            GenericFile or str
        :return:            Path to file on disk
        """
        try:
            return primary_arg.filepath()
        except AttributeError:
            return primary_arg

    def _check_primary_arg(self, primary_arg):
        fpath = self._get_filepath(primary_arg)
        if not os.path.isfile(fpath):
            raise Exception("File not found: {}".format(fpath))


class FileSizeCheck(FileCheckBase):
    """
    Data file {strictness} size limit: {threshold}Gbytes.
    """
    short_name = "File size {strictness} limit {threshold}Gbytes"
    defaults = {"threshold": 2, "strictness": "hard"}
    message_templates = ["Data file exceeds {strictness} limit of {threshold}Gbytes in size."]
    level = "HIGH"

    def _get_result(self, primary_arg):
        fpath = self._get_filepath(primary_arg)
        threshold = float(self.kwargs["threshold"])

        success = file_util._is_file_size_less_than(fpath, threshold * (2.**30))
        messages = []

        if success:
            score = self.out_of
        else:
            score = 0
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class FileNameStructureCheck(FileCheckBase):
    """
    File name must consist of items separated by '{delimiter}', followed by '{extension}'.
    """

    short_name = "File name structure"
    defaults = {"delimiter": "_", "extension": ".nc"}
    message_templates = [
        "File name does not follow required format of '{delimiter}' delimiters and '{extension}' extension."]
    level = "HIGH"
    _ALLOWED_CHARACTERS = '[A-Za-z0-9\-\.]'

    def _get_result(self, primary_arg):
        fpath = os.path.basename(self._get_filepath(primary_arg))
        self.kwargs["AC"] = self._ALLOWED_CHARACTERS
        regex = re.compile("{AC}+({delimiter}{AC}+)+\{extension}".format(**self.kwargs))

        success = regex.match(fpath)
        messages = []

        if success:
            score = self.out_of
        else:
            score = 0
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class FileNameRegexCheck(FileCheckBase):
    """
    File name must match regex '{regex}'
    """
    short_name = "File name regex check"
    message_templates = ["File name did not match regex '{regex}'"]
    required_parameters = {"regex": str}

    def _setup(self):
        """
        Fix backslashes in regex
        """
        self.kwargs["regex"] = self.kwargs["regex"].replace("\\\\", "\\")

    def _get_result(self, primary_arg):
        fpath = os.path.basename(self._get_filepath(primary_arg))
        messages = []
        if re.match(self.kwargs["regex"], fpath):
            score = self.out_of
        else:
            print("Failed to match {} against regex {}".format(fpath, self.kwargs["regex"]))
            score = 0
            messages.append(self.get_messages()[score])
        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)

