#!/bin/bash

ifile=$1
filename=$(basename "$ifile")
opath="checker_output"
ofile_stump=${filename/%".nc"}


for check_type in mandatory recommended optional
do
    echo
    echo
    echo "--------------------------------------------------------------------------------"
    cchecker.py --y atmodat_standard_checker_${check_type}.yml -f json_new -o ${opath}/"${ofile_stump}"_${check_type}.json --test atmodat_standard_checker_${check_type}:1.0 "${ifile}"
    cchecker.py --y atmodat_standard_checker_${check_type}.yml --test atmodat_standard_checker_${check_type}:1.0 "${ifile}"
    echo "--------------------------------------------------------------------------------"
    echo
    echo
done
cfchecks -v auto "${ifile}"
