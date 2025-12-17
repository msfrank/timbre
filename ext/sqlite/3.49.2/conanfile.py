from os.path import join
from platform import machine, system

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import build_jobs
from conan.tools.files import copy, get, unzip
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.layout import basic_layout


SQLITE_URL = "https://sqlite.org/2025/sqlite-autoconf-3490200.tar.gz"
SQLITE_DOWNLOAD_NAME = "sqlite-autoconf-3490200.tar.gz"
SQLITE_SOURCE_DIR = "sqlite-autoconf-3490200"

class Sqlite(ConanFile):
    name = "sqlite"
    version = "3.49.2"
    user = "timbre"
    url = "https://sqlite.org"
    description = """
SQLite is a C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.
"""

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, SQLITE_URL, filename=SQLITE_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=SQLITE_SOURCE_DIR)

    def generate(self):
        ms = VirtualRunEnv(self)
        ms.generate()
        env = Environment()
        rpath = "@loader_path" if is_apple_os(self) else "\$ORIGIN/"
        env.define("LDFLAGS", "-Wl,-rpath," + rpath)
        envvars = env.vars(self)
        envvars.save_script("sqlite_env")

    def build(self):
        configure_script = join(self.source_folder, 'configure')
        install_prefix = join(self.build_folder, 'install')
        configure_cmd = "%s --debug --prefix=%s" % (configure_script, install_prefix)

        #self.run(configure_cmd, cwd=build_dir)
        self.run(configure_cmd, cwd=self.build_folder, env=['sqlite_env'])
        self.run("make -j%d" % build_jobs(self), cwd=self.build_folder, env=['sqlite_env'])
        self.run("make install", cwd=self.build_folder, env=['sqlite_env'])

    def package(self):
        copy(self, "*", join(self.build_folder, "install"), self.package_folder, keep_path=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["sqlite3"]
