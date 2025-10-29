from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, unzip

RATS_URL = "https://github.com/DEgITx/librats/archive/refs/tags/0.3.1.tar.gz"
RATS_DOWNLOAD_NAME = "librats-0.3.1.tar.gz"
RATS_SOURCE_DIR = "librats-0.3.1"

class Rats(ConanFile):
    name = "rats"
    version = "0.3.1"
    user = "timbre"
    url = "https://librats.com/"
    description = """
Enterprise-grade peer-to-peer networking library with advanced NAT traversal, end-to-end
encryption, and publish-subscribe messaging.
    """

    settings = "os", "build_type", "compiler", "arch"

    def source(self):
        get(self, RATS_URL, filename=RATS_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=RATS_SOURCE_DIR, build_folder='rats')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables['RATS_SHARED_LIBRARY'] = 'ON'
        tc.cache_variables['RATS_STATIC_LIBRARY'] = 'OFF'
        tc.cache_variables['RATS_BINDINGS'] = 'OFF'
        tc.cache_variables['RATS_BUILD_TESTS'] = 'OFF'
        tc.cache_variables['RATS_BUILD_EXAMPLES'] = 'OFF'
        tc.cache_variables['CMAKE_MACOSX_RPATH'] = 'ON'
        tc.cache_variables['CMAKE_INSTALL_RPATH_USE_LINK_PATH'] = 'ON'
        tc.cache_variables["CMAKE_INSTALL_RPATH"] = "@loader_path" if is_apple_os(self) else "\$ORIGIN/"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # copy libraries to lib/ package directory
        copy(self, "*.so", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        # copy header files to include/ package directory
        copy(self, "*.h", join(self.source_folder, "src"), join(self.package_folder, "include"))
        copy(self, "*.h", join(self.build_folder, "src"), join(self.package_folder, "include"))
        fix_apple_shared_install_name(self)
        # copy license file to share/ package directory
        copy(self, 'LICENSE', self.source_folder, join(self.package_folder,'share'))

    def package_info(self):
        self.cpp_info.libs = ['rats']
