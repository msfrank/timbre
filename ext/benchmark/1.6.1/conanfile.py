from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

BENCHMARK_URL = "https://github.com/google/benchmark/archive/v1.6.1.tar.gz"
BENCHMARK_DOWNLOAD_NAME = "benchmark-1.6.1.tar.gz"
BENCHMARK_SOURCE_DIR = "benchmark-1.6.1"

class Benchmark(ConanFile):
    name = "benchmark"
    version = "1.6.1"
    user = "timbre"
    url = "https://github.com/google/benchmark"
    description = """
A library to benchmark code snippets, similar to unit tests.
"""

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "build_type", "compiler", "arch"

    def source(self):
        get(self, BENCHMARK_URL, filename=BENCHMARK_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=BENCHMARK_SOURCE_DIR, build_folder='benchmark')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['BUILD_SHARED_LIBS'] = 'ON'
        tc.cache_variables['BENCHMARK_ENABLE_TESTING'] = 'OFF'
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        copy(self, '*.h', self.build_folder, join(self.package_folder,'include'))
        copy(self, '*.dll', self.build_folder, join(self.package_folder,'bin'), keep_path=False)
        copy(self, '*.so', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, '*.dylib', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, '*.a', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, 'lib/cmake', self.build_folder, join(self.package_folder,'lib','cmake'))
        copy(self, 'LICENSE', self.source_folder, join(self.package_folder,'share'))

    def package_info(self):
        self.cpp_info.libs = ["benchmark"]
