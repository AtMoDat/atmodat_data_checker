# A quick-start guide to the compliance check library

This quick-start guide includes some recipes for working with different
parts of the compliance checking framework. 

## Creating a "checks" file for a new project 

### Install the required packages

Do all the following on  a linux machine...

1. Install Python 3 via conda:

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh -p $HOME/miniconda3 -b

rm -f Miniconda3-latest-Linux-x86_64.sh
```

2. Create conda environment: amf-checker-env

```
export PATH=$HOME/miniconda3/bin:$PATH
conda create --name amf-checker-env -y

conda activate amf-checker-env
conda install -c conda-forge compliance-checker pip -y
```

3. Get the relevant checker packages installed

```
WORK_DIR=$PWD/checker
mkdir -p $WORK_DIR

cd $WORK_DIR/

# Install: cc-yaml
git clone https://github.com/cedadev/cc-yaml
cd cc-yaml/

pip install --editable . --no-deps
pip install -r requirements.txt

cd ../

# Install: compliance-check-lib
git clone https://github.com/cedadev/compliance-check-lib
cd compliance-check-lib/

pip install --editable . --no-deps
pip install -r requirements.txt

# Install: sub-repository
git submodule update --init --recursive
export PYESSV_ARCHIVE_HOME=$PWD/cc-vocab-cache/pyessv-archive-eg-cvs

```

Test the compliance works:

```
cchecker.py --test cf:1.6 checklib/test/example_data/nc_file_checks_data/simple_nc.nc
```

4. Add and point to the CMIP6 controlled vocabularies

Pull the CMIP6 CVs - formatted for the `pyessv` library.

```
cd $WORK_DIR/
git clone https://github.com/ES-DOC/pyessv-archive

# Point `pyessv` at the "archive" where CMIP6 is stored 
export PYESSV_ARCHIVE_HOME=$PWD/pyessv-archive

# Test it works
python -c 'import pyessv; cmip6 = pyessv.WCRP.cmip6; assert isinstance(cmip6, pyessv.Scope);'

```

5. Add a new YAML file to specify some CV checks 

Create a local file called `my-proj-suite.yml`:

```
# Write a suite of checks in a YAML file
cat <<EOF > my-proj-suite.yml
suite_name: "my-proj-suite:1.0"

checks:
  - check_id: "filesize_check"
    parameters: {"threshold": 1}
    check_name: "checklib.register.FileSizeCheck"

  - check_id: "filename_check"
    parameters: {"delimiter": "_", "extension": ".nc"}
    check_name: "checklib.register.FileNameStructureCheck"

  - check_id: "frequency_attribute_check"
    parameters: {"attribute": "frequency", "vocab_lookup": "label", "vocabulary_ref": "WCRP:cmip6"}
    check_name: "checklib.register.GlobalAttrVocabCheck"

EOF
```
Now run the checker on a sample file with those checks:

```
cchecker.py --yaml my-proj-suite.yml --test my-proj-suite:1.0 compliance-check-lib/checklib/test/example_data/nc_file_checks_data/simple_nc.nc
```

NOTE: the final check will check the `frequency` global attribute is in the CMIP6 CVs.

