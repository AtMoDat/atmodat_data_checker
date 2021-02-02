#!/bin/bash


ifolder=$1
for file in "${ifolder}"/*.nc; do
    cchecker.py --y atmodat_data_checker_mandatory.yml --test atmodat_data_checker_mandatory:1.0 "${file}" --verbose -f json -o "${file::-3}_result.json"
    echo "--------------------------------------------------------------------------------"
    cchecker.py --y atmodat_data_checker_recommended.yml --test atmodat_data_checker_recommended:1.0 "${file}" --verbose -f json -o "${file::-3}_result.json"
    echo "--------------------------------------------------------------------------------"
    cchecker.py --y atmodat_data_checker_optional.yml --test atmodat_data_checker_optional:1.0 "${file}" --verbose -f json -o "${file::-3}_result.json"
    echo "--------------------------------------------------------------------------------"
    cfchecks -v auto "${file}" >> "${file::-3}_result.txt"
done
