Ancillary files contained in this folder:

install_adc.sh: shell script to automate the installation of the atmodat data checker (adc).
The script allows you to define the name of the conda environment in which the checker is installed.
Besides the atmodat data checker, the scripts also installs CDOs, NCOs and Jupyter Lab (with a adc kernel).

To use the script, please make sure the install_adc.sh is executable (chmod +x install_adc.sh).
Then run the script either like
./install_adc.sh
--> installation of atmodat checker in conda environment named 'atmodat'
./install_adc.sh myenvname 
--> installation of atmodat checker in conda environment named 'myenvname'

