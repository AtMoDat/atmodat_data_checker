from cc_yaml.yaml_parser import YamlParser


class SuiteGenerator(object):
    """
    Interface between compliance-checker plugin system and YAML loading.
    Provides methods to get checker classes based on command-line arguments.
    """

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("-y", "--yaml", action="append", dest="yaml_files",
                            default=[], help="Specify YAML file(s) to generate "
                                             "check suites from")

    @classmethod
    def get_checkers(cls, args):
        """
        :param args: argparse arguments object
        :return:     dictionary mapping check name to checker class
        """
        checkers = {}
        for filename in args.yaml_files:
            checker = YamlParser.get_checker_class(filename)
            checkers[checker.__name__] = checker
        return checkers
