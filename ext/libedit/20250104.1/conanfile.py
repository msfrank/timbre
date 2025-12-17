from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get, unzip

LIBEDIT_URL = "https://www.thrysoee.dk/editline/libedit-20250104-3.1.tar.gz"
LIBEDIT_DOWNLOAD_NAME = "libedit-20250104-3.1.tar.gz"
LIBEDIT_SOURCE_DIR = "libedit-20250104-3.1"

class Libedit(ConanFile):
    name = "libedit"
    version = "20250104.1"
    user = "timbre"
    url = "https://thrysoee.dk/editline/"
    description = """
This is an autotool- and libtoolized port of the NetBSD Editline library (libedit). This
Berkeley-style licensed command line editor library provides generic line editing, history,
and tokenization functions, similar to those found in GNU Readline.
"""

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, LIBEDIT_URL, filename=LIBEDIT_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=LIBEDIT_SOURCE_DIR)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()
        autotools.install()

    def package(self):
        copy(self, "*.so", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.h", join(self.build_folder, "include"), join(self.package_folder, "include"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["edit"]
