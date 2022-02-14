#!/bin/bash -i


## usage: ./install_adc.sh mycustomenvname 
## mycustomenvname: specify a custom environment name. If not specified, the name will be atmodat.

if [ $# -gt 0 ] ; then
   new_env=$1
   mkdir -p $new_env;cd $new_env
fi


git clone https://github.com/AtMoDat/atmodat_data_checker.git
cd atmodat_data_checker || exit


if [ $# -gt 0 ] ; then
   new_env=$1
   sed -i.bak "s/atmodat/${new_env}/" environment.yml
fi

env_name=$(sed -n 2p environment.yml |cut -d: -f2|tr -d ' ')
echo "Installing atmodat checker in environment" "{$env_name}"

conda env create         # environment name is retrieved from environment.yml


conda activate $env_name
# shellcheck disable=SC1090
#source ~/anaconda3/bin/activate "$env_name"      #-- equivalent to conda activate ${env_name} in terminal
#source ~/anaconda3/etc/profile.d/conda.sh
conda env list

conda config --add channels conda-forge

mamba install --yes --file mamba_requirements.txt
pip install -U -e .

git submodule init
git submodule update  --remote --recursive


#=== install jupyterlab and create ipykernel with name of the environment

mamba install --yes -c conda-forge jupyterlab
mamba install --yes -c conda-forge cdo nco

python -m ipykernel install --user --name "${env_name}"kernel
