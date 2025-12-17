#!/usr/bin/env python3

import os
import sys

from argparse import ArgumentParser
from json import loads
from subprocess import run

parser = ArgumentParser(
    prog="install_and_upload_package",
    description="install package from cache and upload to conan remote")
parser.add_argument('--conan-path', default='conan')
parser.add_argument('--conan-home', default=None)
parser.add_argument('--conan-profile', default=None)
parser.add_argument('--conan-build-profile', default=None)
parser.add_argument('--build', action='append', default=[])
parser.add_argument('--force-upload', action='store_true')
parser.add_argument('--clean', action='store_true')
parser.add_argument('--debug', action='store_true')
parser.add_argument('package_ref')
parser.add_argument('remote')
args = parser.parse_args()

def run_conan(*cmd_args):
    full_args = [args.conan_path]
    full_args.extend(cmd_args)
    env = os.environ.copy()
    if args.conan_home:
        env['CONAN_HOME'] = args.conan_home
    if args.conan_profile:
        env['CONAN_DEFAULT_PROFILE'] = args.conan_profile
    if args.conan_build_profile:
        env['CONAN_DEFAULT_BUILD_PROFILE'] = args.conan_build_profile
    result = run(full_args, env=env, check=False, capture_output=True, text=True)
    if args.debug:
        print(f"---- STDERR ----")
        print(result.stderr)
        print(f"---- STDOUT ----")
        print(result.stdout)
        print(f"----------------")
    if result.returncode != 0:
        print(f"command '{' '.join(full_args)}' exited with status {result.returncode}")
        sys.exit(1)
    return result

# install package

install_args = ['install', '-f', 'json', f"--requires={args.package_ref}", f"--build={args.package_ref}"]

for build in args.build:
    install_args.append(f"--build={build}")

install_result = run_conan(*install_args)

# build list of package revisions to upload

create_json = loads(install_result.stdout)
graph_nodes = create_json['graph']['nodes']
upload_revisions = [node['ref'] for (_, node) in graph_nodes.items() if node['binary'] == 'Build']

# upload package

for revision in upload_revisions:
    upload_args = ['upload', '-cc', 'core:non_interactive=True', '-c', '-r', args.remote, revision]
    if args.force_upload:
        upload_args.append('--force')
    run_conan(*upload_args)

    if args.clean:
        package_id,sep,rev = revision.partition('#')
        clean_ref = f"{package_id}#!latest"
        clean_args = ['remove', '-cc', 'core:non_interactive=True', f"--remote={args.remote}", '-c', '-f', 'json', clean_ref]
        clean_result = run_conan(*clean_args)
