"""
ess_vocabs.py
=============

Holds the ESSVocabs class.

This is a base class for working with controlled vocabularies that can be worked with
using the pyessv library (https://github.com/ES-DOC/pyessv).

For example, the CMIP6 project manages its CVs in GitHub and can be accessed by pyessv
using a local file-system cache of the files.

"""

import os, re
from netCDF4 import Dataset

# Check that ESSV directory exists, or give warning
VOCABS_DIR = os.environ.get('PYESSV_ARCHIVE_HOME', os.path.expanduser('~/.esdoc/pyessv-archive')) 

if not os.path.isdir(VOCABS_DIR):
    import warnings
    warnings.warn('Could not find PYESSV vocabularies directory. Vocabulary checks '
                  'will not work. Directory should exist at: {}'.format(VOCABS_DIR))


# Import library to interact with Controlled Vocabularies
import pyessv


def validate_daterange(frequency):
    if frequency == "yr" or frequency == "decadal":
        template = "yyyy"
    elif frequency == "mon" or frequency == "monClim":
        template = "yyyyMM"
    return template


class ESSVocabs(object):
    """
    Class for working with Vocabularies stored in ESSV format.
    Accessible via `pyessv` library.

    """
    authority = None
    scope = None

    
    def __init__(self, authority, scope):
        """
        Instantiates class by setting authority, scope and loading the CVs 
        from local cache.
        """
        self.authority = authority
        self.scope = scope
        self._cache_controlled_vocabularies()


    def _cache_controlled_vocabularies(self):
        """
        Loads controlled vocabularies once and caches them.
        """
        self._cvs = pyessv.load("{}:{}".format(self.authority, self.scope))
        self._authority_info = pyessv.load(self.authority)


    def _get_lookup_id(self, attr, full=False):
        """
        Maps attribute name to lookup value.

        :attr   attribute name: string
        :full   boolean to say whether the attribute should be expressed
                as a full path: default=False 
                If True: <authority>:<scope>:<attribute>
        :return: lookup value: string
        """
        fixed_attr = attr.replace("_", "-")

        if full:
            return "{}:{}:{}".format(self.authority, self.scope, fixed_attr)
        else:
            return fixed_attr

    def get_value(self, term, property="label"):
        """
        Makes the lookup for a given term and matches against the property given.
        Copes with nested dictionary lookups that are expressed by the "." convention in the value of `attr`.

        :param term: term to lookup (either string as '<collection>:<term>' or pyessv Term instance).
        :param property: property of term to match against (even including sub-dictionary lookups).
        :return: value or None if not found.
        """
        # Delay nested looks up if required
        if "." in property:
            property, key_chain = property.split(".", 2)
            key_chain = key_chain.split(".")
        else:
            key_chain = []

        # Fix term type: must be instance of pyessv.Term
        if not isinstance(term, pyessv.Term):
              
            try:
                # Use only the last 2 values (collection, item) to do the lookup
                colln, item = term.split(":")[-2:]
                term = [v for v in self._cvs[colln] if item in (v.canonical_name, v.label)][0]
            except:
                raise Exception("Could not get value of term based on vocabulary lookup: '{}'.".format(term))

        # Do vocabulary look-up
        value = getattr(term, property, None)
        if not value:
            return None

        # Now do nested lookup
        for key in key_chain:
            value = value[key]

        return value

    def check_global_attribute(self, ds, attr, property="label"):
        """
        Checks that global attribute `attr` is in allowed values (from CV).
       
        :param ds: NetCDF4 Dataset object
        :param attr: string - name of attribtue to check.
        :param property: string property of CV term to check (defaults to 'label')
        :return: Integer (0: not found; 1: found (not recognised); 2: found and recognised.
        """
        if not attr in ds.ncattrs():
            return 0
           
        nc_attr = ds.getncattr(attr) 
        allowed_values = [self.get_value(term, property) for term in self._cvs[self._get_lookup_id(attr)]]

        if nc_attr not in allowed_values:
            return 1
            
        return 2

    def check_global_attribute_by_status(self, ds, attr, status, property="label"):
        """
        Checks that global attribute `attr` is in allowed values (from CV).

        :param ds: NetCDF4 Dataset object
        :param attr: string - name of attribtue to check.
        :param status: string - status (mandatory or sth. else)
        :param property: string property of CV term to check (defaults to 'label')
        :return: Integer (0: not found; 1: found (not recognised); 2: found and recognised.
        """
        if status == "mandatory" and not attr in ds.ncattrs():
            return 0

        nc_attr = ds.getncattr(attr)
        allowed_values = [self.get_value(term, property) for term in
                          self._cvs[self._get_lookup_id(attr)]]

        if nc_attr not in allowed_values:
            return 1

        return 2

    def get_terms(self, collection):
        """
        Returns all terms (in alphabetical order) for a given collection.
        Raises an exception if no terms found.

        :param collection: vocabulary collection ID/lookup
        :return: list of terms [of type: pyessv.Term]
        """
        lookup = self._get_lookup_id(collection)
        terms = [term for term in self._cvs[lookup]]

        if not terms:
            raise Exception("Could not find vocabulary terms for: '{}'".format(collection))
        return terms


    def check_array_matches_terms(self, array, collection, prop="raw_name"):
        """
        Checks that the values in `array` match those in the vocabulary collection
        with each term being matched by its property specified by `prop`.

        :param array: array/list of strings
        :param collection: vocabulary collection ID/lookup
        :param prop: property of term to compare with item in array
        :return: boolean
        """
        try:
            terms = self.get_terms(collection)
        except:
            return False

        term_values = [getattr(term, prop) for term in terms]

        # If not the same length return False
        if len(array) != len(term_values):
            return False

        # If any items do not match, return False
        for i, item in enumerate(term_values):

            # Convert character array to string for each element
            if item != ''.join([_.decode('utf-8') for _ in array[i]]):
                return False

        return True


    def check_global_attribute_value(self, ds, attr, value, property="label"):
        """
        Checks that global attribute `attr` is in allowed values (from CV) and
        the global attributes value equals the given value.

        :param ds: NetCDF4 Dataset object
        :param attr: string - name of attribute to check
        :param value: string - the expected value of the attribute
        :param property: string property of CV term to check (defaults to 'label')
        :return: Integer (0: not found; 1: found (not recognised); 2: found and recognised.
        """
        messages = []
        score = 2
        if attr not in ds.ncattrs():
            messages.append("Required '{}' global attribute is not present.".
                            format(attr))
            return 0, messages

        nc_attr = ds.getncattr(attr)
        if nc_attr != value:
            messages.append("Required '{attr}' global attribute value "
                            "'{nc_attr}' not equal value from file name "
                            "'{value}'.".
                            format(attr=attr, nc_attr=nc_attr, value=value))
            score = 1

        allowed_values = [self.get_value(term, property) for term in self._cvs[self._get_lookup_id(attr)]]

        if nc_attr not in allowed_values:
            messages.append("Required '{attr}' global attribute value "
                            "'{nc_attr}' is invalid.".
                            format(attr=attr, nc_attr=nc_attr))
            score = 1

        return score, messages


    def check_file_name(self, filename, keys=None, delimiter="_", extension=".nc"):
        """
        Checks that components in the file name match CV-allowed values.
        Scoring works as follows:
         - 1 for correct extension
         - 1 for each component of the file-name that is valid
         - 1 for each regex component that is valid

        E.g.:
        <variable_id>   tas
        <table_id>      Amon
        <source_id>     hadgem3-es
        <experiment_id> piCtrl
        <member_id>     r1i1p1f1
        <grid_label>    gn
        [<time_range>]  201601-210012
        .nc

        :param filename: string
        :keys  sequence of attribute keys to look-up values from in CVs.
        :delimiter  string used as delimiter in file name: string.
        :extension  the file extension: string.
        :return: boolean
        """
        if not keys or type(keys) not in (type([]), type(())):
            raise Exception("File name checks require an input of attribute keys to check against. "
                            "None given.")

        score = 0
        messages = []

        filebase, ext = os.path.splitext(filename)
        items = filebase.split(delimiter)

        # Check extension
        if ext == extension:
            score += 1

        # Now check
        template, regexs = _get_templates(keys, delimiter, items)
        collections = self._get_collections(keys)

        # Set strictness of check
        strictness_level = 1  # Uses raw-name - which matches case

        if '{}' in template:
            try:
                parser = pyessv.create_template_parser(template, collections,
                                                       seperator=delimiter,
                                                       strictness=strictness_level)
                parser.parse(filebase)
                score += len(collections)
            except AssertionError as ex:
                messages.append(ex.message)
            except pyessv.TemplateParsingError as ex:
                messages.append('File name does not match global attributes.')

        # test any regexs that were found
        for i, regex in regexs:
            regex_c = re.compile(regex)
            if regex_c.match(items[i]):
                score += 1
            else:
                messages.append('File name fragment {item} does not match '
                                'regex {regex}.'.format(item=items[i],
                                                        regex=regex))
        return score, messages

    def _get_collections(self, keys):
        """
        Get a list of collections from the keys.
        If a key starts with 'regex:' then it is ignored.

        :keys    sequence of attribute keys to look-up values from in CVs.
        :return a tuple of collections
        """
        collections = []
        for key in keys:
            if not key.startswith('regex:'):
                collections.append(self._get_lookup_id(key, full=True))
        return tuple(collections)


def _get_templates(keys, delimiter, items):
    """
    Get the template and list of regex constructed from the items.

    :keys  sequence of attribute keys to look-up values from in CVs.
    :delimiter  string used as delimiter in file name: string.
    :items a list of the components from the file name
    :return: the template and a list of regex
    """
    regex_list = []
    for i, key in enumerate(keys):
        if key.startswith("regex:"):
            regex_list.append((i, key.split('regex:')[1]))
            if i == 0:
                template = items[i]
            else:
                template = delimiter.join([template, items[i]])
        else:
            if i == 0:
                template = '{}'
            else:
                template = delimiter.join([template, '{}'])

    return template, regex_list

