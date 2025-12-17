from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

ARROW_URL = "https://github.com/apache/arrow/archive/refs/tags/apache-arrow-22.0.0.tar.gz"
ARROW_DOWNLOAD_NAME = "arrow-apache-arrow-22.0.0.tar.gz"
ARROW_SOURCE_DIR = "arrow-apache-arrow-22.0.0"

class ApacheArrow(ConanFile):
    name = "apachearrow"
    version = "22.0.0"
    user = "timbre"
    url = "https://arrow.apache.org"
    description = """
Apache Arrow is a software development platform for building high performance applications that
process and transport large data sets.
"""

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires("absl/20250127.1@timbre")
        self.requires("boost/1.88.0@timbre")
        self.requires("cares/1.23.0@timbre")
        self.requires("gflags/20251106.1@timbre")
        self.requires("grpc/1.74.1@timbre")
        self.requires("openssl/3.5.2@timbre")
        self.requires("protobuf/32.0@timbre")
        self.requires("rapidjson/20250205.1@timbre")
        self.requires("re2/20210901.1@timbre")

    def source(self):
        get(self, ARROW_URL, filename=ARROW_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=ARROW_SOURCE_DIR, build_folder='apachearrow')

    def generate(self):
        tc = CMakeToolchain(self)

        tc.extra_cxxflags.append('-Wno-deprecated-declarations')

        tc.variables['CMAKE_CXX_STANDARD'] = '17'                   # force c++ 17
        tc.variables['CMAKE_INSTALL_LIBDIR'] = 'lib'                # force libdir to be 'lib' even on 64bit
        tc.variables['CMAKE_POSITION_INDEPENDENT_CODE'] = 'ON'      # force PIC
        tc.variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = 'ON'

        tc.cache_variables['CMAKE_INSTALL_RPATH_USE_LINK_PATH'] = 'ON'  # force append link paths to rpath
        #tc.cache_variables['ARROW_INSTALL_NAME_RPATH'] = 'ON'
        #tc.cache_variables['ARROW_RPATH_ORIGIN'] = 'ON'

        # find dependencies
        tc.cache_variables['absl_ROOT'] = self.dependencies["absl"].package_folder
        tc.cache_variables['c-ares_ROOT'] = self.dependencies["cares"].package_folder
        tc.cache_variables['gRPCAlt_ROOT'] = self.dependencies["grpc"].package_folder
        tc.cache_variables['OPENSSL_ROOT_DIR'] = self.dependencies["openssl"].package_folder
        tc.cache_variables['Protobuf_ROOT'] = self.dependencies["protobuf"].package_folder
        tc.cache_variables['RapidJSON_ROOT'] = self.dependencies["rapidjson"].package_folder

        # component selection
        tc.cache_variables["ARROW_BUILD_UTILITIES"] = 'ON'
        tc.cache_variables["ARROW_BUILD_SHARED"] = 'ON'
        tc.cache_variables["ARROW_BUILD_STATIC"] = 'OFF'
        tc.cache_variables["ARROW_BUILD_TESTS"] = 'OFF'
        tc.cache_variables["ARROW_COMPUTE"] = 'ON'
        tc.cache_variables["ARROW_DATASET"] = 'ON'
        tc.cache_variables["ARROW_FILESYSTEM"] = 'ON'
        tc.cache_variables["ARROW_FLIGHT"] = 'ON'
        tc.cache_variables["ARROW_IPC"] = 'OFF'
        tc.cache_variables["ARROW_JEMALLOC"] = 'OFF'
        tc.cache_variables["ARROW_CSV"] = 'ON'
        tc.cache_variables["ARROW_JSON"] = 'ON'

        # other options
        tc.cache_variables["ARROW_DEPENDENCY_SOURCE"] = 'SYSTEM'
        tc.cache_variables["ARROW_BOOST_USE_SHARED"] = 'ON'
        tc.cache_variables["ARROW_PROTOBUF_USE_SHARED"] = 'ON'
        tc.cache_variables["ARROW_WITH_ZLIB"] = 'OFF'
        tc.cache_variables["ARROW_WITH_UTF8PROC"] = 'OFF'
        tc.cache_variables["ARROW_SIMD_LEVEL"] = 'NONE'
        tc.cache_variables["ARROW_RUNTIME_SIMD_LEVEL"] = 'NONE'

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("openssl", "cmake_find_mode", "none") # disable openssl generator, force usage of FindOpenSSL.cmake
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="cpp")
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)
        copy(self, "LICENSE.txt", self.source_folder, join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "Arrow"))
        self.cpp_info.builddirs.append(join("lib", "cmake", "ArrowDataset"))
        self.cpp_info.builddirs.append(join("lib", "cmake", "ArrowFlight"))
