# AtMoDat Standard Compliance Checks 

This is a python library that contains checks to ensure compliance with the AtMoDat Standard.

Its core funtionallity is based on the [IOOS compliance checker](https://github.com/ioos/compliance-checker). The AtMoDat Standard Compliance Checks library makes use of [cc-yaml](https://github.com/cedadev/cc-yaml) which provides a plugin for the [IOOS compliance checker](https://github.com/ioos/compliance-checker) that generates check suites from YAML descriptions. Furthermore, the [Compliance Check Library](https://github.com/cedadev/compliance-check-lib) is used as the basis to define generic, reusable compliance checks. This repository is an extension of this library as it holds specfifc checks to ensure compliance with the AtMoDat Standard.

## Installation (only tested on a linux machine)

1. Clone this repository and update submodules (compliance-check-lib and cc-yaml)
```
git clone [URL] (!!! adaption needed !!!)
cd atmodat_standard_checker (!!! adaption needed !!!)
git submodule init
git submodule update
```

2. Install Python 3 via conda if necessary:
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh -p $HOME/miniconda3 -b
rm -f Miniconda3-latest-Linux-x86_64.sh
```

3. Create conda environment and install the IOOS compliance checker via conda:
```
conda create --name atmodat_checker -y
conda activate atmodat_checker
conda install -c conda-forge compliance-checker pip -y
```

4. Install relevant checker packages:
- cc-yaml
```
cd cc-yaml
pip install --editable . --no-deps
pip install -r requirements.txt
cd ..
```
- compliance-check-lib
```
cd compliance-check-lib
pip install --editable . --no-deps
pip install -r requirements.txt
cd ..
```
- atmodat-checker
```
cd atmodat-checker
pip install --editable . --no-deps
cd ..
```
5. Point `pyessv` at the "archive" where AtMoDat controlled vocabulary is stored
```
export PYESSV_ARCHIVE_HOME=$PWD/pyessv-archive
```

## Run tests
This repository contains the `atmodat_standard_checker.yml` YAML file that contains the necessary checks. It holds checks suites for "mandatory" and "recommended" attributes of the AtMoDat Standard. For checking mandatory attributes run:
```
cchecker.py --y atmodat_standard_checker.yml --test atmodat_standard_checker_mandatory:0.1 file_to_test.nc
```
or recommended attributes, respectively:
```
cchecker.py --y atmodat_standard_checker.yml --test atmodat_standard_checker_recommended:0.1 file_to_test.nc
```
