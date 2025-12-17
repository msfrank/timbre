from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get, unzip

ICU_URL = "https://github.com/unicode-org/icu/releases/download/release-77-1/icu4c-77_1-src.tgz"
ICU_DOWNLOAD_NAME = "icu4c-77.1.tar.gz"
ICU_SOURCE_DIR = "icu4c-77.1"

class Icu(ConanFile):
    name = "icu"
    version = "77.1"
    user = "timbre"
    url = "https://icu.unicode.org"
    description = """
ICU is a mature, widely used set of C/C++ and Java libraries providing Unicode and Globalization
support for software applications. ICU is widely portable and gives applications the same results
on all platforms and between C/C++ and Java software.
"""

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, ICU_URL, filename=ICU_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=ICU_SOURCE_DIR)

    def generate(self):
        tc = AutotoolsToolchain(self)
        #tc.configure_args.append('--enable-rpath')
        rpath = "@loader_path" if is_apple_os(self) else "\$ORIGIN"
        tc.extra_ldflags = ["-Wl,-rpath," + rpath + ",-headerpad_max_install_names"]
        #tc.extra_ldflags = ["-Wl,-rpath," + rpath]
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        configure_dir = join(self.source_folder, 'source')
        autotools = Autotools(self)
        autotools.configure(build_script_folder=configure_dir)
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        fix_apple_shared_install_name(self)
        copy(self, "LICENSE", self.source_folder, join(self.package_folder, "share"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = [ "icudata", "icui18n", "icuio", "icutu", "icuuc" ]
