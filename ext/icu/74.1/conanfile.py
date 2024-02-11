from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get, unzip

ICU_URL = "https://github.com/unicode-org/icu/releases/download/release-74-1/icu4c-74_1-src.tgz"
ICU_DOWNLOAD_NAME = "icu4c-74.1.tar.gz"
ICU_SOURCE_DIR = "icu4c-74.1"

class Icu(ConanFile):
    name = "icu"
    version = "74.1"
    user = "timbre"
    url = "https://icu.unicode.org"
    description = """
ICU is a mature, widely used set of C/C++ and Java libraries providing Unicode and Globalization
support for software applications. ICU is widely portable and gives applications the same results
on all platforms and between C/C++ and Java software.
"""

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, ICU_URL, filename=ICU_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=ICU_SOURCE_DIR)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append('--enable-rpath')
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        configure_dir = join(self.source_folder, 'source')
        autotools = Autotools(self)
        autotools.configure(build_script_folder=configure_dir)
        autotools.make()
        autotools.install()

    def package(self):
        copy(self, "*", join(self.build_folder, 'include'), join(self.package_folder, 'include'))
        copy(self, "*", join(self.build_folder, 'lib'), join(self.package_folder, 'lib'))
        copy(self, "*", join(self.build_folder, 'bin'), join(self.package_folder, 'include'))
        copy(self, "*", join(self.build_folder, 'sbin'), join(self.package_folder, 'sbin'))
        copy(self, "LICENSE", self.source_folder, join(self.package_folder, "share"), keep_path=False)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = [ "icudata", "icui18n", "icuio", "icutu", "icuuc" ]
