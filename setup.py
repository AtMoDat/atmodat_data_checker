#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from atmodat_checklib import __version__

__author__ = "Jan Kretzschmar, Amandine Kaiser, Angelika Heil"
__contact__ = "heil@dkrz.de"
__license__ = "Apache licence"


# Populate long description setting with content of README
#
# Use markdown format read me file as GitHub will render it automatically
# on package page
with open("README.md") as readme_file:
    _long_description = readme_file.read()


requirements = [line.strip() for line in open('requirements.txt')]

setup_requirements = ['pytest-runner', ]

test_requirements = ["pytest"]


setup(
    author=__author__,
    author_email=__contact__,

    # See:
    # https://www.python.org/dev/peps/pep-0301/#distutils-trove-classification
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: macOS :: macOS',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    description="Compliance Check Library for AtMoDat Standard - python library of compliance checks.",

    license=__license__,

    # This qualifier can be used to selectively exclude Python versions -
    # in this case early Python 2 and 3 releases
    python_requires='>=3.6.0',
    install_requires=requirements,
    long_description=_long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='admodat',
    name="atmodat_check_lib",
    packages=find_packages(include=["atmodat_checklib", "atmodat_checklib.*"]),
    setup_requires=setup_requirements,
    scripts=["run_checks.py", "utils/fill_global_attributes/fill_global_attributes.py", "utils/fill_variable_attributes/fill_variable_attributes.py"],
    entry_points={'console_scripts': ['run_checks = run_checks:main']},
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/AtMoDat/atmodat_data_checker',
    version=__version__,
    zip_safe=False,
)
