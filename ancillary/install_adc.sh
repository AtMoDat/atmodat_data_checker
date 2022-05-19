#!/bin/bash

if [ $# -gt 0 ] ; then
   new_env=$1
   git clone https://github.com/AtMoDat/atmodat_data_checker.git $new_env
   cd $new_env || exit
   sed -i.bak "s/atmodat/${new_env}/" environment.yml
else
   git clone https://github.com/AtMoDat/atmodat_data_checker.git
   cd atmodat_data_checker || exit
fi

env_name=$(sed -n 2p environment.yml |cut -d: -f2|tr -d ' ')
echo "Installing atmodat checker in environment" "$env_name"

conda env create         # environment name is retrieved from environment.yml

source ~/anaconda3/bin/activate "$env_name"      #-- equivalent to conda activate ${env_name} in terminal
mamba install --yes --file mamba_requirements.txt
pip install -U -e .
git submodule init
git submodule update --remote --recursive


#=== install jupyterlab and create ipykernel with name of the environment
#=== also install cdo and nco
mamba install --yes -c conda-forge jupyterlab
mamba install --yes -c conda-forge cdo nco

python -m ipykernel install --user --name "$env_name"kernel

echo "finished installing $env_name
      you can now activate the atmodat checker environment with
      conda activate $env_name"
