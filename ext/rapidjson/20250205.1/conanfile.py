from os.path import join

from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get

RAPIDJSON_URL = "https://github.com/Tencent/rapidjson/archive/24b5e7a8b27f42fa16b96fc70aade9106cf7102f.tar.gz"
RAPIDJSON_DOWNLOAD_NAME = "rapidjson-20250205_1.tar.gz"
RAPIDJSON_SOURCE_DIR = "rapidjson-24b5e7a8b27f42fa16b96fc70aade9106cf7102f"

class Rapidjson(ConanFile):
    name = "rapidjson"
    version = "20250205.1"
    user = "timbre"
    url = "https://rapidjson.org"
    description = """
RapidJSON is a JSON parser and generator for C++.
"""

    exports_sources = "include/*"
    no_copy_source = True
    package_type = "header-library"

    def source(self):
        get(self, RAPIDJSON_URL, filename=RAPIDJSON_DOWNLOAD_NAME, strip_root=True)
 
    def layout(self):
        basic_layout(self, src_folder=RAPIDJSON_SOURCE_DIR)

    def package(self):
        copy(self, "*.h", join(self.source_folder, "include"), join(self.package_folder, "include"))
        copy(self, 'license.txt', self.source_folder, join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
