import os
from pathlib import Path
import platform

UDUNITS_PATH_WINDOWS=['share', 'udunits']
UDUNITS_PATH_LINUX=['Library', 'share', 'udunits']

def set_env_variables():

    # Verify we are in atmodat conda environment
    if not os.environ["UDUNITS2_XML_PATH"] :
        
        if platform.system() == 'Windows' :
            udunits_local_path=UDUNITS_PATH_WINDOWS
        else :
            udunits_local_path=UDUNITS_PATH_LINUX
            
        for binpath in os.environ["PATH"].split(':') :
            searchpath=binpath.split(os.path.sep)[:-1]
            if os.path.isfile(os.path.join([searchpath]+ udunits_local_path)):
                udunits2_xml_path_out=os.path.join([binpath]+ udunits_local_path)
                break
        if not udunits2_xml_path_out:
            raise RuntimeError("Could not find udunits xml path")
    else :
        udunits2_xml_path_out=os.environ["UDUNITS2_XML_PATH"]

    # PYESSV_ARCHIVE_PATH
    atmodat_cv_base_path = str(Path(__file__).resolve().parents[1])
    pyessv_archive_home_out = os.path.join(atmodat_cv_base_path, 'AtMoDat_CVs')

    return udunits2_xml_path_out, pyessv_archive_home_out
