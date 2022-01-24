# Changelog
All notable changes to this project will be documented in this file.

## [Unreleased]
### Added:
- Check file existence when running on single file (#48)
- Add possibility to run the ATMODAT Standard Compliance Checker in a binder
- Make the AtMoDaT Standard Compliance Checker compatible with Windows (#69)
- Add Changelog.md (#79)
- Add non-recursive file search when path to multiple files is provided (-pnr option) (#81)
- Add information on how to update the ATMODAT Standard Compliance Checker (and related packages)
- Add tests for run_checks.py (check for expected number of missing attributes in demo_data) (#97)
- Add output of version number via -V option (#111)
- Allow for installation form github via pip (#111) 

### Changed:
- Add cfunits to environment.yml to fix tests (#52)
- Large revision of README.md (#51)
- Avoid checking for existence the Conventions attribute multiple times (#54)
- Fixing CV checks (#59) and adapt checker to run with new compliance-check-lib version (#68)
- Speed up checking of multiple files (#66)
- Fixing -op option 
- Fix command-line string size issue (#80)
- Use mamba to install required conda packages (#83)
- Ignoring errors related to formula_terms in boundary variables (#84)
- Set environment variables during runtime of checker (#85)
- Do not delete content of output directory (#88)
- Restructure the content and use of submodules (#101) 
- Make "point" entry in geospatial_lat/lon_resolution a valid entry (#111)

### Removed:

## Version [1.1] - 2021-07-07
This is the state before the CHANGELOG.md has been created. From here on, all changes will be tracked.

[Unreleased]: https://github.com/AtMoDat/atmodat_data_checker/compare/v1.1...HEAD
[1.1]: https://github.com/AtMoDat/atmodat_data_checker/compare/v1.0...v1.1