"""
format_checks_register.py
=========================

A register of checks at the file-level that test the format of the file
given the file path.

"""

from collections import OrderedDict

from compliance_checker.base import Result

from .file_checks_register import FileCheckBase


class NCFileIsReadableCheck(FileCheckBase):
    """
    Data file is recognised as a valid netCDF file, using sub-format: {file_format}.
    """
    short_name = "File is netCDF"
    defaults = {"file_format": "NETCDF4_CLASSIC"}
    message_templates = ["File is not in required netCDF format: {file_format}."]
    level = "HIGH"

    def _get_result(self, primary_arg):
        from netCDF4 import Dataset

        try:
            ds = Dataset(primary_arg)
            assert(type(ds.variables) == dict)
            assert(type(ds.dimensions) == dict)
            # assert(ds.file_format == self.kwargs['file_format'])
            # print(ds.file_format)
            success = True
        except Exception as err:
            success = False

        messages = []

        if success:
            score = self.out_of
        else:
            score = 0
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class NCFileSoftwareCheck(FileCheckBase):
    """
    Data file is recognised as a valid netCDF file by multiple python packages (iris/xarray).
    """
    short_name = "File is netCDF readable by multiple packages"
    defaults = {}
    message_templates = ["File cannot be read by iris.",
                         "File cannot be read by xarray."]
    level = "HIGH"

    def _get_result(self, primary_arg):
        import iris
        import xarray as xr

        score = 0

        try:
            cl = iris.load(primary_arg)
            assert(type(cl) in (iris.cube.Cube, iris.cube.CubeList))
            score += 1
        except Exception as err:
            pass

        try:
            ds = xr.open_dataset(primary_arg)
            assert(type(ds) in (xr.Dataset, xr.DataArray))
            score += 1
        except Exception as err:
            pass

        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)
