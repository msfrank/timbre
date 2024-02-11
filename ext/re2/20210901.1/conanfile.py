from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

RE2_URL = "https://github.com/google/re2/archive/refs/tags/2021-09-01.tar.gz"
RE2_DOWNLOAD_NAME = "re2-2021-09-01.tar.gz"
RE2_SOURCE_DIR = "re2-2021-09-01"

class Re2(ConanFile):
    name = "re2"
    version = "20210901.1"
    user = "timbre"
    url = "https://github.com/google/re2"
    description = """
RE2 is a fast, safe, thread-friendly alternative to backtracking regular expression
engines like those used in PCRE, Perl, and Python.
"""

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "compiler.cppstd": ["17"]}
    default_options = {"shared": True, "compiler.cppstd": "17"}

    def source(self):
        get(self, RE2_URL, filename=RE2_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=RE2_SOURCE_DIR, build_folder='re2')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['BUILD_SHARED_LIBS'] = 'ON'
        tc.variables['CMAKE_POSITION_INDEPENDENT_CODE'] = 'ON'   # force PIC
        tc.variables['CMAKE_INSTALL_RPATH_USE_LINK_PATH'] = 'ON' # force append link paths to rpath
        tc.cache_variables['RE2_BUILD_TESTING'] = 'OFF'
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        copy(self, "LICENSE", self.source_folder, join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = [ "re2" ]
