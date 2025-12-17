from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, download, get, unzip

ANTLR_COMPLETE_JAR_URL = "https://repo1.maven.org/maven2/org/antlr/antlr4/4.13.2/antlr4-4.13.2-complete.jar"
ANTLR_COMPLETE_JAR_DOWNLOAD_NAME = "antlr-4.13.2-complete.jar"
ANTLR_RUNTIME_URL = "https://github.com/antlr/antlr4/archive/4.13.2.tar.gz"
ANTLR_RUNTIME_DOWNLOAD_NAME = "antlr4-4.13.2.tar.gz"
ANTLR_RUNTIME_SOURCE_DIR = "antlr4-4.13.2"

class Antlr(ConanFile):
    name = "antlr"
    version = "4.13.2"
    user = "timbre"
    url = "https://www.antlr.org"
    description = """
ANTLR (ANother Tool for Language Recognition) is a powerful parser generator for reading, processing,
executing, or translating structured text or binary files. It's widely used to build languages,
tools, and frameworks. From a grammar, ANTLR generates a parser that can build and walk parse trees.
    """

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "build_type", "compiler", "arch"

    def source(self):
        download(self, ANTLR_COMPLETE_JAR_URL, ANTLR_COMPLETE_JAR_DOWNLOAD_NAME)
        get(self, ANTLR_RUNTIME_URL, filename=ANTLR_RUNTIME_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder=ANTLR_RUNTIME_SOURCE_DIR, build_folder='antlr')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['CMAKE_MACOSX_RPATH'] = 'ON'
        tc.cache_variables['WITH_DEMO'] = 'OFF'
        tc.cache_variables['ANTLR_BUILD_CPP_TESTS'] = 'OFF'
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=join("runtime", "Cpp"))
        cmake.build()
        cmake.install()

    def package(self):
        copy(self, '*.h', self.build_folder, join(self.package_folder,'include'))
        copy(self, '*.dll', self.build_folder, join(self.package_folder,'bin'), keep_path=False)
        copy(self, '*.so', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, '*.dylib', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, '*.a', self.build_folder, join(self.package_folder,'lib'), keep_path=False)
        copy(self, 'LICENSE.txt', self.source_folder, join(self.package_folder,'share'))
        copy(self, ANTLR_COMPLETE_JAR_DOWNLOAD_NAME, self.source_folder, join(self.package_folder,'lib','java'))

    def package_info(self):
        self.cpp_info.libs = ["antlr4-runtime"]
        self.cpp_info.includedirs = ["include/antlr4-runtime"]
        self.buildenv_info.define('ANTLR_TOOL_JAR', join(self.package_folder, "lib", "java", ANTLR_COMPLETE_JAR_DOWNLOAD_NAME))
