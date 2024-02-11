from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

CROARING_URL = "https://github.com/RoaringBitmap/CRoaring/archive/refs/tags/v1.1.5.tar.gz"
CROARING_DOWNLOAD_NAME = "croaring-1.1.5.tar.gz"
CROARING_SOURCE_DIR = "CRoaring-1.1.5"

class Croaring(ConanFile):
    name = "croaring"
    version = "1.1.5"
    user = "timbre"
    url = "https://roaringbitmap.org"
    description = """
Portable Roaring bitmaps in C (and C++) with full support for your favorite compiler (GNU GCC,
LLVM's clang, Visual Studio, Apple Xcode, Intel oneAPI).
"""

    settings = "os", "build_type", "compiler", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    def source(self):
        get(self, CROARING_URL, filename=CROARING_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=CROARING_SOURCE_DIR, build_folder='croaring')

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
        copy(self, "*", join(self.build_folder, 'include'), join(self.package_folder, "include"))
        copy(self, "*", join(self.build_folder, 'lib'), join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["roaring"]
