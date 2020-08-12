"""
util.py
=======

General utilities.

"""

import re


def _parse_boolean(value):
    """
    Attempts to convert a value to a boolean and returns it.
    If it fails, then it raises an Exception.

    :param value: a value
    :return: boolean
    """
    if re.match("^(on|true|yes|1)$", str(value), re.IGNORECASE):
        return True

    if re.match("^(off|false|no|0)$", str(value), re.IGNORECASE):
        return False

    raise Exception("Unable to coerce value '{}' to boolean".format(value))

