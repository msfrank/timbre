from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get, unzip

JEMALLOC_URL = "https://github.com/jemalloc/jemalloc/releases/download/5.3.0/jemalloc-5.3.0.tar.bz2"
JEMALLOC_DOWNLOAD_NAME = "jemalloc-5.3.0.tar.bz2"
JEMALLOC_SOURCE_DIR = "jemalloc-5.3.0"

class Jemalloc(ConanFile):
    name = "jemalloc"
    version = "5.3.0"
    user = "timbre"
    url = "https://jemalloc.net"
    description = """
jemalloc is a general purpose malloc(3) implementation that emphasizes fragmentation avoidance
and scalable concurrency support.
"""

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, JEMALLOC_URL, filename=JEMALLOC_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=JEMALLOC_SOURCE_DIR)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append('--with-jemalloc-prefix=je_')
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()
        autotools.install(args=["-j1"])

    def package(self):
        copy(self, "*.so", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.h", join(self.build_folder, "include"), join(self.package_folder, "include"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["jemalloc"]
