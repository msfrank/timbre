from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

CARES_URL = "https://github.com/c-ares/c-ares/releases/download/v1.34.6/c-ares-1.34.6.tar.gz"
CARES_DOWNLOAD_NAME = "cares-1.34.6.tar.gz"
CARES_SOURCE_DIR = "c-ares-1.34.6"

class Cares(ConanFile):
    name = "cares"
    version = "1.34.6"
    user = "timbre"
    url = "https://c-ares.org"
    description = """
c-ares is a C library for asynchronous DNS requests (including name resolves).
    """

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "build_type", "compiler", "arch"

    def source(self):
        get(self, CARES_URL, filename=CARES_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=CARES_SOURCE_DIR, build_folder='cares')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables['CARES_STATIC'] = 'ON'
        tc.cache_variables['CARES_SHARED'] = 'ON'
        tc.cache_variables['CARES_STATIC_PIC'] = 'ON'
        tc.cache_variables['CARES_BUILD_TESTS'] = 'OFF'
        tc.cache_variables['CMAKE_INSTALL_RPATH_USE_LINK_PATH'] = 'ON'
        tc.cache_variables['CMAKE_MACOSX_RPATH'] = 'ON'
        tc.cache_variables["CMAKE_INSTALL_RPATH"] = "@loader_path" if is_apple_os(self) else "\$ORIGIN/"
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
        copy(self, 'LICENSE.md', self.source_folder, join(self.package_folder,'share'))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "c-ares"))
