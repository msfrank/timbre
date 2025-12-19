#!/usr/bin/env python3

import os
import sys

from argparse import ArgumentParser
from json import loads, dumps
from subprocess import run

parser = ArgumentParser(
    prog="determine_changes",
    description="generate build order for the specified packages")
parser.add_argument('--conan-path', default='conan')
parser.add_argument('--conan-home', default=None)
parser.add_argument('--conan-profile', default=None)
parser.add_argument('--conan-build-profile', default=None)
parser.add_argument('--scan-cache', action='store_true')
parser.add_argument('--package-refs-path', default='package-refs.json')
parser.add_argument('--build-order-path', default='build-order.json')
parser.add_argument('--debug', action='store_true')
parser.add_argument('requires', nargs='*')
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

# construct the build order

graph_args = ['graph', 'build-order', '--build=missing', '-f', 'json']

requires_list = []

for requires in args.requires:
    requires_list.append(f"--requires={requires}")

if args.scan_cache:
    list_result = run_conan('list', '-c', '-f', 'json')
    list_json = loads(list_result.stdout)
    for requires,_ in list_json['Local Cache'].items():
        requires_list.append(f"--requires={requires}")

if len(requires_list) == 0:
    print(f"no requirements found, aborting")
    sys.exit(1)
graph_args.extend(requires_list)

graph_result = run_conan(*graph_args)
graph_json = loads(graph_result.stdout)

package_refs = []
build_order = []

for list in graph_json:
    for node in list:
        package = node['packages'][0][0]
        ref = node['ref']
        package_refs.append(ref)
        if package['binary'] == 'Build':
            build_order.append(ref)

with open(args.package_refs_path, 'w') as f:
    f.write(dumps(package_refs))

with open(args.build_order_path, 'w') as f:
    f.write(dumps(build_order))
