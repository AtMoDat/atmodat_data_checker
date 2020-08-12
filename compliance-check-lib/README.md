# Compliance Check Library - python library of compliance checks

This is a python library (`checklib`) that defines generic, reusable compliance checks for use with the [IOOS compliance checker](https://github.com/ioos/compliance-checker).

Each check is defined within a class that knows about:
 - a human-readable description of the check (including templating for modifications)
 - a list of return values and useful user messages based on a range of possible results
 - unit tests for each test
 - hooks to talk to any vocabularies that can be interpreted by the [pyessv](https://github.com/es-doc/pyessv).

## Testing

To run the tests:

```
# Set up the directory required for working with the ESSV controlled vocabularies
mkdir -p ~/.esdoc

# Copy the example vocabularies into place
cp -r checklib/test/example_data/pyessv-archive-eg-cvs ~/.esdoc/pyessv-archive

pytest
```

## Importing the checks

You can get to all checks with.

```
from checklib.checks import *

print(dir())

print ALL_CHECKS
```
