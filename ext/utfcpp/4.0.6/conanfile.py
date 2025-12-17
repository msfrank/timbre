from os.path import join

from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get

UTFCPP_URL = "https://github.com/nemtrif/utfcpp/archive/refs/tags/v4.0.6.tar.gz"
UTFCPP_DOWNLOAD_NAME = "utfcpp-4.0.6.tar.gz"
UTFCPP_SOURCE_DIR = "utfcpp-4.0.6"

class Utfcpp(ConanFile):
    name = "utfcpp"
    version = "4.0.6"
    user = "timbre"
    url = "https://github.com/nemtrif/utfcpp"
    description = """
UTF-8 with C++ in a Portable Way
"""

    exports_sources = "include/*"
    no_copy_source = True
    package_type = "header-library"

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    def source(self):
        get(self, UTFCPP_URL, filename=UTFCPP_DOWNLOAD_NAME, strip_root=True)
 
    def layout(self):
        basic_layout(self, src_folder=UTFCPP_SOURCE_DIR)

    def package(self):
        copy(self, "*.h", join(self.source_folder, "source"), join(self.package_folder, "include"))
        copy(self, 'LICENSE', self.source_folder, join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
