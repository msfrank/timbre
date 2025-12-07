from os.path import join
from platform import system

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import build_jobs
from conan.tools.files import copy, get, unzip
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.layout import basic_layout

BOOST_URL = "https://archives.boost.io/release/1.88.0/source/boost_1_88_0.tar.bz2"
BOOST_DOWNLOAD_NAME = "boost-1.88.0.tar.bz2"
BOOST_SOURCE_DIR = "boost_1_88_0"

class Boost(ConanFile):
    name = "boost"
    version = "1.88.0"
    user = "timbre"
    url = "https://www.boost.org"
    description = """
Boost provides free peer-reviewed portable C++ source libraries.
"""

    settings = "os", "build_type", "compiler", "arch"

    def source(self):
        get(self, BOOST_URL, filename=BOOST_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=BOOST_SOURCE_DIR)

    def generate(self):
        ms = VirtualRunEnv(self)
        ms.generate()
        env = Environment()
        envvars = env.vars(self)
        envvars.save_script("boost_env")
 
    def build(self):
        bootstrap_script = join(self.source_folder, "bootstrap.sh")
        b2_script = join(self.source_folder, "b2")

        configure_cmd = "%s --prefix=%s" % (bootstrap_script, self.build_folder)
        self.run(configure_cmd, cwd=self.source_folder, env=["boost_env"])

        rpath = "@loader_path" if is_apple_os(self) else "\$ORIGIN"
        linkflags = "-Wl,-rpath," + rpath + ",-headerpad_max_install_names"

        build_cmd = "%s --build-dir=%s linkflags=%s" % (
            b2_script, self.build_folder, linkflags)
        self.run(build_cmd, cwd=self.source_folder, env=["boost_env"])

    def package(self):
        b2_script = join(self.source_folder, "b2")

        install_cmd = "%s --prefix=%s install" % (
            b2_script, self.package_folder)
        self.run(install_cmd, cwd=self.source_folder, env=["boost_env"])

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "Boost-" + self.version))
