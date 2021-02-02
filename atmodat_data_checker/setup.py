from setuptools import setup, find_packages
from atmodat_checklib import __version__

setup(
    name="atmodat_check_lib",
    description="Compliance Check Library for AtMoDat Standard - python library of compliance checks",
    version=__version__,
    author="Jan Kretzschmar, Amandine Kaiser",
    author_email="kaiser@dkrz.de",
    packages=find_packages(),
)
