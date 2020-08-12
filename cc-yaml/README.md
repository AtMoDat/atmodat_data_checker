# cc-yaml

This repo holds a [compliance-checker](https://github.com/ioos/compliance-checker)
plugin that generates check suites from YAML descriptions.

It is to be used with the
[cedadev fork](https://github.com/cedadev/compliance-checker)
of `compliance-checker` that allows plugins to generate check suites.

## Installation

To set up you must install `compliance-checker` itself and this plugin (`cc-yaml`).

```
pip install -e git+https://github.com/cedadev/compliance-checker
pip install -e git+https://github.com/cedadev/cc-yaml

compliance-checker --yaml <path-to-YAML-file> --test <test name> <dataset>
```

## Creating check suites from YAML descriptions

This plugin allows check suites to be generated from *base checks* using YAML
files containing parameters to call these base checks with.

This allows you to write generic check methods that can be used across
different projects and called with different parameters (which can be
project-specific).

### Example

An example YAML file is shown below. It uses base checks from
[compliance-check-lib](https://github.com/cedadev/compliance-check-lib).

```yaml
suite_name: "custom-check-suite"

checks:
  - check_id: "filesize_check"
    parameters: {"threshold": 1}
    check_name: "checklib.register.FileSizeCheck"

  - check_id: "filename_check"
    parameters: {"delimiter": "_", "extension": ".nc"}
    check_name: "checklib.register.FileNameStructureCheck"

  - check_id: "attribute_check"
    parameters: {"regex": "\\d+", "attribute": "author"}
    check_name: "checklib.register.GlobalAttrRegexCheck"
    check_level: "LOW"
```

Explanation:

* `suite_name` (in this example 'custom-check-suite') is the name of the generated suite (i.e. the
  name to use after `--test` when running Compliance Checker from the command line)
* Each item in the list `checks` defines a single check method:
  * `check_id` is an identifier for the check (the identifier used is somewhat arbitrary, and is
    only used for the name of the check method in the generated class)
  * `check_name` is the *base check* where the actual code to perform the check is defined. It
    should be of the form `<module>.class`. This module needs to be importable from the environment
    in which Compliance Checker is run. Details on what this class should look like are given below.
  * `parameters` is a dictionary that is passed to `__init__` when instantiating the class
    specified in `check_name`.
  * `check_level` is one of `HIGH`, `MEDIUM`, `LOW` and determines the priority level of the check.

This check suite can be run from the command line by using the `--yaml` option:
```
compliance-checker --yaml <path-to-YAML-file> --test custom-check-suite <dataset>
```

### Base Checks

Each base check is represented as a class implementing the following interface:

* **Define a property `supported_ds`**. This should be a list of dataset types
  acceptable to run this check on. For example, this could be `[Dataset]` to
  run checks against NetCDF files only, or `[Dataset, GenericFile]` to check
  any file (including NetCDF files). Here `Dataset` and `GenericFile` are
  defined in `compliance_checker.base`.

* **Take a dictionary of parameters as first argument to `__init__`** (this is
  the value of `parameters` in the YAML file)

* **Accept `level` as an optional kwarg to `__init__`** (this is the value of
  `check_level` from the YAML file)

* **Implement `__call__(self, ds)`**. Here `ds` is the dataset object
  constructed by compliance-checker (it will always be one of the types in
  `supported_ds`). The return value from this method should be the same as for
  any other compliance-checker check method. Documentation can be found on the
  [compliance-checker development wiki page](https://github.com/ioos/compliance-checker/wiki/Development).

A minimal example is provided below. This example check succeeds if a dataset
contains a given variable. The variable name is extracted from the YAML file.

```python
from compliance_checker.base import BaseCheck, Dataset, Result

class VariableExistsCheck(object):
    supported_ds = [Dataset]

    level = BaseCheck.MEDIUM

    def __init__(self, params, level=None):
        self.var_id = params["var_id"]
        if level:
            self.level = getattr(BaseCheck, level)

    def __call__(self, ds):
        messages = []
        success = self.var_id in ds.variables
        if not success:
            messages.append("Variable {} not found in dataset".format(self.var_id))

        return Result(
            weight=self.level,
            value=success,
            name="Variable '{}' check".format(self.var_id),
            msgs=messages
        )
```

### compliance-check-lib

The interface described above has been designed to be as general as possible.
The [compliance-check-lib](https://github.com/cedadev/compliance-check-lib)
library provides a base class `CallableCheckBase` that implements this
interface and provides extra features, such default parameters and validation
of required parameters from YAML.

It also contains a plethora of real-world checks to use as examples:
[see the code on GitHub](https://github.com/cedadev/compliance-check-lib/tree/master/checklib/register).

### Including other YAML files

Checks from one file can be included into another using the `__INCLUDE__`
keyword, e.g.

`suite_1.yml`:
```
suite_name: suite_one
checks:
checks:
  - check_id: "filesize_check"
    parameters: {"threshold": 1}
    check_name: "checklib.register.FileSizeCheck"

  - __INCLUDE__: suite_2.yml
```

`suite_2.yml`:
```
suite_name: suite_two
checks:
  - check_id: "attribute_check"
    parameters: {"regex": "\\d+", "attribute": "author"}
    check_name: "checklib.register.GlobalAttrRegexCheck"
    check_level: "LOW"
```

Running `compliance-checker --yaml suite_1.yml --test suite_one <dataset>` will
then run both `filesize_check` and `attribute_check`.

Note that *all* checks from `suite_2.yml` will be included (if there is more
than one). It is also possible to have several `__INCLUDE__` directives to
include checks from several files.

Recursive inclusions are also supported -- i.e. A includes checks from B which
in turn include checks from C.
