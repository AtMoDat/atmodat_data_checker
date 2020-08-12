# Top-level location of all checks so that they can easily be located

from .register.nc_coords_checks_register import *
from .register.nc_var_checks_register import *
from .register.nc_file_checks_register import *
from .register.format_checks_register import *
from .register.file_checks_register import *

ALL_CHECKS = [check for check in dir() if check.endswith("Check")]
