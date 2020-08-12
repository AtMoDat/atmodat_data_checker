import inspect

from checklib.register.callable_check_base import *
from checklib.register.file_checks_register import *
from checklib.register.nc_var_checks_register import *
from checklib.register.nc_file_checks_register import *
from checklib.register.nc_coords_checks_register import *
from checklib.register.format_checks_register import *


def get_check_class(id):
    """
    Find check class matching `id` in the various registers.

    :param id: identifier for check (matches class name) [string]
    :return: class
    """
    try:
        assert id.endswith("Check")
        return eval(id)
    except:
        raise Exception("Cannot identify Check with identifier: {}".format(id))

