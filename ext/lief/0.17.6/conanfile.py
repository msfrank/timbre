from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

LIEF_URL = "https://github.com/lief-project/LIEF/archive/refs/tags/0.17.6.tar.gz"
LIEF_DOWNLOAD_NAME = "LIEF-0.17.6.tar.gz"
LIEF_SOURCE_DIR = "LIEF-0.17.6"

class Lief(ConanFile):
    name = "lief"
    version = "0.17.6"
    user = "timbre"
    url = "https://lief.re/"
    description = """
The purpose of this project is to provide a cross-platform library to parse,
modify and abstract ELF, PE and MachO formats.
    """

    revision_mode = "scm_folder"
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, LIEF_URL, filename=LIEF_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=LIEF_SOURCE_DIR, build_folder='lief')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables['BUILD_SHARED_LIBS'] = 'ON'
        tc.cache_variables['LIEF_C_API'] = 'OFF'
        tc.cache_variables['LIEF_EXAMPLES'] = 'OFF'
        tc.cache_variables['LIEF_USE_CCACHE'] = 'OFF'
        tc.cache_variables['LIEF_LOGGING'] = 'OFF'
        tc.cache_variables['LIEF_LOGGING_DEBUG'] = 'OFF'
        tc.cache_variables['LIEF_ENABLE_JSON'] = 'OFF'
        tc.cache_variables['LIEF_SO_VERSION'] = 'ON'
        tc.cache_variables['LIEF_DISABLE_FROZEN'] = 'ON'
        tc.cache_variables['LIEF_DEX'] = 'OFF'
        tc.cache_variables['LIEF_ART'] = 'OFF'

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
        #fix_apple_shared_install_name(self)
        copy(self, 'LICENSE', self.source_folder, join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "LIEF"))
