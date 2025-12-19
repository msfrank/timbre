#!/usr/bin/env python3

import os
import sys

from argparse import ArgumentParser
from json import load, loads
from subprocess import run

parser = ArgumentParser(
    prog="promote_packages",
    description="promote packages from source remote to target remote")
parser.add_argument('--conan-path', default='conan')
parser.add_argument('--conan-home', default=None)
parser.add_argument('--conan-profile', default=None)
parser.add_argument('--conan-build-profile', default=None)
parser.add_argument('-p', '--package-ref', action='append', default=[], dest='package_refs')
parser.add_argument('--package-refs-path', default=None)
parser.add_argument('--force-upload', action='store_true')
parser.add_argument('--clean', action='store_true')
parser.add_argument('--debug', action='store_true')
parser.add_argument('source_remote')
parser.add_argument('target_remote')
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

# build list of package refs to promote

package_refs_set = set(args.package_refs)

if args.package_refs_path:
    with open(args.package_refs_path, 'r') as f:
        package_refs_json = load(f)
        package_refs_set.update(package_refs_json)

# list revisions in the source remote

list_source_args = ['list', '-cc', 'core:non_interactive=True', f"--remote={args.source_remote}", '-f', 'json', '*/*#*']
list_source_result = run_conan(*list_source_args)
list_source_json = loads(list_source_result.stdout)

# check whether each package ref exists in the source remote

source_refs = set()
for package_id,node in list_source_json[args.source_remote].items():
    for revision_id,_ in node['revisions'].items():
        source_refs.add(f"{package_id}#{revision_id}")

missing_refs = []
for package_ref in package_refs_set:
    if not package_ref in source_refs:
        missing_refs.append(package_ref)

package_refs_set.difference_update(missing_refs)

# list revisions in the target remote

list_target_args = ['list', '-cc', 'core:non_interactive=True', f"--remote={args.target_remote}", '-f', 'json', '*/*#*']
list_target_result = run_conan(*list_target_args)
list_target_json = loads(list_target_result.stdout)

# check whether each package ref exists in the target remote

target_refs = set()
for package_id,node in list_target_json[args.target_remote].items():
    for revision_id,_ in node['revisions'].items():
        target_refs.add(f"{package_id}#{revision_id}")

promotion_refs = []
for package_ref in package_refs_set:
    if not package_ref in target_refs:
        promotion_refs.append(package_ref)

# copy promotion refs from source remote to target remote

for package_ref in promotion_refs:
    download_args = ['download', '-cc', 'core:non_interactive=True', f"--remote={args.source_remote}", '-f', 'json', package_ref]
    download_result = run_conan(*download_args)
    upload_args = ['upload', '-cc', 'core:non_interactive=True', f"--remote={args.target_remote}", '-f', 'json', package_ref]
    if args.force_upload:
        upload_args.append('--force')
    upload_result = run_conan(*upload_args)

    if args.clean:
        package_id,sep,rev = package_ref.partition('#')
        clean_ref = f"{package_id}#!latest"
        clean_args = ['remove', '-cc', 'core:non_interactive=True', f"--remote={args.target_remote}", '-c', '-f', 'json', clean_ref]
        clean_result = run_conan(*clean_args)
