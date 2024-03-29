"""
nc_file_checks_register.py
==========================

A register of checks for NetCDF4 files.

"""

from netCDF4 import Dataset
from compliance_checker.base import Result, BaseCheck
from checklib.register.callable_check_base import CallableCheckBase
from atmodat_checklib.utils import nc_util
from checklib.cvs.ess_vocabs import ESSVocabs
from checklib.code.errors import FileError


class NCFileCheckBase(CallableCheckBase):
    """Base class for all NetCDF4 File Checks (that work on a file path)."""

    def _check_primary_arg(self, primary_arg):
        if not isinstance(primary_arg, Dataset):
            raise FileError("Object for testing is not a netCDF4 Dataset: {}".format(str(primary_arg)))

    def _atmodat_status_to_level(self, status):
        """
        jkretz: At the moment, low-level checks are not outputted by the IOOS compliance checker.
        The weight of the low-level checks is set to 4 (BaseCheck.HIGH+BaseCheck.LOW) to circumvent this
        """
        atmodat_status = {'mandatory': BaseCheck.HIGH, 'recommended': BaseCheck.MEDIUM,
                          'optional': BaseCheck.HIGH + BaseCheck.LOW}
        self.level = atmodat_status[status]


class LicenseAttrCheck(NCFileCheckBase):
    """
    The global attribute '{attribute}' must have a valid type '{type}' and should not be empty.
    """
    short_name = "Global attribute: {attribute}"
    defaults = {}
    required_args = ['attribute', 'type', 'status']
    message_templates = ["'{attribute}' global attribute is not present",
                         "'{attribute}' global attribute check against unsupported type {type} "
                         "(allowed types are: str, int, float)",
                         "'{attribute}' global attribute is empty",
                         "'{attribute}' global attribute value does not match type {type}"]

    def _get_result(self, primary_arg):
        self._atmodat_status_to_level(self.kwargs["status"])
        ds = primary_arg

        score = nc_util.check_global_attr_type(ds, self.kwargs["attribute"], self.kwargs["type"],)
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])
        else:
            messages.append(getattr(ds, self.kwargs["attribute"]).strip())

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class ConventionsVersionCheck(NCFileCheckBase):
    """
    The version number given in the global attribute '{attribute}' must be within a valid range
    """
    short_name = "{convention_type} version number in valid range"
    defaults = {}
    required_args = ['attribute', 'convention_type', 'min_version', 'max_version']
    message_templates = ["'{attribute}' global attribute is not present", "", ""]

    def _get_result(self, primary_arg):
        self._atmodat_status_to_level(self.kwargs["status"])
        ds = primary_arg

        score = nc_util.check_conventions_version_number(ds, self.kwargs["attribute"], self.kwargs["convention_type"],
                                                         self.kwargs["min_version"], self.kwargs["max_version"])
        messages = []

        if self.kwargs["convention_type"] == 'CF':
            self.message_templates[1] = "'{attribute}' {convention_type} Convention information not present"
            self.message_templates[2] = "'{attribute}' {convention_type} Convention version not in valid range of " \
                                        "{min_version} to {max_version}"
        elif self.kwargs["convention_type"] == 'ATMODAT':
            self.message_templates[1] = "'{attribute}' {convention_type} Standard information not present"
            self.message_templates[2] = "'{attribute}' {convention_type} Standard version given is not in accordance " \
                                        "with performed checks"

        self._define_messages(messages)

        if score == 0:
            # The existence of the "Conventions" attribute is already checked by GlobalAttrTypeCheck, so no output of an
            # error message is needed here
            return
        else:
            if score < self.out_of:
                messages.append(self.get_messages()[score])

            return Result(self.level, (score, self.out_of),
                          self.get_short_name(), messages)


class GlobalAttrResolutionFormatCheck(NCFileCheckBase):
    """
    The global attribute '{attribute}' must be in number+unit format .
    """
    short_name = "Global attribute: {attribute} format check"
    defaults = {}
    required_args = ['attribute']
    message_templates = ["'{attribute}' global attribute is not present",
                         "'{attribute}' No valid value+unit combination (missing value)",
                         "'{attribute}' No valid value+unit combination (missing unit)",
                         "'{attribute}' No valid value+unit combination (invalid unit)"]

    def _get_result(self, primary_arg):
        self._atmodat_status_to_level(self.kwargs["status"])
        ds = primary_arg

        score = nc_util.check_global_attribute_resolution_format(ds, self.kwargs["attribute"])
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class GlobalAttrTypeCheck(NCFileCheckBase):
    """
    The global attribute '{attribute}' must have a valid type '{type}' and should not be empty.
    """
    short_name = "Global attribute: {attribute}"
    defaults = {}
    required_args = ['attribute', 'type', 'status']
    message_templates = ["'{attribute}' global attribute is not present",
                         "'{attribute}' global attribute check against unsupported type {type} "
                         "(allowed types are: str, int, float)",
                         "'{attribute}' global attribute is empty",
                         "'{attribute}' global attribute value does not match type {type}"]

    def _get_result(self, primary_arg):
        self._atmodat_status_to_level(self.kwargs["status"])
        ds = primary_arg

        score = nc_util.check_global_attr_type(ds, self.kwargs["attribute"], self.kwargs["type"],)
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
    message_templates = ["'{attribute}' global attribute is not present",
                         "'{attribute}' global attribute value does not match ISO8601"]

    def _get_result(self, primary_arg):
        self._atmodat_status_to_level(self.kwargs["status"])
        ds = primary_arg

        score = nc_util.check_global_attr_iso8601(ds, self.kwargs["attribute"])
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class GlobalAttrVocabCheckByStatus(NCFileCheckBase):
    """
    The global attribute '{attribute}' must exist (if `status` = mandatory) and have a valid value
    from the relevant vocabulary.
    """
    short_name = "Global attribute: {attribute}"
    defaults = {"vocab_lookup": "canonical_name"}
    required_args = ['attribute', 'status']
    message_templates = ["'{attribute}' global attribute is not present",
                         "'{attribute}' global attribute value is invalid"]

    def _get_result(self, primary_arg):
        self._atmodat_status_to_level(self.kwargs["status"])
        ds = primary_arg
        vocabs = ESSVocabs(*self.vocabulary_ref.split(":")[:2])

        score = vocabs.check_global_attribute(ds, self.kwargs["attribute"], vocab_lookup=self.kwargs["vocab_lookup"])
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)
