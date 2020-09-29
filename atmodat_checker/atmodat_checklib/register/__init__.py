"""
__init__.py
==========================

init file

"""

from atmodat_checklib.register.nc_file_checks_atmodat_register import *
from atmodat_checklib.register.format_checks_atmodat_register import *


def get_check_class(id):
    """
    Find check class matching `id` in the various registers.

    :param id: identifier for check (matches class name) [string]
    :return: class
    """
    try:
        assert id.endswith("Check")
        return eval(id)
    except Exception:
        raise Exception("Cannot identify Check with identifier: {}".format(id))
