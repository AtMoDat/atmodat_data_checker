# AtMoDat Standard Compliance Checks


#Online Demo



Try it out on binder: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/AtMoDat/atmodat_data_checkere/HEAD?filepath=notebooks)




```
To run the checker on all *.nc files of a directory (including all sub-directories), use:
```bash
run_checks.py -p file_path
```
To create summary of checker ouput add the ````-s```` flag, e.g.:
```bash
run_checks.py -s -p file_path
```
To define a custom path where the checker output shall be written, use:
```bash
run_checks.py -op output_path -p file_path
```
To define a CF version against which the file(s) shall be checked, use:
```bash
run_checks.py -cfv 1.6 -p file_path
```
Valid are versions from 1.3 to 1.8. Default is ````-cfv auto````. 

To define if the file(s) shall be checked only against the ATMODAT Standard (AT) or the CF Conventions (CF), specify either ````-check AT```` or ````-check CF````.
Default is ````-check both````. 
```bash
run_checks.py -check AT -p file_path
```
You can combine different optional arguments, for example:
```bash
run_checks.py -s -op mychecks -check both -cfv 1.4 -p file_path
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
