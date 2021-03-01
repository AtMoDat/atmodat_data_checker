"""module to create output directory"""

from pathlib import Path
from datetime import datetime


global opath, opath_base

# Get current date and time
now = datetime.now()
now_formatted = now.strftime("%Y%m%d_%H%M") + '/'

# Get parent of parent directory of current file 
opath_base = str(Path(__file__).resolve().parents[2])

# Define output path for result files
if opath_base:
    opath = opath_base + '/checker_output/' + now_formatted
else:
    opath = 'checker_output/' + now_formatted

