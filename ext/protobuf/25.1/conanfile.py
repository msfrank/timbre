from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

PROTOBUF_URL = "https://github.com/protocolbuffers/protobuf/releases/download/v25.1/protobuf-25.1.tar.gz"
PROTOBUF_DOWNLOAD_NAME = "protobuf-25.1.tar.gz"
PROTOBUF_SOURCE_DIR = "protobuf-25.1"

class Protobuf(ConanFile):
    name = "protobuf"
    version = "25.1"
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

        tc.variables['CMAKE_BUILD_TYPE'] = 'Release'             # force release build
        tc.variables['CMAKE_CXX_STANDARD'] = '17'                # force c++ 17
        tc.variables['CMAKE_INSTALL_LIBDIR'] = 'lib'             # force libdir to be 'lib' even on 64bit
        tc.variables['CMAKE_POSITION_INDEPENDENT_CODE'] = 'ON'   # force PIC
        tc.variables['BUILD_SHARED_LIBS'] = 'ON'                 # force shared library build
        tc.variables['CMAKE_INSTALL_RPATH_USE_LINK_PATH'] = 'ON' # force append link paths to rpath

        tc.variables['absl_DIR'] = self.dependencies['absl'].package_folder

        # set rpath to discover imported libraries
        #if tools.os_info.is_macos:
        #    cmake.definitions['MACOS_RPATH'] = 'TRUE'
        #    cmake.definitions['CMAKE_INSTALL_RPATH'] = '@executable_path/../imports'
        #elif tools.os_info.is_linux:
        #    cmake.definitions['CMAKE_INSTALL_RPATH'] = '\$ORIGIN/../imports'

        tc.cache_variables['protobuf_BUILD_EXAMPLES'] = 'OFF'    # don't build examples
        tc.cache_variables['protobuf_BUILD_TESTS'] = 'OFF'       # don't build tests
        tc.cache_variables['protobuf_ABSL_PROVIDER'] = 'package' # use absl from package

        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        # copy protoc program into package directory
        #self.copy('protoc', dst='bin', keep_path=False)
        # copy protobuf headers and libraries into package directory
        #self.copy('*.h', src='protobuf', dst='include')
        #self.copy('*.dll', src='protobuf', dst='bin', keep_path=False)
        #self.copy('*.so*', src='protobuf', dst='lib', keep_path=False)
        #self.copy('*.dylib*', src='protobuf', dst='lib', keep_path=False)
        #self.copy('*.a', src='protobuf', dst='lib', keep_path=False)

        # copy license file to share/ package directory
        copy(self, 'LICENSE', self.source_folder, join(self.package_folder, 'share'))

        # copy imported libraries into lib/ package directory
        #self.copy('*', src='imports', dst='lib', keep_path=False)

        #self.copy('*proto*.lib', dst='lib', keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "protobuf"))
