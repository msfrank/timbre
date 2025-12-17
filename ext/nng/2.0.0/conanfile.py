from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

NNG_URL = "https://github.com/nanomsg/nng/archive/refs/tags/v2.0.0-alpha.6.tar.gz"
NNG_DOWNLOAD_NAME = "nng-2.0.0-alpha.6.tar.gz"
NNG_SOURCE_DIR = "nng-2.0.0-alpha.6"

class Nng(ConanFile):
    name = "nng"
    version = "2.0.0-alpha.6"
    user = "timbre"
    url = "https://nng.nanomsg.org"
    description = """
nanomsg-next-generation -- light-weight brokerless messaging
    """

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "build_type", "compiler", "arch"

    def source(self):
        get(self, NNG_URL, filename=NNG_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=NNG_SOURCE_DIR, build_folder='nng')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables['CMAKE_MACOSX_RPATH'] = 'ON'
        tc.cache_variables['CMAKE_INSTALL_RPATH_USE_LINK_PATH'] = 'ON'
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
        #fix_apple_shared_install_name(self)
        copy(self, 'LICENSE.txt', self.source_folder, join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "nng"))
