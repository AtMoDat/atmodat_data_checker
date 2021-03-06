# AtMoDat Standard Compliance Checks

This is a python library that contains checks to ensure compliance with the AtMoDat Standard.

Its core functionality is based on the [IOOS compliance checker](https://github.com/ioos/compliance-checker). The AtMoDat Standard Compliance Checks library makes use of [cc-yaml](https://github.com/cedadev/cc-yaml), which provides a plugin for the [IOOS compliance checker](https://github.com/ioos/compliance-checker) that generates check suites from YAML descriptions. Furthermore, the [Compliance Check Library](https://github.com/cedadev/compliance-check-lib) is used as the basis to define generic, reusable compliance checks. This repository is an extension of this library as it holds specific checks to ensure compliance with the AtMoDat Standard. Moreover, it contains checks to verify the compliance to the [AtMoDat CVs](https://github.com/AtMoDat/AtMoDat_CVs).

In addition the compliance to the CF Conventions 1.4 or higher is verified with the [CF checker](https://github.com/cedadev/cf-checker).

## Installation (only tested on a linux machine)

1. Clone this repository and update submodules (compliance-check-lib, cc-yaml and AtMoDat_CVs)

```bash
git clone https://github.com/AtMoDat/atmodat_data_checker.git
cd atmodat_data_checker
git submodule init
git submodule update
```

2. Install Python 3 via conda if necessary:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh -p $HOME/miniconda3 -b
rm -f Miniconda3-latest-Linux-x86_64.sh
```

3. Create conda environment and install the IOOS compliance checker via conda:

```bash
conda create --name atmodat_data_checker -y
conda activate atmodat_data_checker
conda install -c conda-forge compliance-checker pip -y
```

4. Install pyessv:

```bash
pip install pyessv
```

5. Install relevant checker packages:

- cc-yaml

```bash
cd cc-yaml
# pip install --editable . --no-deps (only necessary for developers)
pip install .
cd ..
```

- compliance-check-lib

```bash
cd compliance-check-lib
# pip install --editable . --no-deps (only necessary for developers)
pip install .
cd ..
```

- atmodat-checker

```bash
cd atmodat_data_checker
# pip install --editable . --no-deps (only necessary for developers)
pip install .
cd ..
```

5. Point `pyessv` at the "archive" where AtMoDat controlled vocabulary is stored

```bash
export PYESSV_ARCHIVE_HOME=$PWD/AtMoDat_CVs/pyessv-archive
```

6. Install CF Checker

```bash
pip install cfchecker
```

## Run tests

This repository contains the `atmodat_standard_checker_mandatory.yml`, `atmodat_standard_checker_recommended.yml` and  `atmodat_standard_checker_optional.yml` YAML files that contain the necessary checks. For running the mandatory, recommended and optional checks in one go, you can use `run_checks.py` python scirpt. The call to the CF checker is also included. The results of the checks will be outputted in the `checker_output` directory.

To run checkers on a single file, use:
```bash
python run_checks.py -f file_to_check.nc
```
To run the checker on all *.nc files of a directory, use:
```bash
python run_checks.py -p file_path
```
For more information use `python run_checks.py --help`

## Contributors

In alphabetic order:

- [Ag Stephens](https://github.com/agstephens)
- [Amandine Kaiser](https://github.com/am-kaiser), [ORCID: 0000-0002-2756-9964](https://orcid.org/0000-0002-2756-9964)
- [Anette Ganske](https://github.com/anganske), [ORCID: 0000-0003-1043-4964](https://orcid.org/0000-0003-1043-4964)
- Angelina Kraft, [ORCID: 0000-0002-6454-335X](https://orcid.org/0000-0002-6454-335X)
- [Daniel Heydebreck](https://github.com/neumannd), [ORCID: 0000-0001-8574-9093](https://orcid.org/0000-0001-8574-9093)
- [Hugo Ricketts](https://github.com/gapintheclouds)
- [Jan Kretzschmar](https://github.com/jkretz), [ORCID: 0000-0002-8013-5831](http://orcid.org/0000-0002-8013-5831)


## Acknowledgements

The ATMODAT Standard checker was created within the AtMoDat project (Atmospheric Model Data, <https://www.atmodat.de>). AtMoDat is funded by the German Federal Ministry for Education and Research within the framework of Atmosphären-Modelldaten: Datenqualität, Kurationskriterien und DOI-Branding (FKZ 16QK02A).
