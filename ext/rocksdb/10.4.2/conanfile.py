from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

ROCKSDB_URL = "https://github.com/facebook/rocksdb/archive/refs/tags/v10.4.2.tar.gz"
ROCKSDB_DOWNLOAD_NAME = "rocksdb-10.4.2.tar.gz"
ROCKSDB_SOURCE_DIR = "rocksdb-10.4.2"

class Rocksdb(ConanFile):
    name = "rocksdb"
    version = "10.4.2"
    user = "timbre"
    url = "https://rocksdb.org"
    description = """
A Persistent Key-Value Store for Flash and RAM Storage.
"""

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    def source(self):
        get(self, ROCKSDB_URL, filename=ROCKSDB_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=ROCKSDB_SOURCE_DIR, build_folder='rocksdb')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables['WITH_GFLAGS'] = 'OFF'
        tc.cache_variables['WITH_ZLIB'] = 'ON'
        tc.cache_variables['WITH_TESTS'] = 'OFF'
        tc.cache_variables['WITH_TOOLS'] = 'OFF'
        tc.cache_variables['WITH_BENCHMARK_TOOLS'] = 'OFF'
        tc.cache_variables['CMAKE_INSTALL_LIBDIR'] = 'lib'
        tc.cache_variables['CMAKE_CXX_FLAGS'] = '-Wno-deprecated-declarations -Wno-nontrivial-memcall'
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        copy(self, "*.h", self.build_folder, join(self.package_folder, "include"))
        copy(self, "*.so", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "LICENSE.Apache", self.source_folder, join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["rocksdb"]
