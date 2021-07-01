import numpy as np
import datetime
import re
from cfunits import Units


def check_conventions_version_number(ds, attr, conv_type, min_ver, max_ver):
    """
    Checks global attribute values in a NetCDF Dataset and returns integer
    regarding whether the `attr` matches number+unit format

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :param conv_type: Name of convention string to be checked for version
    :param min_ver: Minimum version allowed
    :param max_ver: Maximum version allowed
    :return: Integer (0: not found; 1: convention to be checked fot not found; 2: convention out of valid range;
    3: all correct)
    """

    if attr not in ds.ncattrs():
        return 0
    global_attr = getattr(ds, attr)

    version = None
    global_attr_split = global_attr.split(' ')
    for conv in global_attr_split:
        if conv_type in conv:
            version = float(re.findall(r"[+]?\d*\.\d+|\d+", conv)[0])

    if not version:
        return 1

    range_check = None
    if conv_type == 'CF':
        range_check = min_ver <= version <= max_ver
    elif conv_type == 'ATMODAT':
        range_check = (version == min_ver) and (version == max_ver)

    if not range_check:
        return 2
    else:
        return 3


def check_global_attr_type(ds, attr, attr_type):
    """
    Checks globals attribute values in a NetCDF Dataset and returns integer
    regarding whether the `attr` matches `attr_type`.

    Note: Problems may occur with numpy types (int32, int 64, ...)

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :param attr_type: a numpy type [string]
    :return: Integer (0: not found; 1: found (but empty); 2: found (incorrect type);
    3: and correct type).
    """
    if attr not in ds.ncattrs():
        return 0

    global_attr = getattr(ds, attr)

    if len(str(global_attr)) == 0:
        return 1

    if np.dtype(type(global_attr)) != np.dtype(attr_type):
        return 2

    return 3


def check_global_attr_iso8601(ds, attr):
    """
    Checks globals attribute values in a NetCDF Dataset and returns integer
    regarding whether the `attr` matches ISO8601 format.

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


def check_global_attribute_resolution_format(ds, attr):
    """
    Checks global attribute values in a NetCDF Dataset and returns integer
    regarding whether the `attr` matches number+unit format

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :return: Integer (0: incorrect format; 1: correct format).
    """

    if attr not in ds.ncattrs():
        return 0

    global_attr = getattr(ds, attr)

    return value_unit_format_conformity(global_attr)


def value_unit_format_conformity(resol_string):

    resol_string = resol_string.strip()

    if not check_value_exists(resol_string):
        # Missing value
        return 1
    else:
        val_unit_dict = split_value_unit(resol_string)
        unit_valid = True
        for val in val_unit_dict.keys():
            if not val_unit_dict[val]:
                # Missing units
                return 2
            else:
                unit_valid = True
                for units in val_unit_dict[val]:
                    if not Units(units).isvalid and not units == "''":
                        unit_valid = False
        if unit_valid:
            # All okay
            return 4
        else:
            # Unrecognized unit
            return 3


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def check_value_exists(string_in):
    var_unit_re = re.compile(r'([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)(\s*)(\S*)')
    val_ex = False
    for substring in string_in.split(' '):
        if isfloat(substring) or re.match(var_unit_re, substring):
            val_ex = True
    return val_ex


def split_value_unit(string_in):
    var_unit_re = re.compile(r'([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)(\s*)(\S*)')
    val_unit_dict_out = {}
    val_space, val_nospace = None, None
    for ns, substring in enumerate(string_in.split(' ')):
        if isfloat(substring):
            val_space = float(substring)
            val_unit_dict_out[val_space] = []
            for substring_loop in string_in.split(' ')[(ns + 1)::]:
                if not isfloat(substring_loop) and not re.match(var_unit_re, substring_loop):
                    val_unit_dict_out[val_space].append(substring_loop)
        elif re.match(var_unit_re, substring) or not isfloat(substring) and not val_space:
            if re.match(var_unit_re, substring):
                val_unit_split = re.match(var_unit_re, substring)
                val_nospace = val_unit_split[1]
                val_unit_dict_out[val_nospace] = [val_unit_split[6]]
            else:
                val_unit_dict_out[val_nospace].append(substring)
    return val_unit_dict_out
