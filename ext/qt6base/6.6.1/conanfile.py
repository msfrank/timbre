from os.path import join

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.files import copy, get, unzip
from conan.tools.layout import basic_layout

QT6BASE_URL = "https://download.qt.io/archive/qt/6.6/6.6.1/submodules/qtbase-everywhere-src-6.6.1.tar.xz"
QT6BASE_DOWNLOAD_NAME = "qtbase-everywhere-src-6.6.1.tar.xz"
QT6BASE_SOURCE_DIR = "qtbase-everywhere-src-6.6.1"

class Qt6Base(ConanFile):
    name = 'qt6base'
    version = '6.6.1'
    user = 'timbre'
    url = ''
    description = """
Qt 6 lets you develop applications with intuitive user interfaces for multiple devices
and platforms, faster than ever before.
"""

    settings = "os", "build_type", "compiler", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    def requirements(self):
        self.requires("icu/74.1@timbre")
        self.requires("openssl/3.2.0@timbre")

    def source(self):
        get(self, QT6BASE_URL, filename=QT6BASE_DOWNLOAD_NAME, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=QT6BASE_SOURCE_DIR)

    def generate(self):
        ms = VirtualRunEnv(self)
        ms.generate()
        env = Environment()
        envvars = env.vars(self)
        envvars.save_script("qt6base_env")

        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        configure_script = join(self.source_folder, "configure")

        args = []
        args.append('-shared')                                      # enable shared libraries
        args.append('-no-framework')                                # don't build frameworks on MacOS
        args.append('-icu')                                         # build with icu from timbre
        args.append('-openssl-linked')                              # build with openssl from timbre
        args.append('-nomake examples')                             # don't build examples
        args.append('-nomake tests')                                # don't build examples
        args.append('-nomake benchmarks')                           # don't build benchmarks
        args.append('-nomake manual-tests')                         # don't build manual tests
        args.append('-nomake minimal-static-tests')                 # don't build minimal static tests

        options = {}
        options['-prefix'] = self.package_folder                    # set the installation prefix

        cachevars = {}
        cachevars['CMAKE_INSTALL_RPATH_USE_LINK_PATH'] = 'ON'                       # force append link paths to rpath
        cachevars['CMAKE_PREFIX_PATH'] = self.dependencies['icu'].package_folder    # append icu prefix path
        cachevars['OPENSSL_ROOT_DIR'] = self.dependencies['openssl'].package_folder # set openssl root dir

        # set the install rpath correctly depending on the host system
        if is_apple_os(self):
            cachevars['MACOSX_RPATH'] = 'ON'
            cachevars['CMAKE_INSTALL_RPATH'] = '@executable_path/../lib'
        else:
            cachevars['CMAKE_INSTALL_RPATH'] = '\$ORIGIN/../lib'

        args.extend(["%s %s" % (k,v) for k,v in options.items()])
        args.append('--')
        args.extend(["-D%s=%s" % (k,v) for k,v in cachevars.items()])

        configure_cmd = "%s %s" % (configure_script, " ".join(args))

        self.run(configure_cmd, cwd=self.build_folder, env=["qt6base_env"])

        cmake = CMake(self)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(join("lib", "cmake", "Qt6"))
