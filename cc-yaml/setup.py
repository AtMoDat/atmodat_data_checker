from setuptools import setup, find_packages

reqs = [line.strip() for line in open("requirements.txt")]

setup(
    name             = "cc-yaml",
    description      = "Compliance checker plugin to create checks from YAML descriptions",
    packages         = find_packages(),
    install_requires = reqs,
    entry_points     = {
        "compliance_checker.generators": [
            "yaml = cc_yaml.suite_generator:SuiteGenerator"
        ]
    }
)
