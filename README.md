[![DOI](https://zenodo.org/badge/286954083.svg)](https://zenodo.org/badge/latestdoi/286954083)

# ATMODAT Standard Compliance Checker

This is a python library that contains checks to ensure compliance with the ATMODAT Standard.

Its core functionality is based on the [IOOS compliance checker](https://github.com/ioos/compliance-checker). The ATMODAT Standard Compliance Checker library makes use of [cc-yaml](https://github.com/cedadev/cc-yaml), which provides a plugin for the [IOOS compliance checker](https://github.com/ioos/compliance-checker) that generates check suites from YAML descriptions. Furthermore, the [Compliance Check Library](https://github.com/cedadev/compliance-check-lib) is used as the basis to define generic, reusable compliance checks. This repository is an extension of this library as it holds specific checks to ensure compliance with the ATMODAT Standard.

In addition, the compliance to the CF Conventions 1.4 or higher is verified with the [CF checker](https://github.com/cedadev/cf-checker).

<!---
We set up a binder where you can try out the functionalities of the ATMODAT Standard Compliance Checker:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/AtMoDat/atmodat_data_checker/HEAD?filepath=notebooks)
-->

## Installation (tested on Linux, macOS and Windows)

1. Install Miniconda or Anaconda (if not already done). Follow the [respective instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation) for your operating system.


2. Open a Terminal / Anaconda Prompt (under Windows)


3. If not already installed, a version of git is needed to clone repository of the checker from GitHub. It can be installed using conda:
    ```bash
   conda install -c anaconda git
    ```
   Clone this repository:

   ```bash
   git clone https://github.com/AtMoDat/atmodat_data_checker.git
   cd atmodat_data_checker
   ```

4. Create conda environment and install the needed anaconda packages (via mamba):
   ```bash
   conda env create -f environment.yml
   conda activate atmodat
   conda config --add channels conda-forge
   mamba install --file mamba_requirements.txt
   ```

5. Install (and upgrade) atmodat-checker
   ```bash
   pip install -U -e .
   ```

6. Initialize and update the [ATMODAT CVs](https://github.com/AtMoDat/AtMoDat_CVs) submodule, which contains the controlled vocabulary for the ATMODAT Standard.
   ```bash
   git submodule init
   git submodule update  --remote --recursive
   ```

## Update the preinstalled checker 
The ATMODAT Standard Compliance Checker and related packages can be updated to its latest version (GitHub master branch) as follows:
```bash
git checkout master
git fetch || git pull origin master || git submodule update --remote --recursive
mamba update --file mamba_requirements.txt
pip install -U -e .
```

## How to run the ATMODAT Standard Checker

The command `run_checks` can be executed from any directory from within the `atmodat` conda environment. It will perform checks to evaluate the compliance with the ATMODAT Standard.  Compliance with the CF Conventions is checked by a call to the [CF checker](https://github.com/cedadev/cf-checker). The results of the performed checks are provided in the `checker_output` directory. 
By default, `run_checks` assumes writing permissions in the path where the atmodat checker is installed. If this is not the case, you must specify an output directory where you possess writing permissions with the `-op output_path`.

* To check a single file, use:
   ```bash
   run_checks -f file_to_check.nc
   ```
* To run the checker on all `*.nc` files of a directory (including all sub-directories), use:
   ```bash
   run_checks -p file_path
   ```
* To create a summary of the checks performed, add the `-s` flag, e.g.:
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
   Valid are versions from 1.4 to 1.8. Default is `-cfv auto`.


* To define whether the file(s) shall be checked only against the ATMODAT Standard (AT) or the CF Conventions (CF), specify either `-check AT` or `-check CF`. 
  ```bash
   run_checks -check AT -p file_path
  ```
   Default is `-check both`.


* You can combine different optional arguments, for example:
   ```bash
   run_checks -s -op mychecks -check both -cfv 1.4 -p file_path
  ```
* For more information use:
  ```bash
  run_checks --help
  ```

## Filling global/variable attribute
To ensure compliance with the CF Conventions and the ATMODAT Standard, it might be necessary to adapt the variable and global attributes. To support this process, the `fill_attributes` script is provided as part of the checker which can be used to fill the respective attributes into netCDF files from csv files. Basic examples for these csv files are provided [here](atmodat_checklib/utils/fill_attributes/attribute_templates). These files can be modified to add/change global attributes and to rename variables and add/change their respective attributes. 



### Usage
To run this script, it is necessary to provide the directory where the csv files are stored (`-a csv_directory`). The scirpt can modify a single file or all netCDF files in a given directory. In case you provide a directory, all netCDF files will be identified and modified recursively. Use the `-p` option and give the path/directory of the file(s) to be modified. 

The typical command-line string to run the attribute filler looks like this:
  ```bash
  fill_attributes -a csv_directory -p file_path/directory
  ```
Presently, the original fill will simply be amended to save runtime due to reduced I/O operations. A backup of the original global/variable for each file is created in the `csv_directory`. The original state of the file/directory can be restored using the `-r` option (files will nevertheless not be bit-identical):
  ```bash
  fill_attributes -r -a csv_directory -p file_path/directory
  ```

## Known Issues
* Presently, there is an unresolved issue in the CF checker (v 4.1.0, [see here](https://github.com/cedadev/cf-checker/issues/75)). Until it will get resolved, this issue will output an error that is related to the `formula_terms` attribute in so-called boundary variables. As this is related to the CF checker, we will simply ignore errors that are related to this issue in the `short_summary` output of the checker.

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
