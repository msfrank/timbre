from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

GTEST_URL = "https://github.com/google/googletest/archive/refs/tags/v1.17.0.tar.gz"
GTEST_DOWNLOAD_NAME = "gtest-1.17.0.tar.gz"
GTEST_SOURCE_DIR = "googletest-1.17.0"

class Gtest(ConanFile):
    name = "gtest"
    version = "1.17.0"
    user = "timbre"
    url = "https://github.com/google/googletest"
    description = """
GoogleTest is Google’s C++ testing and mocking framework.
"""

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, GTEST_URL, filename=GTEST_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=GTEST_SOURCE_DIR, build_folder='gtest')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables['CMAKE_BUILD_TYPE'] = 'Release'  # force the release build
        tc.cache_variables['BUILD_SHARED_LIBS'] = 'ON'
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        gtest_source_dir =join(self.source_folder, GTEST_SOURCE_DIR)
        copy(self, "*.h", join(gtest_source_dir, "googletest", "include"), dst="include")
        copy(self, "*.h", join(gtest_source_dir, "googlemock", "include"), dst="include")
        copy(self, "*.dll", self.build_folder, join(self.package_folder, "bin"), keep_path=False)
        copy(self, "*.so.*", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", self.build_folder, join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["gtest", "gtest_main", "gmock", "gmock_main"]
