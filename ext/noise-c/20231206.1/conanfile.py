from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.files import copy, get, unzip

NOISEC_URL = "https://github.com/rweather/noise-c/archive/cfe25410979a87391bb9ac8d4d4bef64e9f268c6.tar.gz"
NOISEC_DOWNLOAD_NAME = "noise-c-cfe25410979a87391bb9ac8d4d4bef64e9f268c6.tar.gz"
NOISEC_SOURCE_DIR = "noise-c-cfe25410979a87391bb9ac8d4d4bef64e9f268c6"

class NoiseC(ConanFile):
    name = "noise-c"
    version = "20231206.1"
    user = "timbre"
    url = ""
    description = """
Noise-C, a plain C implementation of the Noise protocol 
"""

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, NOISEC_URL, filename=NOISEC_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=NOISEC_SOURCE_DIR)

    def generate(self):
        ms = VirtualRunEnv(self)
        ms.generate()
        env = Environment()
        envvars = env.vars(self)
        envvars.save_script("autogen_env")

        tc = AutotoolsToolchain(self)
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autogen_script = join(self.source_folder, "autogen.sh")
        self.run(autogen_script, cwd=self.source_folder, env=['autogen_env'])

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = ["noiseprotocol", "noisekeys", "noiseprotobufs"]
