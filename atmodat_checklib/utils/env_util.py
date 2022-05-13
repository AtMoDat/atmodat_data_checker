import os
from pathlib import Path
import platform

UDUNITS_PATH_LINUX = ['share', 'udunits']
UDUNITS_PATH_WINDOWS = ['Library', 'share', 'udunits']


def set_env_variables():

    try:
        os.environ["UDUNITS2_XML_PATH"]
    except KeyError:
        if platform.system() == 'Windows':
            udunits_local_path = UDUNITS_PATH_WINDOWS
        else:
            udunits_local_path = UDUNITS_PATH_LINUX

        udunits2_xml_path_out = None
        for binpath in os.environ["PATH"].split(':'):
            searchpath = Path(binpath).parents[0]
            udunits_search_path = os.path.join(searchpath, *udunits_local_path)
            if os.path.isdir(udunits_search_path):
                udunits2_xml_path_out = os.path.join(udunits_search_path, 'udunits2.xml')
                break

        if not udunits2_xml_path_out:
            raise RuntimeError("Could not find udunits xml path")

    else:
        udunits2_xml_path_out = os.environ["UDUNITS2_XML_PATH"]

    # PYESSV_ARCHIVE_PATH
    atmodat_cv_base_path = str(Path(__file__).resolve().parents[1])
    pyessv_archive_home_out = os.path.join(atmodat_cv_base_path, 'AtMoDat_CVs')

    return udunits2_xml_path_out, pyessv_archive_home_out
