import numpy as np
import re
from cfunits import Units
import dateutil.parser as parser
import requests


def check_conventions_version_number(ds, attr, conv_type, min_ver, max_ver):
    """
    Checks global attribute values in a NetCDF Dataset and returns integer
    regarding whether the `attr` matches number+unit format

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :param conv_type: Name of convention string to be checked for version
    :param min_ver: Minimum version allowed
    :param max_ver: Maximum version allowed
    :return: Integer (0: not found; 1: convention to be checked for not found; 2: convention out of valid range;
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


def find_url(ds):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|" \
            r"(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    attr_url_dict = {}
    for attr in ds.ncattrs():
        attr_content = getattr(ds, attr)
        url = re.findall(regex, attr_content)
        url_list = [x[0] for x in url]
        if len(url_list) > 0:
            attr_url_dict[attr] = url_list
    return attr_url_dict


def check_url_status(url_in):
    try:
        response = requests.get(url_in)
    except:
        return True
    else:
        if response.status_code == 200:
            return False
        else:
            return True


def orcid_checksum(number):
    """Calculate the ORICD checksum. A valid ORCID should have a checksum of 1."""
    checksum = 0
    for n in number:
        checksum = (2 * checksum + int(10 if n == 'X' else n)) % 11
    return checksum


def check_orcid(url_in):
    orcid = url_in.rstrip('/').split('/')[-1].replace('-', '')
    checksum = 0
    for n in orcid:
        checksum = (2 * checksum + int(10 if n == 'X' else n)) % 11
    if checksum == 1:
        return 1
    else:
        return 0


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

    if attr_type == 'int':
        attr_type_class = int
    elif attr_type == 'float':
        attr_type_class = float
    elif attr_type == 'str':
        attr_type_class = str
    else:
        return 1

    if len(str(global_attr)) == 0:
        return 2

    if np.dtype(type(global_attr)) != np.dtype(attr_type_class):
        return 3

    return 4


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

    try:
        parser.isoparse(global_attr)
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

    if resol_string == 'point':
        return 4
    elif not check_value_exists(resol_string):
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
