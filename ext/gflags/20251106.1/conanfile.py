from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

GFLAGS_URL = "https://github.com/gflags/gflags/archive/3398b59cedbd3575e997470734f8e69c26a752f2.tar.gz"
GFLAGS_DOWNLOAD_NAME = "gflags-3398b59cedbd3575e997470734f8e69c26a752f2.tar.gz"
GFLAGS_SOURCE_DIR = "gflags-3398b59cedbd3575e997470734f8e69c26a752f2"

class Gflags(ConanFile):
    name = "gflags"
    version = "20251106.1"
    user = "timbre"
    url = "https://github.com/gflags/gflags"
    description = """
The gflags package contains a C++ library that implements commandline flags processing.
"""

    settings = "os", "build_type", "compiler", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    def source(self):
        get(self, GFLAGS_URL, filename=GFLAGS_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=GFLAGS_SOURCE_DIR, build_folder='gflags')

    def generate(self):
        tc = CMakeToolchain(self)
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
        copy(self, '*.h', self.build_folder, join(self.package_folder,'include'))
        copy(self, '*.dll', self.build_folder, join(self.package_folder,'bin'), keep_path=False)
        copy(self, '*.so', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, '*.dylib', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, '*.a', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, 'lib/cmake', self.build_folder, join(self.package_folder,'lib','cmake'))
        copy(self, 'COPYING.txt', self.source_folder, join(self.package_folder,'share'))

    def package_info(self):
        self.cpp_info.libs = ["gflags"]
