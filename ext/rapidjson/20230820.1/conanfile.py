from os.path import join

from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get

RAPIDJSON_URL = "https://github.com/Tencent/rapidjson/archive/476ffa2fd272243275a74c36952f210267dc3088.tar.gz"
RAPIDJSON_DOWNLOAD_NAME = "rapidjson-20230820.tar.gz"
RAPIDJSON_SOURCE_DIR = "rapidjson-476ffa2fd272243275a74c36952f210267dc3088"

class Rapidjson(ConanFile):
    name = "rapidjson"
    version = "20230820.1"
    user = "timbre"
    url = "https://rapidjson.org"
    description = """
RapidJSON is a JSON parser and generator for C++.
"""

    def source(self):
        get(self, RAPIDJSON_URL, filename=RAPIDJSON_DOWNLOAD_NAME, strip_root=True)
 
    def layout(self):
        basic_layout(self, src_folder=RAPIDJSON_SOURCE_DIR)

    def package(self):
        copy(self, "*.h", join(self.source_folder, "include"), join(self.package_folder, "include"))
        copy(self, 'license.txt', self.source_folder, join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.includedirs = ["include"]
