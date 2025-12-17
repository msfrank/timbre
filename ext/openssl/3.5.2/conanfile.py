from os.path import join
from platform import machine, system

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import build_jobs
from conan.tools.files import copy, get, unzip
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.layout import basic_layout

OPENSSL_URL = "https://github.com/openssl/openssl/releases/download/openssl-3.5.2/openssl-3.5.2.tar.gz"
OPENSSL_DOWNLOAD_NAME = "openssl-3.5.2.tar.gz"
OPENSSL_SOURCE_DIR = "openssl-3.5.2"

class Openssl(ConanFile):
    name = "openssl"
    version = "3.5.2"
    user = "timbre"
    url = "https://www.openssl.org"
    description = """
OpenSSL is a software library for applications that provide secure communications over
computer networks against eavesdropping, and identify the party at the other end. It
is widely used by Internet servers, including the majority of HTTPS websites. 
    """

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "build_type", "compiler", "arch"

    def source(self):
        get(self, OPENSSL_URL, filename=OPENSSL_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=OPENSSL_SOURCE_DIR)

    def generate(self):
        ms = VirtualRunEnv(self)
        ms.generate()
        env = Environment()
        rpath = "@loader_path" if is_apple_os(self) else "\$ORIGIN/"
        env.define("LDFLAGS", "-Wl,-rpath," + rpath)
        envvars = env.vars(self)
        envvars.save_script("openssl_env")

    def build(self):
        configure_script = join(self.source_folder, 'Configure')
        install_prefix = join(self.build_folder, 'install')
        system_name = system()
        machine_type = machine()
        if system_name == 'Darwin':
            configure_cmd = "%s --debug --prefix=%s --libdir=lib darwin64-%s-cc threads shared zlib-dynamic no-tests no-docs" % (
                configure_script, install_prefix, machine_type)
        elif system_name == 'Linux':
            configure_cmd = "%s --debug --prefix=%s --libdir=lib threads shared zlib-dynamic no-tests no-docs" % (
                configure_script, install_prefix)
        else:
            raise Exception("don't know how to build for platform: %s" % system_name)

        #self.run(configure_cmd, cwd=build_dir)
        self.run(configure_cmd, cwd=self.build_folder, env=['openssl_env'])
        self.run("make -j%d" % build_jobs(self), cwd=self.build_folder, env=['openssl_env'])
        self.run("make install", cwd=self.build_folder, env=['openssl_env'])

    def package(self):
        install_prefix = join(self.build_folder, 'install')
        copy(self, "*", join(install_prefix, 'bin'), join(self.package_folder,"bin"))
        copy(self, "*", join(install_prefix, 'lib'), join(self.package_folder,"lib"))
        copy(self, "*", join(install_prefix, 'lib64'), join(self.package_folder,"lib64"))
        copy(self, "*", join(install_prefix, 'include'), join(self.package_folder,"include"))
        copy(self, "*", join(install_prefix, 'ssl'), join(self.package_folder,"share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "OpenSSL"))
        self.buildenv_info.define('OPENSSL_OPENSSL', join(self.package_folder, "bin", "openssl"))
        self.buildenv_info.define('OPENSSL_OPENSSL_CNF', join(self.package_folder, "share", "openssl.cnf"))
        self.buildenv_info.define('OPENSSL_C_REHASH', join(self.package_folder, "bin", "c_rehash"))

