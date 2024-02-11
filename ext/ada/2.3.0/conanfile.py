from os.path import join
import shutil

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

ADA_URL = "https://github.com/ada-url/ada/archive/refs/tags/v2.3.0.tar.gz"
ADA_DOWNLOAD_NAME = "ada-2.3.0.tar.gz"
ADA_SOURCE_DIR = "ada-2.3.0"

class Ada(ConanFile):
    name = "ada"
    version = "2.3.0"
    user = "timbre"
    url = "https://github.com/ada-url/ada"
    description = """
Ada is a fast and spec-compliant URL parser written in C++. Specification for URL parser can
be found from the WHATWG website.
    """

    settings = "os", "build_type", "compiler", "arch"
    options = {"shared": [False], "fPIC": [True]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        get(self, ADA_URL, filename=ADA_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=ADA_SOURCE_DIR, build_folder='ada')

    def generate(self):
        tc = CMakeToolchain(self)
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
        copy(self, '*.dll', self.build_folder, join(self.package_folder,'bin'), keep_path=False)
        copy(self, '*.so.*', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, '*.so', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, '*.dylib', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, '*.a', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, '*', join(self.build_folder, 'lib','cmake'), join(self.package_folder,'lib','cmake'))

    def package_info(self):
        self.cpp_info.libs = ["ada"]
