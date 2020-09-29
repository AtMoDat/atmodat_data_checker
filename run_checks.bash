#!/bin/bash


ifile=$1
cchecker.py --y atmodat_standard_checker_mandatory.yml --test atmodat_standard_checker_mandatory:1.0 "${ifile}"
echo "--------------------------------------------------------------------------------"
cchecker.py --y atmodat_standard_checker_recommended.yml --test atmodat_standard_checker_recommended:1.0 "${ifile}"
echo "--------------------------------------------------------------------------------"
cchecker.py --y atmodat_standard_checker_optional.yml --test atmodat_standard_checker_optional:1.0 "${ifile}"
echo "--------------------------------------------------------------------------------"
cfchecks -v auto "${ifile}"