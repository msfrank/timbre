from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get, unzip


LIBUV_URL = "https://github.com/libuv/libuv/archive/v1.51.0.tar.gz"
LIBUV_DOWNLOAD_NAME = "libuv-1.51.0.tar.gz"
LIBUV_SOURCE_DIR = "libuv-1.51.0"

class Uv(ConanFile):
    name = "uv"
    version = "1.51.0"
    user = "timbre"
    url = "https://libuv.org"
    description = """
libuv is a multi-platform support library with a focus on asynchronous I/O.
"""

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, LIBUV_URL, filename=LIBUV_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=LIBUV_SOURCE_DIR)

    def generate(self):
        ms = VirtualRunEnv(self)
        ms.generate()
        env = Environment()
        envvars = env.vars(self)
        envvars.save_script("uv_env")

        tc = AutotoolsToolchain(self)
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autogen_script = join(self.source_folder, "autogen.sh")
        self.run(autogen_script, cwd=self.build_folder, env=['uv_env'])

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()
        autotools.install()

    def package(self):
        copy(self, "*.so", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.h", self.build_folder, join(self.package_folder, "include"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["uv"]
