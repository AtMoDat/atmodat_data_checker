import numpy as np
import datetime


def check_global_attr_type(ds, attr, attr_type):
    """
    Checks globals attribute values in a NetCDF Dataset and returns integer regarding
    whether the `attr` matches `attr_type`.

    Note: Problems may occur with numpy types (int32, int 64, ...)

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :param attr_type: a numpy type [string]
    :return: Integer (0: not found; 1: found (incorrect type); 2: found and correct type.
    """
    if attr not in ds.ncattrs():
        return 0

    global_attr = getattr(ds, attr)

    if np.dtype(type(global_attr)) != np.dtype(attr_type):
        return 1

    return 2


def check_global_attr_iso8601(ds, attr):
    """
    Checks globals attribute values in a NetCDF Dataset and returns integer regarding
    whether the `attr` matches ISO8601 format.

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :return: Integer (0: incorrect format; 1: correct format).
    """

    if attr not in ds.ncattrs():
        return 0

    global_attr = getattr(ds, attr)

    return check_iso8601_conformity(global_attr)


def check_iso8601_conformity(date_string):

    # Timezone related replacements
    if date_string.endswith('Z'):
        date_string = date_string.replace('Z', '+00:00')
    # Replace comma with decimal point
    if ',' in date_string:
        date_string = date_string.replace(',', '.')

    try:
        datetime.datetime.fromisoformat(date_string)
        return 2
    except ValueError:
        return 1
