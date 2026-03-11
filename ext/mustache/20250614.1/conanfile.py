from os.path import join

from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get

MUSTACHE_URL = "https://github.com/kainjow/Mustache/archive/3f654942a70c46a775070d7a09ca7acfa3e205b7.tar.gz"
MUSTACHE_DOWNLOAD_NAME = "Mustache-3f654942a70c46a775070d7a09ca7acfa3e205b7.tar.gz"
MUSTACHE_SOURCE_DIR = "Mustache-3f654942a70c46a775070d7a09ca7acfa3e205b7"

class Mustache(ConanFile):
    name = "mustache"
    version = "20250614.1"
    user = "timbre"
    url = "https://github.com/kainjow/Mustache"
    description = """
Mustache text templates for modern C++
"""

    exports_sources = "mustache.hpp"
    no_copy_source = True
    package_type = "header-library"

    revision_mode = "scm_folder"
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    def source(self):
        get(self, MUSTACHE_URL, filename=MUSTACHE_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=MUSTACHE_SOURCE_DIR)

    def package(self):
        copy(self, "mustache.hpp", self.source_folder, join(self.package_folder, "include", "mustache"))
        copy(self, 'LICENSE', self.source_folder, join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
