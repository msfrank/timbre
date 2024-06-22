from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

PROTOBUF_URL = "https://github.com/protocolbuffers/protobuf/releases/download/v25.3/protobuf-25.3.tar.gz"
PROTOBUF_DOWNLOAD_NAME = "protobuf-25.3.tar.gz"
PROTOBUF_SOURCE_DIR = "protobuf-25.3"

class Protobuf(ConanFile):
    name = "protobuf"
    version = "25.3"
    user = "timbre"
    url = "https://protobuf.dev"
    description = """
Protocol Buffers are language-neutral, platform-neutral extensible mechanisms for serializing
structured data.
"""

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "build_type": ["Release","Debug"], "compiler.cppstd": ["17"]}
    default_options = {"shared": True, "build_type": "Release", "compiler.cppstd": "17"}
    #keep_imports = True

    def requirements(self):
        self.requires("absl/20230802.1@timbre")

    def source(self):
        get(self, PROTOBUF_URL, filename=PROTOBUF_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=PROTOBUF_SOURCE_DIR, build_folder='protobuf')

    def generate(self):
        tc = CMakeToolchain(self)

        #tc.variables['CMAKE_BUILD_TYPE'] = 'Release'             # force release build
        tc.variables['CMAKE_CXX_STANDARD'] = '17'                # force c++ 17
        tc.variables['CMAKE_INSTALL_LIBDIR'] = 'lib'             # force libdir to be 'lib' even on 64bit
        tc.variables['CMAKE_POSITION_INDEPENDENT_CODE'] = 'ON'   # force PIC
        tc.variables['BUILD_SHARED_LIBS'] = 'ON'                 # force shared library build
        tc.variables['CMAKE_INSTALL_RPATH_USE_LINK_PATH'] = 'ON' # force append link paths to rpath

        tc.variables['absl_DIR'] = self.dependencies['absl'].package_folder

        tc.cache_variables['protobuf_BUILD_EXAMPLES'] = 'OFF'    # don't build examples
        tc.cache_variables['protobuf_BUILD_TESTS'] = 'OFF'       # don't build tests
        tc.cache_variables['protobuf_ABSL_PROVIDER'] = 'package' # use absl from package
        tc.cache_variables['protobuf_DEBUG_POSTFIX'] = ''

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
        copy(self, 'LICENSE', self.source_folder, join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "protobuf"))
        self.buildenv_info.define('PROTOBUF_PROTOC', join(self.package_folder, "bin", "protoc"))
