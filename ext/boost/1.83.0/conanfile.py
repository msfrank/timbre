from os.path import join
from platform import system

from conan import ConanFile
from conan.tools.build import build_jobs
from conan.tools.files import copy, get, unzip
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.layout import basic_layout

BOOST_URL = "https://boostorg.jfrog.io/artifactory/main/release/1.83.0/source/boost_1_83_0.tar.bz2"
BOOST_DOWNLOAD_NAME = "boost-1.83.0.tar.bz2"
BOOST_SOURCE_DIR = "boost_1_83_0"

class Boost(ConanFile):
    name = "boost"
    version = "1.83.0"
    user = "timbre"
    url = "https://www.boost.org"
    description = """
Boost provides free peer-reviewed portable C++ source libraries.
"""

    settings = "os", "build_type", "compiler", "arch"
    options = {"shared": [True, False], "with_icu": [True,False]}
    default_options = {"shared": True, "with_icu": True}

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

        configure_cmd = "%s --prefix=%s --with-libraries=all" % (
            bootstrap_script, self.build_folder)
        if self.options.with_icu:
            configure_cmd += " --with-icu"
        self.run(configure_cmd, cwd=self.source_folder, env=["boost_env"])

        build_cmd = "%s --prefix=%s" % (
            b2_script, self.build_folder)
        self.run(build_cmd, cwd=self.source_folder, env=["boost_env"])

        install_cmd = "%s --prefix=%s install" % (
            b2_script, self.build_folder)
        self.run(install_cmd, cwd=self.source_folder, env=["boost_env"])

    def package(self):
        copy(self, "*.h", join(self.build_folder, 'include'), join(self.package_folder, "include"))
        copy(self, "*.hpp", join(self.build_folder, 'include'), join(self.package_folder, "include"))
        copy(self, "*.inc", join(self.build_folder, 'include'), join(self.package_folder, "include"))
        copy(self, "*.ipp", join(self.build_folder, 'include'), join(self.package_folder, "include"))
        copy(self, "*.dll", self.build_folder, join(self.package_folder, "bin"), keep_path=False)
        copy(self, "*.so", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*", join(self.build_folder,'lib','cmake'), join(self.package_folder, 'lib','cmake'))

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.components['headers'].libs = []
        self.cpp_info.components['headers'].includedirs = ['include']
