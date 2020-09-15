# AtMoDat Standard Compliance Checks 

This is a python library that contains checks to ensure compliance with the AtMoDat Standard.

Its core funtionallity is based on the [IOOS compliance checker](https://github.com/ioos/compliance-checker). The AtMoDat Standard Compliance Checks library makes use of [cc-yaml](https://github.com/cedadev/cc-yaml) which provides a plugin for the [IOOS compliance checker](https://github.com/ioos/compliance-checker) that generates check suites from YAML descriptions. Furthermore, the [Compliance Check Library](https://github.com/cedadev/compliance-check-lib) is used as the basis to define generic, reusable compliance checks. This repository is an extension of this library as it holds specfifc checks to ensure compliance with the AtMoDat Standard.

## Installation (only tested on a linux machine)

1. Clone this repository and update submodules (compliance-check-lib and cc-yaml)
```
git clone https://github.com/AtMoDat/atmodat_standard_checker.git
cd atmodat_standard_checker 
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
```diff
cd cc-yaml
# pip install --editable . --no-deps (only necessary for developers)
pip install -r requirements.txt
cd ..
```
- compliance-check-lib
```diff
cd compliance-check-lib
# pip install --editable . --no-deps (only necessary for developers)
pip install -r requirements.txt
cd ..
```
- atmodat-checker
```diff
cd atmodat_checker
# pip install --editable . --no-deps (only necessary for developers)
pip install
cd ..
```
5. Point `pyessv` at the "archive" where AtMoDat controlled vocabulary is stored
```
export PYESSV_ARCHIVE_HOME=$PWD/AtMoDat_CVs/pyessv-archive
```

## Run tests
This repository contains the `atmodat_standard_checker_mandatory.yml` and `atmodat_standard_checker_recommended.yml` YAML files that contains the necessary checks. For running the mandatory and recommended checks, you can use the `run_checks.bash`:
```
./run_checks.bash file_to_check.nc
```

## Contributors:

In alphabetic order:

* [Ag Stephens](https://github.com/agstephens)
* [Amandine Kaiser](https://github.com/am-kaiser), [ORCID: 0000-0002-2756-9964](https://orcid.org/0000-0002-2756-9964)
* [Anette Ganske](https://github.com/anganske), [ORCID: 0000-0003-1043-4964](https://orcid.org/0000-0003-1043-4964)
* Angelina Kraft, [ORCID: 0000-0002-6454-335X](https://orcid.org/0000-0002-6454-335X)
* [Daniel Heydebreck](https://github.com/neumannd), [ORCID: 0000-0001-8574-9093](https://orcid.org/0000-0001-8574-9093)
* [Hugo Ricketts](https://github.com/gapintheclouds)
* [Jan Kretzschmar](https://github.com/jkretz), [ORCID: 0000-0002-8013-5831](http://orcid.org/0000-0002-8013-5831)


## Acknowledgements:

The ATMODAT Standard checker was created within the AtMoDat project (Atmospheric Model Data, https://www.atmodat.de). AtMoDat is funded by the German Federal Ministry for Education and Research within the framework of Atmosphaeren-Modelldaten: Datenqualitaet, Kurationskriterien und DOI-Branding (FKZ 16QK02A).
 