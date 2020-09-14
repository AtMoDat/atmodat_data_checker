import os
from datetime import datetime


class PyessvWriter(object):

    def __init__(self, pyessv_root=None):
        if pyessv_root:
            os.environ["PYESSV_ARCHIVE_HOME"] = pyessv_root

        # Not normally good to import modules anywhere except top of the file,
        # but pyessv loads archive directory from an environment variable when
        # the module is imported. This means we cannot change the archive
        # directory from the code unless it is imported afterwards...
        #
        # This also prevents cluttering output with pyessv's logs even when CVs
        # are not being generated
        import pyessv
        self._pyessv = pyessv

        self.create_date = datetime.now()

        self.authority = pyessv.create_authority(
            "AtMoDat",
            "AtMoDat Standard CVs",
            label="AtMoDat",
            url="https://www.atmodat.de/",
            create_date=self.create_date
        )

        self.scope_asc = pyessv.create_scope(
            self.authority,
            "atmodat_standard_checker",
            "Controlled Vocabularies (CVs) for use in ATMODAT Standard checker",
            label="atmodat_standard_checker",
            url="https://github.com/AtMoDat/AtMoDat_CVs.git",
            create_date=self.create_date
        )

        # Make sure to include '@' for email addresses
        self.term_regex = r"^[a-z0-9\-@\.]*$"

    def write_cvs(self, cvs):
        print("Writing to pyessv archive...")
        for cv in cvs:
            print(cv)
            collection = self._pyessv.create_collection(
                self.scope_asc,
                cv.namespace,
                "ATMODAT Standard CV collection: {}".format(cv.namespace),
                create_date=self.create_date,
                term_regex=self.term_regex
            )
            # Note: This relies on the namespace being a top level key in CV
            # dictionary
            inner_cv = cv.cv_dict[cv.namespace]
            # If inner_cv is a dict then use keys for term names and values for
            # 'data' attribute. Otherwise (e.g. inner_cv is a list), ommit data
            # attribute
            for name in inner_cv:
                kwargs = {}
                if isinstance(inner_cv, dict):
                    kwargs["data"] = inner_cv[name]

                self._pyessv.create_term(collection, name=name, label=name,
                                         create_date=self.create_date,
                                         **kwargs)
            self._pyessv.archive(self.authority)


if __name__ == "__main__":
    import json

    file_path = '/mnt/c/Users/k204223/Nextcloud/AtMoDat/02_AtMoDat_Standard/03_netCDF_checker/01_IOOS_plugin_generator/03_Python_scripts/checker/create_pyessv_archive/atmodat_cvs/test.json'
    with open(file_path) as f:
        data = json.load(f)
        print(data["namespace"])
        #writer = PyessvWriter()
        #writer.write_cvs(f)

