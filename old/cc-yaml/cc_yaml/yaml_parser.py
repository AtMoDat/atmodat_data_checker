import importlib
import os

import yaml

from compliance_checker import __version__ as cc_check_version
from compliance_checker.base import BaseCheck


class YamlParser(object):
    """
    Class to hold methods relating to generating a checker class from a YAML
    config file
    """
    # Key used to include checks from another file
    INCLUDE_KEYWORD = "__INCLUDE__"

    @classmethod
    def load_yaml(cls, filename):
        """
        Load a YAML document from a file

        :param filename: Path to file
        :return: YAML object as a dict
        """
        with open(filename) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        if not isinstance(config, dict):
            raise TypeError("Could not parse dictionary from YAML file '{}'"
                            .format(filename))
        return config

    @classmethod
    def get_checker_class(cls, config):
        """
        Parse the given YAML file and return a checker class

        :param config: Config dictionary or filename of YAML file to parse
                       config from
        :return:       A class that can be used as a check suite with
                       compliance-checker
        """
        # Treat config as a filename if it is a string
        filename = None
        if isinstance(config, str):
            filename = config
            config = cls.load_yaml(filename)

        if filename is not None:
            cls.resolve_includes(config, os.path.dirname(filename))
        cls.validate_config(config)

        # Build the attributes and methods for the generated class
        class_properties = {
            "_cc_spec_version": cc_check_version
        }

        supported_ds_sets = []

        for check_info in config["checks"]:
 
            method_name = "check_{}".format(check_info["check_id"])

            # Instantiate a check object using the params from the config
            check_cls = YamlParser.get_base_check_cls(check_info["check_name"])
            kwargs = {}

            try:
                kwargs["level"] = check_info["check_level"]
            except KeyError:
                pass
            check_instance = check_cls(check_info["parameters"], **kwargs)

            # Create function that will become method of the new class. Specify
            # check_instance as a default argument so that it is evaluated when
            # function is defined - otherwise the function stores a reference
            # to check_instance which changes as the for loop progresses, so
            # only the last check is run
            def inner(self, ds, c=check_instance):
                return c(ds)

            inner.__name__ = str(method_name)
            class_properties[method_name] = inner
            supported_ds_sets.append(set(check_cls.supported_ds))

        # Supported dataset types will be those that are supported by ALL checks
        class_properties["supported_ds"] = list(set.intersection(*supported_ds_sets))

        return type(config["suite_name"], (BaseCheck,), class_properties)

    @classmethod
    def resolve_includes(cls, config, base_directory):
        """
        Modify a config dict to include checks from other YAML files as
        necessary

        :param config:         The dictionary parsed from YAML file
        :param base_directory: The directory relative to which the included
                               files are found (if relative path is given)
        """
        # Avoid doing any validation here, since config is validated properly
        # after includes
        if "checks" not in config:
            return

        new_checks = []
        for check_info in config["checks"]:
            if len(check_info) == 1 and cls.INCLUDE_KEYWORD in check_info:
                included = check_info[cls.INCLUDE_KEYWORD]
                if os.path.isabs(included):
                    fname = included
                else:
                    fname = os.path.join(base_directory, included)

                included_config = cls.load_yaml(fname)
                # Resolve includes recursively. Not that there is nothing in
                # the code to prevent an endless loop if file A includes file B
                # and B also includes A...
                cls.resolve_includes(included_config, os.path.dirname(fname))
                if "checks" not in included_config:
                    print("WARNING: 'checks' attribute not found in included "
                          "file '{}'".format(fname))
                    continue

                new_checks += included_config["checks"]
            else:
                new_checks.append(check_info)

        config["checks"] = new_checks

    @classmethod
    def get_base_check_cls(cls, base_check_str):
        """
        Parse a string specifying the base check and return the class
        :param base_check_str: Path to class as a string in the form
                               <package>.<module>.<class name>
        :return:               Class object
        """
        parts = base_check_str.split(".")
        module = importlib.import_module(".".join(parts[:-1]))
        return getattr(module, parts[-1])

    @classmethod
    def validate_config(cls, config):
        """
        Validate a config dict to check it has all the information required to
        generate a checker class

        :param config: The dictionary parsed from YAML file to check
        :raises ValueError: if any required values are missing or invalid
        :raises TypeError:  if any values are an incorrect type
        """
        required_global = {"checks": list, "suite_name": str}
        required_percheck = {"check_id": str, "parameters": dict, "check_name": str}
        optional_percheck = {"check_level": str}

        for f_name, f_type in required_global.items():
            cls.validate_field(f_name, f_type, config, True)

        for check_info in config["checks"]:
            for f_name, f_type in required_percheck.items():
                cls.validate_field(f_name, f_type, check_info, True)

            for f_name, f_type in optional_percheck.items():
                cls.validate_field(f_name, f_type, check_info, False)

            allowed_levels = ("HIGH", "MEDIUM", "LOW")
            if "check_level" in check_info and check_info["check_level"] not in allowed_levels:
                raise ValueError("Check level must be one of {}".format(", ".join(allowed_levels)))

        if not config["checks"]:
            raise ValueError("List of checks cannot be empty")

    @classmethod
    def validate_field(cls, key, val_type, d, required):
        """
        Helper method to check a dictionary contains a given key and that the
        value is the correct type
        """
        if required and key not in d:
            raise ValueError("Required key '{}' not present".format(key))

        if key in d and not isinstance(d[key], val_type):
            err_msg = "Value for field '{}' is not of type '{}'"
            raise TypeError(err_msg.format(key, val_type.__name__))
