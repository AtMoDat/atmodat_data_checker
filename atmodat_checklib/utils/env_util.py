import os
from pathlib import Path


def set_env_variables():

    # Verify we are in atmodat conda environment
    atmodat_conda_envpath = os.environ["CONDA_PREFIX"]
    if not atmodat_conda_envpath.endswith('atmodat'):
        raise RuntimeError('Not in atmodat conda environment')

    # UDUNITS2_XML_PATH
    udunits2_xml_path_out = atmodat_conda_envpath + '/share/udunits/udunits2.xml'

    # Set
    atmodat_base_path = str(Path(__file__).resolve().parents[2])
    pyessv_archive_home_out = atmodat_base_path + '/AtMoDat_CVs/pyessv-archive'

    return udunits2_xml_path_out, pyessv_archive_home_out
