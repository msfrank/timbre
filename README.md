Timbre - Pinned Conan package recipes
=====================================

Copyright (c) 2024, Michael Frank

Overview
--------

This repository contains a set of Conan package recipes used by the Zuri project.
All recipes in this repository are explicitly exported using the 'timbre' package
user in order to disambiguate them from publicly available recipes in conan center.

Usage
-----

Building this project will export all of the recipes into the local conan2 package
cache. Downstream dependents will use conan to build and install the dependencies
as needed.

Prerequisites
-------------

Timbre requires the following dependencies to be installed on the system:
```
CMake version 3.27 or greater
Conan version 2
Java JDK version 11 or greater
```

Quick Start
-----------

1. Navigate to the repository root.
1. Generate the project buildsystem:
  ```
cmake -B build
  ```
1. Build the default target:
  ```
cmake --build build/
  ```
