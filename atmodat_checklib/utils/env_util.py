import os
from pathlib import Path
import platform


def set_env_variables():

    # Verify we are in atmodat conda environment
    try:
        atmodat_conda_envpath = os.environ["CONDA_PREFIX"]
    except KeyError:
        atmodat_conda_envpath = os.environ["CONDA"]

    # UDUNITS2_XML_PATH
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        udunits2_xml_path_out = os.path.join(atmodat_conda_envpath, 'share', 'udunits', 'udunits2.xml')
    elif platform.system() == 'Windows':
        udunits2_xml_path_out = os.path.join(atmodat_conda_envpath, 'Library', 'share', 'udunits', 'udunits2.xml')

    # PYESSV_ARCHIVE_PATH
    atmodat_base_path = str(Path(__file__).resolve().parents[2])
    pyessv_archive_home_out = os.path.join(atmodat_base_path, 'AtMoDat_CVs', 'pyessv-archive')

    return udunits2_xml_path_out, pyessv_archive_home_out
