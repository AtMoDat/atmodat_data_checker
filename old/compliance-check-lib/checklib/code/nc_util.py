"""
nc_util.py
=========

Utilities to support compliance checker classes - working with
netCDF4 Dataset objects.

"""

import re
import numpy as np



def get_main_variable(ds):
    """
    Gets the main variable from a NetCDF4 Dataset. The main
    variable is determined as that which has the biggest shape/size.
    If there is more than one variable of the biggest size it raises
    an Exception.

    :param ds: netCDF4 Dataset object
    :return: netCDF4 Variable object
    """
    dsv = ds.variables
    sizes = {}

    for ncvar in dsv:
        sizes[ncvar] = dsv[ncvar].size

    mx_size = max(sizes.values())
    if list(sizes.values()).count(mx_size) > 1:
        raise Exception("More than one 'main' variable found in netCDF4 file.")

    return [dsv[ncvar] for ncvar, size in sizes.items() if dsv[ncvar].size == mx_size][0]


def check_main_variable_type(ds, datatype):
    """
    Checks variables in a NetCDF Dataset and returns boolean regarding
    whether the main variable is of the required type. The main
    variable is determined as that which has the biggest shape/size.

    :param ds: netCDF4 Dataset object
    :paran datatype: the type of the variable, this should be a numpy type: string
    :return: boolean
    """
    main_var = get_main_variable(ds)
    return main_var.dtype == np.dtype(datatype)


def is_there_only_one_main_variable(ds):
    """
    Checks variables in a NetCDF Dataset and returns boolean regarding
    whether there is only one main variable. It believes the main variable
    has the biggest shape/size. If two are the same size it returns False.

    :param ds: netCDF4 Dataset object
    :return: boolean
    """
    try:
        get_main_variable(ds)
        return True
    except:
        return False


def check_global_attr_type(ds, attr, attr_type, status):
    """
    Checks globals attribute values in a NetCDF Dataset and returns integer regarding
    whether the `attr` matches `attr_type`.

    Note: Problems may occur with numpy types (int32, int 64, ...)

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :param attr_type: a numpy type [string]
    :param status: status (mandatory or sth. else) [string]
    :return: Integer (0: not found; 1: found (incorrect type); 2: found and correct type.
    """
    if status == "mandatory" and not attr in ds.ncattrs():
        return 0

    global_attr = getattr(ds, attr)

    if np.dtype(type(global_attr)) != np.dtype(attr_type):
        return 1

    return 2


def check_global_attr_ISO8601(ds, attr):
    """
    Checks globals attribute values in a NetCDF Dataset and returns integer regarding
    whether the `attr` matches ISO8601 format.

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :return: Integer (0: incorrect format; 1: correct format).
    """
    global_attr = getattr(ds, attr)

    if np.dtype(type(global_attr)) != np.dtype(attr_type):
        return 1

    return 2


def check_global_attr_against_regex(ds, attr, regex):
    """
    Returns 0 if attribute `attr` not found, 1 if found but doesn't match
    and 2 if found and matches `regex`.

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :regex: a regular expression definition [string]
    :return: an integer (see above)
    """
    if attr not in ds.ncattrs():
        return 0
    if not re.match("^{}$".format(regex), getattr(ds, attr), re.DOTALL):
        return 1
    # Success
    return 2


def check_variable_type(ds, var_id, datatype):
    """
    Checks variables in a NetCDF Dataset and returns boolean regarding
    whether the variable `var_id` is of the required type.

    :param ds: netCDF4 Dataset object
    :param var_id: Variable ID.
    :paran datatype: the type of the variable, this should be a numpy type: string
    :return: boolean
    """
    return (is_variable_in_dataset(ds, var_id) and
            ds.variables[var_id].dtype == np.dtype(datatype))


def is_variable_in_dataset(ds, var_id):
    """
    Checks that variable with name `var_id` exists in the file.
    Returns True if variable is in the dataset.

    :param ds: netCDF4 Dataset object
    :paran var_id: the variable ID.
    :return: boolean
    """
    return var_id in ds.variables


def variable_is_within_valid_bounds(ds, var_id, minimum, maximum):
    """
    Checks whether variable `var_id` is out of bounds set by arguments
    `minimum` and `maximum`.

    :param ds: netCDF4 Dataset object
    :paran var_id: the variable ID.
    :param minimum: the minimum allowed value (a number)
    :param maximum: the maximum allowed value (a number)
    :return: boolean
    """
    if var_id not in ds.variables: return False

    data = ds.variables[var_id][:]
    mn, mx = data.min(), data.max()

    if mn < minimum or mx > maximum:
        return False

    return True


def check_nc_attribute(variable, attr, expected_value):
    """
    Checks that attribute ``attr`` is in the netCDF4 Variable and the value
    matches the expected value. Returns True for success and False for failure.

    If the attribute is `_FillValue` then use `numpy.isclose()` to do the
    comparison - to cope with Floating Point errors.

    :param variable: netCDF4 Variable instance.
    :param attr: attribute name (string).
    :param expected_value: value that we expect to find (varied type).
    :return: boolean.
    """
    value = getattr(variable, attr)

    if attr == "_FillValue":
        # Check values are close to handle floating point errors
        if np.isclose(value, expected_value):
            return True

    elif value == expected_value:
        return True

    return False
