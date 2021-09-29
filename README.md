# ATMODAT Standard Compliance Checker


This is a python library that contains checks to ensure compliance with the ATMODAT Standard.

Its core functionality is based on the [IOOS compliance checker](https://github.com/ioos/compliance-checker). The ATMODAT Standard Compliance Checker library makes use of [cc-yaml](https://github.com/cedadev/cc-yaml), which provides a plugin for the [IOOS compliance checker](https://github.com/ioos/compliance-checker) that generates check suites from YAML descriptions. Furthermore, the [Compliance Check Library](https://github.com/cedadev/compliance-check-lib) is used as the basis to define generic, reusable compliance checks. This repository is an extension of this library as it holds specific checks to ensure compliance with the ATMODAT Standard.

In addition, the compliance to the CF Conventions 1.4 or higher is verified with the [CF checker](https://github.com/cedadev/cf-checker).

We set up a binder where you can try out the functionalities of the ATMODAT Standard Compliance Checker:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/AtMoDat/atmodat_data_checker/HEAD?filepath=notebooks)

## Installation (tested on Linux, macOS and Windows)

1. Install Miniconda or Anaconda (if not already done). Follow the [respective instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation) for your operating system.


2. Open a Terminal / Anaconda Prompt (under Windows)


3. If not already installed, a version of git is needed to clone repository of the checker from github. It can be installed using conda:
```bash
conda install -c anaconda git
```
Clone this repository:

```bash
git clone https://github.com/AtMoDat/atmodat_data_checker.git
cd atmodat_data_checker
```

4. Create conda environment and install the needed anaconda packages:

```bash
conda env create -f environment.yml
conda activate atmodat
```

5. Install (and upgrade) atmodat-checker
```bash
pip install -U -e .
```

6. Initialize and update the [ATMODAT CVs](https://github.com/AtMoDat/AtMoDat_CVs) submodule, which contains the controlled vocabulary for the ATMODAT Standard.

```bash
git submodule init
git submodule update
```

7. Set the `PYESSV_ARCHIVE_HOME` path  to where the `pyessv-archive` with the ATMODAT controlled vocabulary is stored.

For Linux/macOS use this command:
```bash
export PYESSV_ARCHIVE_HOME=${path_to_atmodat_checker}/AtMoDat_CVs/pyessv-archive
```
and replace `${path_to_atmodat_checker}` with the absolute path to the directory of the `atmodat_data_checker`. For regular usage of the checker, we recommend adding this line to your `.bashrc` or `.bash_profile`.

For Windows use this command:
```
set PYESSV_ARCHIVE_HOME "${path_to_atmodat_checker}\AtMoDat_CVs\pyessv-archive"
```
and replace `${path_to_atmodat_checker}` with the absolute path to the directory of the `atmodat_data_checker`. For regular usage of the checker, we recommend to permanently adding this path using:
```
setx PYESSV_ARCHIVE_HOME "${path_to_atmodat_checker}\AtMoDat_CVs\pyessv-archive"
```

8. It might be necessary to also set the `UDUNITS2_XML_PATH` path, which has to point to the `udunits2.xml` (see also [here](https://ncas-cms.github.io/cfunits/installation.html#dependencies). It is located in the `atmodat` conda environment. As a first step, find the base path to the `atmodat` conda environment (`atmodat_condapath`). You will find the `udunits2.xml` in `${atmodat_condapath}/share/udunits/` (for Linux/macOS) or `${atmodat_condapath}\Library\share\udunits` (for Windows). As for step 7, set the `UDUNITS2_XML_PATH` variable to the `udunits2.xml`.  


## How to run the ATMODAT Standard Checker

The command `run_checks` can be executed from any directory from within the `atmodat` conda environment. It will perform checks to evaluate the compliance with the ATMODAT Standard.  Compliance with the CF Conventions is checked by a call to the [CF checker](https://github.com/cedadev/cf-checker). The results of the performed checks are provided in the `checker_output` directory.

* To check a single file, use:
```bash
run_checks -f file_to_check.nc
```
* To run the checker on all `*.nc` files of a directory (including all sub-directories), use:
```bash
run_checks -p file_path
```
* To create a summary of the checks performed, add the ````-s```` flag, e.g.:
```bash
run_checks -s -p file_path
```
* To define a custom path into which the checker output shall be written, use:
```bash
run_checks -op output_path -p file_path
```
* To define the CF version against which the file(s) shall be checked, use:
```bash
run_checks -cfv 1.6 -p file_path
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Valid are versions from 1.4 to 1.8. Default is ````-cfv auto````. 

* To define whether the file(s) shall be checked only against the ATMODAT Standard (AT) or the CF Conventions (CF), specify either ````-check AT```` or ````-check CF````. 
```bash
run_checks -check AT -p file_path
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  Default is ````-check both````.

* You can combine different optional arguments, for example:
```bash
run_checks -s -op mychecks -check both -cfv 1.4 -p file_path
```
* For more information use:
```bash
run_checks --help
```

## Contributors

In alphabetic order:

- [Ag Stephens](https://github.com/agstephens)
- [Amandine Kaiser](https://github.com/am-kaiser), [ORCID: 0000-0002-2756-9964](https://orcid.org/0000-0002-2756-9964)
- [Anette Ganske](https://github.com/anganske), [ORCID: 0000-0003-1043-4964](https://orcid.org/0000-0003-1043-4964)
- [Angelika Heil](https://github.com/atmodatcode), [ORCID: 0000-0002-8768-5027](https://orcid.org/0000-0002-8768-5027)
- Angelina Kraft, [ORCID: 0000-0002-6454-335X](https://orcid.org/0000-0002-6454-335X)
- [Daniel Heydebreck](https://github.com/neumannd), [ORCID: 0000-0001-8574-9093](https://orcid.org/0000-0001-8574-9093)
- [Hugo Ricketts](https://github.com/gapintheclouds)
- [Jan Kretzschmar](https://github.com/jkretz), [ORCID: 0000-0002-8013-5831](http://orcid.org/0000-0002-8013-5831)


## Acknowledgements

The ATMODAT Standard Compliance Checker was created within the AtMoDat project (Atmospheric Model Data, <https://www.atmodat.de>). AtMoDat is funded by the German Federal Ministry for Education and Research within the framework of Atmosphären-Modelldaten: Datenqualität, Kurationskriterien und DOI-Branding (FKZ 16QK02A).
