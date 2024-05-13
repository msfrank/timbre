from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

CURL_URL = "https://curl.se/download/curl-8.5.0.tar.gz"
CURL_DOWNLOAD_NAME = "curl-8.5.0.tar.gz"
CURL_SOURCE_DIR = "curl-8.5.0"

class Curl(ConanFile):
    name = "curl"
    version = "8.5.0"
    user = "timbre"
    url = "https://curl.se"
    description = """
Command line tool and library for transferring data with URLs (since 1998).
"""

    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires("cares/1.23.0@timbre")
        self.requires("openssl/3.2.0@timbre")

    def source(self):
        get(self, CURL_URL, filename=CURL_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=CURL_SOURCE_DIR, build_folder='curl')

    def generate(self):
        tc = CMakeToolchain(self)

        # ensure library name is the same for release and debug builds
        tc.variables['CMAKE_DEBUG_POSTFIX'] = ''

        # curl has a custom find script that searches for ares.h. setting CMAKE_PREFIX_PATH helps
        # the find_* commands detect the cares headers and libraries.
        tc.variables['CMAKE_PREFIX_PATH'] = self.dependencies['cares'].cpp_info.includedirs

        # curl uses the default cmake FindOpenSSL script, which takes OPENSSL_ROOT_DIR as a hint
        # to locate the openssl headers and libraries.
        tc.variables['OPENSSL_ROOT_DIR'] = self.dependencies['openssl'].package_folder

        tc.cache_variables['BUILD_CURL_EXE'] = 'OFF'
        tc.cache_variables['BUILD_TESTING'] = 'OFF'
        tc.cache_variables['CURL_ENABLE_SSL'] = 'ON'
        tc.cache_variables['CURL_USE_OPENSSL'] = 'ON'
        tc.cache_variables['ENABLE_ARES'] = 'ON'
        tc.cache_variables['CMAKE_INSTALL_RPATH_USE_LINK_PATH'] = 'ON'

        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        # copy license file to share/ package directory
        copy(self, 'COPYING', self.build_folder, join(self.package_folder,'share'))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "CURL"))
        self.conf_info.define('user.curl.license_file', join(self.package_folder, 'share', 'COPYING'))
