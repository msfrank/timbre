from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

CAPNPROTO_URL = "https://github.com/capnproto/capnproto/archive/refs/tags/v1.2.0.tar.gz"
CAPNPROTO_DOWNLOAD_NAME = "capnproto-1.2.0.tar.gz"
CAPNPROTO_SOURCE_DIR = "capnproto-1.2.0"

class Nng(ConanFile):
    name = "capnproto"
    version = "1.2.0"
    user = "timbre"
    url = "https://capnproto.org"
    description = """
Cap’n Proto is an insanely fast data interchange format and capability-based RPC system.
    """

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "build_type", "compiler", "arch"

    def source(self):
        get(self, CAPNPROTO_URL, filename=CAPNPROTO_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=CAPNPROTO_SOURCE_DIR, build_folder='capnproto')

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables['CMAKE_CXX_STANDARD'] = '11'
        tc.variables['CMAKE_CXX_EXTENSIONS'] = 'ON'

        tc.cache_variables['BUILD_SHARED_LIBS'] = 'ON'
        tc.cache_variables['BUILD_TESTING'] = 'OFF'
        tc.cache_variables['WITH_OPENSSL'] = 'OFF'
        tc.cache_variables['WITH_ZLIB'] = 'OFF'
        tc.cache_variables['WITH_FIBERS'] = 'OFF'

        tc.cache_variables['CMAKE_INSTALL_RPATH_USE_LINK_PATH'] = 'ON'
        rpath = "@loader_path" if is_apple_os(self) else "\$ORIGIN"
        tc.variables['CMAKE_INSTALL_RPATH'] = rpath + '/../lib'

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
        copy(self, 'LICENSE', self.source_folder, join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "CapnProto"))

        self.buildenv_info.define('CAPNPROTO_CAPNP', join(self.package_folder, "bin", "capnp"))
