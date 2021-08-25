# ATMODAT Standard Compliance Checker

This is a python library that contains checks to ensure compliance with the ATMODAT Standard.

Its core functionality is based on the [IOOS compliance checker](https://github.com/ioos/compliance-checker). The ATMODAT Standard Compliance Checker library makes use of [cc-yaml](https://github.com/cedadev/cc-yaml), which provides a plugin for the [IOOS compliance checker](https://github.com/ioos/compliance-checker) that generates check suites from YAML descriptions. Furthermore, the [Compliance Check Library](https://github.com/cedadev/compliance-check-lib) is used as the basis to define generic, reusable compliance checks. This repository is an extension of this library as it holds specific checks to ensure compliance with the ATMODAT Standard.

In addition the compliance to the CF Conventions 1.4 or higher is verified with the [CF checker](https://github.com/cedadev/cf-checker).

## Installation (tested on Linux and Mac OS)

1. Clone this repository

```bash
git clone https://github.com/AtMoDat/atmodat_data_checker.git
cd atmodat_data_checker
```

2. Install Python 3 via conda if necessary:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh -p $HOME/miniconda3 -b
rm -f Miniconda3-latest-Linux-x86_64.sh
```

3. Create conda environment and install the IOOS compliance checker via conda:

```bash
conda env create         # environment name is retrieved from environment.yml
conda activate atmodat
```

4. Install (and upgrade) atmodat-checker
```bash
pip install -U -e .
```

5. Initalize and update the [ATMODAT CVs](https://github.com/AtMoDat/AtMoDat_CVs) submodule, which contains the controlled vocabulary for the ATMODAT Standard.

```bash
git submodule init
git submodule update
```

6. Point `pyessv` to the `pyessv-archive` where ATMODAT controlled vocabulary is stored

```bash
export PYESSV_ARCHIVE_HOME=$PWD/AtMoDat_CVs/pyessv-archive
```

7. For regular usage of the ATMODAT Standard Checker, it is recommended to put the line given in 6. into your `.bashrc` or `.bash_profile`. Replace the `$PWD` with the absolute path. 


## How to run the ATMODAT Standard Checker

The command `run_checks.py` can be executed from any directory from within the `atmodat` conda environment. It will perform checks to evaluate the compliance with the ATMODAT Standard.  Compliance with the CF Conventions is checked by a call to the [CF checker](https://github.com/cedadev/cf-checker). The results of the performed checks are provided in the `checker_output` directory.

* To check a single file, use:
```bash
run_checks.py -f file_to_check.nc
```
* To run the checker on all `*.nc` files of a directory (including all sub-directories), use:
```bash
run_checks.py -p file_path
```
* To create a summary of the checks performed, add the ````-s```` flag, e.g.:
```bash
run_checks.py -s -p file_path
```
* To define a custom path into which the checker output shall be written, use:
```bash
run_checks.py -op output_path -p file_path
```
* To define the CF version against which the file(s) shall be checked, use:
```bash
run_checks.py -cfv 1.6 -p file_path
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Valid are versions from 1.4 to 1.8. Default is ````-cfv auto````. 

* To define whether the file(s) shall be checked only against the ATMODAT Standard (AT) or the CF Conventions (CF), specify either ````-check AT```` or ````-check CF````. 
```bash
run_checks.py -check AT -p file_path
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  Default is ````-check both````.

* You can combine different optional arguments, for example:
```bash
run_checks.py -s -op mychecks -check both -cfv 1.4 -p file_path
```
* For more information use:
```bash
python run_checks.py --help`
```

## Contributors

In alphabetic order:

- [Ag Stephens](https://github.com/agstephens)
- [Amandine Kaiser](https://github.com/am-kaiser), [ORCID: 0000-0002-2756-9964](https://orcid.org/0000-0002-2756-9964)
- [Anette Ganske](https://github.com/anganske), [ORCID: 0000-0003-1043-4964](https://orcid.org/0000-0003-1043-4964)
- [Angelika Heil](https://github.com/atmodatcode), [ORCID: 0000-0002-0131-1404](https://orcid.org/0000-0002-0131-1404)
- Angelina Kraft, [ORCID: 0000-0002-6454-335X](https://orcid.org/0000-0002-6454-335X)
- [Daniel Heydebreck](https://github.com/neumannd), [ORCID: 0000-0001-8574-9093](https://orcid.org/0000-0001-8574-9093)
- [Hugo Ricketts](https://github.com/gapintheclouds)
- [Jan Kretzschmar](https://github.com/jkretz), [ORCID: 0000-0002-8013-5831](http://orcid.org/0000-0002-8013-5831)


## Acknowledgements

The ATMODAT Standard Compliance Checker was created within the AtMoDat project (Atmospheric Model Data, <https://www.atmodat.de>). AtMoDat is funded by the German Federal Ministry for Education and Research within the framework of Atmosphären-Modelldaten: Datenqualität, Kurationskriterien und DOI-Branding (FKZ 16QK02A).
