from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

FMT_URL = "https://github.com/fmtlib/fmt/releases/download/9.1.0/fmt-9.1.0.zip"
FMT_DOWNLOAD_NAME = "fmt-9.1.0.zip"
FMT_SOURCE_DIR = "fmt-9.1.0"

class Fmt(ConanFile):
    name = "fmt"
    version = "9.1.0"
    user = "timbre"
    url = "https://fmt.dev"
    description = """
{fmt} is an open-source formatting library providing a fast and safe alternative to C stdio and C++ iostreams.
"""

    settings = "os", "build_type", "compiler", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    def source(self):
        get(self, FMT_URL, filename=FMT_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=FMT_SOURCE_DIR, build_folder='fmt')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables['FMT_DEBUG_POSTFIX'] = ''    # disable appending 'd' to library name in debug mode
        tc.cache_variables['FMT_TEST'] = 'OFF'          # disable tests
        tc.cache_variables['BUILD_SHARED_LIBS'] = 'ON'  # always build shared libraries
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
        copy(self, "*.dll", self.build_folder, join(self.package_folder, "bin"), keep_path=False)
        copy(self, "*.so", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "lib/cmake", self.build_folder, join(self.package_folder, "lib","cmake"))

    def package_info(self):
        self.cpp_info.libs = ["fmt"]
