from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

HDRHISTOGRAM_URL = "https://github.com/HdrHistogram/HdrHistogram_c/archive/0.9.6.tar.gz"
HDRHISTOGRAM_DOWNLOAD_NAME = "hdr-histogram-0.9.6.tar.gz"
HDRHISTOGRAM_SOURCE_DIR = "HdrHistogram_c-0.9.6"

class Hdrhistogram(ConanFile):
    name = "hdrhistogram"
    version = "0.9.6"
    user = "timbre"
    url = "http://hdrhistogram.org"
    description = """
HDR Histogram is designed for recoding histograms of value measurements in latency and performance sensitive applications. 
"""

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    def source(self):
        get(self, HDRHISTOGRAM_URL, filename=HDRHISTOGRAM_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=HDRHISTOGRAM_SOURCE_DIR, build_folder='hdrhistogram')

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
        copy(self, "*.h", self.build_folder, join(self.package_folder, "include"))
        copy(self, "*.so", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        # copy license file to share/ package directory
        copy(self, "LICENSE.txt", self.source_folder, join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["hdr_histogram"]
