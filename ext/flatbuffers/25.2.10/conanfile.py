from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

FLATBUFFERS_URL = "https://github.com/google/flatbuffers/archive/refs/tags/v25.2.10.tar.gz"
FLATBUFFERS_DOWNLOAD_NAME = "flatbuffers-25.2.10.tar.gz"
FLATBUFFERS_SOURCE_DIR = "flatbuffers-25.2.10"

class Flatbuffers(ConanFile):
    name = "flatbuffers"
    version = "25.2.10"
    user = "timbre"
    url = "https://flatbuffers.dev"
    description = """
FlatBuffers is an efficient cross platform serialization library for C++, C#, C, Go, Java, Kotlin,
JavaScript, Lobster, Lua, TypeScript, PHP, Python, Rust and Swift. It was originally created at
Google for game development and other performance-critical applications.
"""

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, FLATBUFFERS_URL, filename=FLATBUFFERS_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=FLATBUFFERS_SOURCE_DIR, build_folder='flatbuffers')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["FLATBUFFERS_BUILD_SHAREDLIB"] = True
        tc.cache_variables["FLATBUFFERS_BUILD_FLATLIB"] = False
        tc.cache_variables["FLATBUFFERS_BUILD_TESTS"] = False
        tc.cache_variables['CMAKE_INSTALL_LIBDIR'] = 'lib'  # force libdir to be 'lib' even on 64bit
        tc.cache_variables['CMAKE_POSITION_INDEPENDENT_CODE'] = 'ON'
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        copy(self, "flatc", self.build_folder, join(self.package_folder, "bin"), keep_path=False)
        copy(self, "*.lib", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.h", self.build_folder, join(self.package_folder, "include"))
        copy(self, "LICENSE", self.source_folder, join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["flatbuffers"]
        self.buildenv_info.define('FLATBUFFERS_FLATC', join(self.package_folder, "bin", "flatc"))
