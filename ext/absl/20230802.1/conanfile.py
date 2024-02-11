from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

ABSL_URL = "https://github.com/abseil/abseil-cpp/archive/refs/tags/20230802.1.tar.gz"
ABSL_DOWNLOAD_NAME = "abseil-cpp-20230802.1.tar.gz"
ABSL_SOURCE_DIR = "abseil-cpp-20230802.1"

class Absl(ConanFile):
    name = "absl"
    version = "20230802.1"
    user = "timbre"
    url = "https://abseil.io"
    description = """
Abseil is an open source collection of C++ libraries drawn from the most fundamental
pieces of Google’s internal codebase.
    """

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "compiler.cppstd": ["17"]}
    default_options = {"shared": True, "compiler.cppstd": "17"}

    def source(self):
        get(self, ABSL_URL, filename=ABSL_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=ABSL_SOURCE_DIR, build_folder='absl')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables['CMAKE_CXX_STANDARD'] = '17'
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        copy(self, '*.h', self.build_folder, join(self.package_folder, 'include'))
        copy(self, '*.so', self.build_folder, join(self.package_folder, 'lib'), keep_path=False)
        copy(self, '*.dylib', self.build_folder, join(self.package_folder, 'lib'), keep_path=False)
        copy(self, '*.a', self.build_folder, join(self.package_folder, 'lib'), keep_path=False)
        copy(self, '*', join(self.build_folder, 'lib','cmake'), join(self.package_folder, 'lib', 'cmake'))
        copy(self, 'LICENSE', self.source_folder, join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "absl"))
