from os.path import join

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, unzip

GRPC_URL = "https://github.com/grpc/grpc/archive/refs/tags/v1.74.1.tar.gz"
GRPC_DOWNLOAD_NAME = "grpc-1.74.1.tar.gz"
GRPC_SOURCE_DIR = "grpc-1.74.1"

class Grpc(ConanFile):
    name = "grpc"
    version = "1.74.1"
    user = "timbre"
    url = "https://grpc.io"
    description = """
gRPC is a modern open source high performance Remote Procedure Call (RPC) framework that can run
in any environment.
"""

    settings = "os", "build_type", "compiler", "arch"
    options = {"shared": [True, False], "build_type": ["Release","Debug"], "compiler.cppstd": ["17"]}
    default_options = {"shared": True, "build_type": "Release", "compiler.cppstd": "17"}

    def requirements(self):
        self.requires("absl/20250127.1@timbre")
        self.requires("benchmark/1.6.1@timbre")
        self.requires("cares/1.23.0@timbre")
        self.requires("openssl/3.5.2@timbre")
        self.requires("protobuf/32.0@timbre")
        self.requires("re2/20210901.1@timbre")

    def source(self):
        get(self, GRPC_URL, filename=GRPC_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=GRPC_SOURCE_DIR, build_folder='grpc')

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables['CMAKE_BUILD_TYPE'] = 'Release'             # force release build
        tc.variables['CMAKE_CXX_STANDARD'] = '17'                # force c++ 17
        tc.variables['CMAKE_INSTALL_LIBDIR'] = 'lib'             # force libdir to be 'lib' even on 64bit
        tc.variables['CMAKE_POSITION_INDEPENDENT_CODE'] = 'ON'   # force PIC
        tc.variables['BUILD_SHARED_LIBS'] = 'ON'                 # force shared library build
        tc.variables['CMAKE_INSTALL_RPATH_USE_LINK_PATH'] = 'ON' # force append link paths to rpath
        rpath = "@loader_path" if is_apple_os(self) else "\$ORIGIN"
        tc.variables['CMAKE_INSTALL_RPATH'] = rpath + '/../lib'

        # set cmake definitions to allow grpc to find dependencies
        tc.variables['absl_DIR'] = self.dependencies['absl'].package_folder
        tc.variables['c-ares_DIR'] = self.dependencies['cares'].package_folder
        tc.variables['re2_DIR'] = self.dependencies['re2'].package_folder
        tc.variables['Protobuf_DIR'] = self.dependencies['protobuf'].package_folder
        tc.variables['OpenSSL_DIR'] = self.dependencies['openssl'].package_folder
        tc.variables['OPENSSL_ROOT_DIR'] = self.dependencies['openssl'].package_folder

        # don't build tests
        tc.cache_variables['gRPC_BUILD_TESTS'] = 'OFF'

        # build gRPC with static dependencies
        tc.cache_variables['gRPC_ABSL_PROVIDER'] = 'package'
        tc.cache_variables['gRPC_BENCHMARK_PROVIDER'] = 'package'
        tc.cache_variables['gRPC_CARES_PROVIDER'] = 'package'
        tc.cache_variables['gRPC_GFLAGS_PROVIDER'] = 'package'
        tc.cache_variables['gRPC_PROTOBUF_PROVIDER'] = 'package'
        tc.cache_variables['gRPC_RE2_PROVIDER'] = 'package'
        tc.cache_variables['gRPC_SSL_PROVIDER'] = 'package'
        tc.cache_variables['gRPC_ZLIB_PROVIDER'] = 'package'
        tc.cache_variables['gRPC_PROTOBUF_PACKAGE_TYPE'] = 'CONFIG'

        # disable building most plugins
        tc.cache_variables['gRPC_BUILD_GRPC_CSHARP_PLUGIN'] = 'OFF'
        tc.cache_variables['gRPC_BUILD_GRPC_NODE_PLUGIN'] = 'OFF'
        tc.cache_variables['gRPC_BUILD_GRPC_OBJECTIVE_C_PLUGIN'] = 'OFF'
        tc.cache_variables['gRPC_BUILD_GRPC_PHP_PLUGIN'] = 'OFF'
        tc.cache_variables['gRPC_BUILD_GRPC_PYTHON_PLUGIN'] = 'OFF'
        tc.cache_variables['gRPC_BUILD_GRPC_RUBY_PLUGIN'] = 'OFF'

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        # copy generated protobuf headers to include/gens/ package directory
        copy(self, "*", join(self.build_folder, "gens"), join(self.package_folder, "include", "gens"))
        # copy license file to share/ package directory
        copy(self, "LICENSE", self.source_folder, join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "grpc"))
        self.buildenv_info.define('GRPC_CPP_PLUGIN', join(self.package_folder, "bin", "grpc_cpp_plugin"))
