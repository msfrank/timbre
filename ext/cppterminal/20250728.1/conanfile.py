from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

CPPTERMINAL_URL = "https://github.com/jupyter-xeus/cpp-terminal/archive/dfb5ddf47dca73ce3cb51e3b8a80f2485bb74dff.tar.gz"
CPPTERMINAL_DOWNLOAD_NAME = "cpp-terminal-20250728.tar.gz"
CPPTERMINAL_SOURCE_DIR = "cpp-terminal-dfb5ddf47dca73ce3cb51e3b8a80f2485bb74dff"

class Cppterminal(ConanFile):
    name = "cppterminal"
    version = "20250728.1"
    user = "timbre"
    url = "https://github.com/jupyter-xeus/cpp-terminal"
    description = """
CPP-Terminal is a small and dependency-free C++ library for writing platform independent
terminal-based applications.
"""

    settings = "os", "build_type", "compiler", "arch"

    def source(self):
        get(self, CPPTERMINAL_URL, filename=CPPTERMINAL_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=CPPTERMINAL_SOURCE_DIR, build_folder='cppterminal')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables['CPPTERMINAL_ENABLE_INSTALL'] = 'ON'
        tc.cache_variables['CPPTERMINAL_BUILD_EXAMPLES'] = 'OFF'
        tc.cache_variables['CPPTERMINAL_ENABLE_TESTING'] = 'OFF'
        tc.cache_variables['CPPTERMINAL_ENABLE_DOCS'] = 'OFF'
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
        copy(self, '*.so', self.build_folder, join(self.package_folder, 'lib'), keep_path=False)
        copy(self, '*.dylib', self.build_folder, join(self.package_folder, 'lib'), keep_path=False)
        copy(self, '*.a', self.build_folder, join(self.package_folder, 'lib'), keep_path=False)
        copy(self, '*', join(self.build_folder, 'lib','cmake'), join(self.package_folder, 'lib', 'cmake'))
        copy(self, 'LICENSE', self.source_folder, join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "cpp-terminal"))
