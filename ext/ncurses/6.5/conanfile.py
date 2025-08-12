from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get, unzip

NCURSES_URL = "https://invisible-island.net/archives/ncurses/ncurses-6.5.tar.gz"
NCURSES_DOWNLOAD_NAME = "ncurses-6.5.tar.bz2"
NCURSES_SOURCE_DIR = "ncurses-6.5"

class Ncurses(ConanFile):
    name = "ncurses"
    version = "6.5"
    user = "timbre"
    url = "https://invisible-island.net/ncurses/ncurses.html"
    description = """
ncurses is a library of functions that manage an application's display on character-cell terminals (e.g., VT100).
"""

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, NCURSES_URL, filename=NCURSES_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=NCURSES_SOURCE_DIR)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append('--with-shared')
        tc.configure_args.append('--without-ada')
        tc.configure_args.append('--without-tests')
        tc.configure_args.append('--enable-ext-colors')
        tc.configure_args.append('--enable-rpath')

        # disabling because it appears to change the library name
        #tc.configure_args.append('--with-pthread')
        #tc.configure_args.append('--enable-reentrant')

        rpath = "@loader_path" if is_apple_os(self) else "\$ORIGIN"
        tc.extra_ldflags = ["-Wl,-rpath," + rpath + ",-headerpad_max_install_names"]

        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        fix_apple_shared_install_name(self)
        #copy(self, "*.so", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        #copy(self, "*.dylib", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        #copy(self, "*.a", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
        #copy(self, "*.h", join(self.build_folder, "include"), join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.libs = ["ncursesw"]
