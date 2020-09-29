"""
ess_vocabs_utils.py
=============

Holds the ESSVocabs class.

This is a base class for working with controlled vocabularies that can
be worked with using the pyessv library (https://github.com/ES-DOC/pyessv).

For example, the CMIP6 project manages its CVs in GitHub and can be
accessed by pyessv using a local file-system cache of the files.
"""

from netCDF4 import Dataset
from checklib.cvs.ess_vocabs import ESSVocabs
from checklib.code.errors import FileError


class ESSVocabsAtmodat(ESSVocabs):
    """Base class for all ESSVocabs File Checks (that work on a file path."""

    def _check_primary_arg(self, primary_arg):
        if not isinstance(primary_arg, Dataset):
            raise FileError("Object for testing is not a netCDF4 Dataset: "
                            "{}".format(str(primary_arg)))

    def check_global_attribute(self, ds, attr, property_check="label"):
        """
        Checks that global attribute `attr` is in allowed values (from CV).

        :param ds: NetCDF4 Dataset object
        :param attr: string - name of attribtue to check.
        :param property_check: string property of CV term to check
        (defaults to 'label')
        :return: Integer (0: not found; 1: found (not recognised);
        2: found and recognised.
        """
        if attr not in ds.ncattrs():
            return 0

        nc_attr = ds.getncattr(attr)

        allowed_values = [self.get_value(term, property_check) for term in
                          self._cvs[self._get_lookup_id(attr)]]

        if nc_attr not in allowed_values:
            return 1

        return 2
