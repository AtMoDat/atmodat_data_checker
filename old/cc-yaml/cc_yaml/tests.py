"""
Test the generation of a checker class from a YAML file
"""
import pytest
import inspect
from copy import deepcopy

import yaml

from cc_yaml.yaml_parser import YamlParser
from compliance_checker.base import BaseCheck, Dataset


class BaseTestCheckClass(object):
    supported_ds = []
    def __init__(self, params, level="MEDIUM"):
        pass
    def __call__(self, ds):
        return None


# Create test checks for checking the supported_ds property in the generated
# check class. For simplicity here dataset types are ints
class SupportDsTestCheckClass1(BaseTestCheckClass):
    supported_ds = [1, 2, 3]


class SupportDsTestCheckClass2(BaseTestCheckClass):
    supported_ds = [2, 3, 4]


class BasicTestCheck(object):
    supported_ds = [Dataset]
    def __init__(self, params, level=None):
        self.params = params
        self.level = level
    def __call__(self, ds):
        return (self.params, self.level)


class TestYamlParsing(object):

    def get_import_string(self, cls):
        """
        Return a string to use as 'check_name' in YAML configs in tests to
        import a class from this file
        """
        return "{}.{}".format("cc_yaml.tests", cls)

    def get_check_method_names(self, cls):
        method_names = [x[0] for x in inspect.getmembers(cls, inspect.isfunction)]
        return sorted([x for x in method_names if x.startswith("check_")])

    def test_missing_keys(self):
        """
        Check that a config with missing required fields is marked as invalid
        """
        invalid_configs = [
            {},
            {"suite_name": "hello"},  # Missing checks
            {"checks": []},           # Missing suite name
            # Missing parameters
            {"suite_name": "hello", "checks": [{"check_id": "one"}]}
        ]
        valid_config = {"suite_name": "hello",
                        "checks": [{"check_id": "one", "parameters": {},
                                    "check_name": "blah"}]}

        for c in invalid_configs:
            with pytest.raises(ValueError):
                YamlParser.validate_config(c)
        try:
            YamlParser.validate_config(valid_config)
        except ValueError:
            assert False, "Valid config was incorrectly marked as invalid"

    def test_invalid_types(self):
        """
        Check that configs are marked as invalid if elements in it are of the
        wrong type
        """
        # Start with a valid config
        valid_config = {"suite_name": "hello",
                        "checks": [{
                            "check_id": "one", "parameters": {},
                            "check_name": self.get_import_string("BasicTestCheck")
                        }]}

        c1 = deepcopy(valid_config)
        c1["suite_name"] = ("this", "is", "not", "a", "string")

        c2 = deepcopy(valid_config)
        c2["checks"] = "oops"

        c3 = deepcopy(valid_config)
        c3["checks"][0]["check_id"] = {}

        c4 = deepcopy(valid_config)
        c4["checks"][0]["parameters"] = 0

        for c in (c1, c2, c3, c4):
            with pytest.raises(TypeError):
                YamlParser.validate_config(c)

    def test_no_checks(self):
        """
        Check that a config with no checks is invalid
        """
        with pytest.raises(ValueError):
            YamlParser.validate_config({"suite_name": "test", "checks": []})

    def test_class_gen(self):
        """
        Check that a checker class is generated correctly
        """
        check_cls = self.get_import_string("BasicTestCheck")
        config = {
            "suite_name": "test_suite",
            "checks": [
                {"check_id": "one", "parameters": {"a": 42}, "check_name": check_cls},
                {"check_id": "two", "parameters": {"a": 19}, "check_name": check_cls,
                 "check_level": "LOW"}
            ]
        }
        new_class = YamlParser.get_checker_class(config)
        # Check class inherits from BaseCheck
        assert BaseCheck in new_class.__bases__

        # Check the expected methods are present
        assert self.get_check_method_names(new_class) == ["check_one", "check_two"]

        # Check name is correct
        assert new_class.__name__ == "test_suite"

        # Check the class methods return the expected values
        checker = new_class()
        assert checker.check_one("dataset") == ({"a": 42}, None)
        assert checker.check_two("dataset") == ({"a": 19}, "LOW")

    def test_supported_ds(self):
        valid_config = {
            "suite_name": "test_suite",
            "checks": [
                {"check_id": "one", "parameters": {},
                 "check_name": self.get_import_string("SupportDsTestCheckClass1")},

                {"check_id": "one", "parameters": {},
                 "check_name": self.get_import_string("SupportDsTestCheckClass2")}
            ]
        }
        check_cls = YamlParser.get_checker_class(valid_config)
        # Supported datasets for generated class should be types common to both
        # checks
        assert check_cls.supported_ds == [2, 3]

    def test_include_other_yaml_file(self, tmpdir):
        """
        Check that checks from another YAML file can be included
        """
        # Create YAML files in different directories so we can check that
        # included file is looked up relative to the first
        dir1 = tmpdir.mkdir("dir1")
        dir2 = tmpdir.mkdir("dir2")
        dir3 = dir2.mkdir("dir2")
        yaml1 = dir1.join("suite1.yml")
        yaml2 = dir2.join("suite2.yml")

        yaml1.write(yaml.dump({
            "suite_name": "first_suite",
            "checks": [
                {
                    "check_id": "first_check",
                    # The base check used here is not important...
                    "check_name": self.get_import_string("BasicTestCheck"),
                    "parameters": {}
                },
                {"__INCLUDE__": "../dir2/suite2.yml"}
            ]
        }))

        yaml2.write(yaml.dump({
            "suite_name": "this_should_not_be_seen",
            "checks": [
                {
                    "check_id": "included_check1",
                    "check_name": self.get_import_string("BasicTestCheck"),
                    "parameters": {"some_var": "some_value"}
                },
                {
                    "check_id": "included_check2",
                    "check_name": self.get_import_string("BasicTestCheck"),
                    "parameters": {"another_var": "another_value"}
                }
            ]
        }))

        # Try generating the combined YAML from different directories to check
        # relative path lookup
        dirs = (tmpdir, dir1, dir2, dir3)
        for d in dirs:
            with d.as_cwd():
                cls = YamlParser.get_checker_class(str(yaml1))

                assert cls.__name__ == "first_suite"
                assert self.get_check_method_names(cls) == [
                    "check_first_check", "check_included_check1", "check_included_check2"
                ]

    def test_include_absolute_path(self, tmpdir):
        yaml1 = tmpdir.join("yaml1.yml")
        yaml2 = tmpdir.join("yaml2.yml")

        yaml1.write(yaml.dump({
            "suite_name": "first_suite",
            "checks": [{"__INCLUDE__": str(yaml2)}]
        }))

        yaml2.write(yaml.dump({
            "suite_name": "included_suite",
            "checks": [
                {
                    "check_id": "included_check",
                    "check_name": self.get_import_string("BasicTestCheck"),
                    "parameters": {"var": "value"}
                }
            ]
        }))

        cls = YamlParser.get_checker_class(str(yaml1))
        assert self.get_check_method_names(cls) == ["check_included_check"]

    def test_invalid_config_in_included_file(self, tmpdir):
        """
        Check that a validation error is raised if an included file is not
        valid
        """
        yaml1 = tmpdir.join("yaml1.yml")
        yaml2 = tmpdir.join("yaml2.yml")

        yaml1.write(yaml.dump({
            "suite_name": "first_suite",
            "checks": [{"__INCLUDE__": "yaml2.yml"}]
        }))

        yaml2.write(yaml.dump({
            "suite_name": "included_suite",
            "checks": [
                {
                    "cheque_id": "included_check",
                    "check_nom": self.get_import_string("BasicTestCheck"),
                    "purumuters": {"var": "value"}
                }
            ]
        }))

        with pytest.raises(ValueError):
            cls = YamlParser.get_checker_class(str(yaml1))

    def test_recursive_include(self, tmpdir):
        """
        Check that includes can be recursive, i.e 1 includes 2 which includes 3
        will result in checks from 1 + 2 + 3
        """
        # Note: create 1 in different dir to 2 and 3, so that we check the
        # path to 3 is resolved relative to 2 (not relative to 1)...
        dir1 = tmpdir.mkdir("dir1")
        dir2 = tmpdir.mkdir("dir2")
        yaml1 = dir1.join("yaml1.yml")
        yaml2 = dir2.join("yaml2.yml")
        yaml3 = dir2.join("yaml3.yml")

        def get_check(name):
            return {
                "check_id": "from_{}".format(name),
                "check_name": self.get_import_string("BasicTestCheck"),
                "parameters": {}
            }

        yaml1.write(yaml.dump({
            "suite_name": "one",
            "checks": [
                get_check("one"),
                {"__INCLUDE__": "../dir2/yaml2.yml"}
            ]
        }))

        yaml2.write(yaml.dump({
            "suite_name": "two",
            "checks": [
                get_check("two"),
                {"__INCLUDE__": "yaml3.yml"}
            ]
        }))

        yaml3.write(yaml.dump({
            "suite_name": "three",
            "checks": [
                get_check("three"),
            ]
        }))

        cls = YamlParser.get_checker_class(str(yaml1))
        assert self.get_check_method_names(cls) == [
            "check_from_one", "check_from_three", "check_from_two"
        ]
