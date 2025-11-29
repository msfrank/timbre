#!/usr/bin/env python3

import os

from argparse import ArgumentParser
from os.path import join
from shutil import rmtree
from subprocess import run
from tempfile import mkdtemp, mkstemp

parser = ArgumentParser(prog="build_stage", description="build stage cache")
parser.add_argument('--conan-path', default='conan')
parser.add_argument('--conan-home', default=None)
parser.add_argument('--conan-profile', default=None)
parser.add_argument('--conan-build-profile', default=None)
parser.add_argument('--binary-dir', default=os.getcwd())
parser.add_argument('--cache-file', default=join(os.getcwd(), 'cache.tgz'))
parser.add_argument('--keep-tmp', action='store_true')
parser.add_argument('recipe_paths', nargs='*')
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
    run(full_args, env=env, check=True)

stage_dir = mkdtemp(prefix="build_stage.", dir=args.binary_dir)

# create each package and write the build graph
graph_paths = []
for recipe_path in args.recipe_paths:
    (_, graph_path) = mkstemp(suffix=".graph", dir=stage_dir)
    run_conan('create', recipe_path, '--build=missing', '--no-remote', '--format=json', f"--out-file={graph_path}")
    graph_paths.append(graph_path)

# convert each graph into a pkglist
pkglist_paths = []
for graph_path in graph_paths:
    pkglist_path = graph_path + '.pkglist'
    run_conan('list', f"--graph={graph_path}", '--format=json', f"--out-file={pkglist_path}")
    pkglist_paths.append(pkglist_path)

# merge individual pkglists into a single mergelist
mergelist_path = join(stage_dir, "mergelist")
pkglist_params = [ f"--list={pkglist}" for pkglist in pkglist_paths]
run_conan('pkglist', 'merge', '--format=json', f"--out-file={mergelist_path}", *pkglist_params)

# save package cache
run_conan('cache', 'save', '--no-source', f"--list={mergelist_path}", f"--file={args.cache_file}")

# if we are not keeping the stage dir then delete it
if not args.keep_tmp:
    rmtree(stage_dir)
