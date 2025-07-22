cmake_minimum_required(VERSION 3.27)

project(timbre)

#######################################################################
#
# declare options
#
#######################################################################

set(CONAN_PACKAGE_CHANNEL ""
    CACHE STRING
    "the packaging channel, defaults to ''")

set(CONAN_HOME ""
    CACHE STRING
    "the conan home location, defaults to ''")

#######################################################################
#
# configure toolchain
#
#######################################################################


#######################################################################
#
# find required and optional dependencies
#
#######################################################################

# ensure that pkg-config is available
find_package(PkgConfig REQUIRED)

# find required dependencies which may come from the platform
find_package(ZLIB REQUIRED)
find_package(BZip2 REQUIRED)
find_package(LibXml2 REQUIRED)

# find java installation
find_package(Java REQUIRED)

# find python installation
find_package (Python3 COMPONENTS Interpreter)

# find conan package manager
find_program(Conan conan REQUIRED)

# check the conan version
execute_process(COMMAND ${Conan} --version
    RESULT_VARIABLE CONAN_RESULT
    OUTPUT_VARIABLE CONAN_OUTPUT
    ERROR_VARIABLE CONAN_ERROR
    TIMEOUT 10
    )
if (${CONAN_RESULT} GREATER 0)
    message(FATAL_ERROR "Failed to invoke ${Conan}: {CONAN_ERROR}")
endif()

string(REGEX REPLACE "Conan version ([0-9]+\\.[0-9]+\\.[0-9]+)" "\\1"
    CONAN_FULL_VERSION
    "${CONAN_OUTPUT}")
if (NOT CONAN_FULL_VERSION)
    message(FATAL_ERROR "Failed to detect conan version. Output was: ${CONAN_OUTPUT}")
endif()

string(REGEX REPLACE "([0-9]+)\\.[0-9]+\\.[0-9]+" "\\1"
    CONAN_MAJOR_VERSION
    "${CONAN_FULL_VERSION}")
if (${CONAN_MAJOR_VERSION} EQUAL 2)
    message(STATUS "Found conan version ${CONAN_FULL_VERSION}")
else()
    message(FATAL_ERROR "Version 2 of conan is required but detected: ${CONAN_FULL_VERSION}")
endif()


#######################################################################
#
# configure tools and paths
#
#######################################################################

if (${CONAN_HOME})
    set(CONAN "${CMAKE_COMMAND} -E env CONAN_HOME=\"${CONAN_HOME}\" ${Conan}")
else()
    set(CONAN ${Conan})
endif ()

set(PYTHON3 ${Python3_EXECUTABLE})


#######################################################################
#
# define aggregate build targets
#
#######################################################################

add_custom_target(export-all-packages ALL)
add_custom_target(create-all-packages)


#######################################################################
#
# define build constants
#
#######################################################################

set(DECLARED_CREATE_TARGETS "" CACHE INTERNAL "declared create targets" FORCE)

function(declare_package_export PACKAGE_NAME PACKAGE_VERSION)

    # declare the export_<package-name>_<package-version> target
    set(EXPORT_TARGET_NAME "export_${PACKAGE_NAME}_${PACKAGE_VERSION}")
    if(${CONAN_PACKAGE_CHANNEL})
        add_custom_target (
            ${EXPORT_TARGET_NAME}
            COMMAND ${CONAN} export ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py --channel ${CONAN_PACKAGE_CHANNEL}
            COMMENT "exporting package ${PACKAGE_NAME}-${PACKAGE_VERSION} into channel '${CONAN_PACKAGE_CHANNEL}'"
            SOURCES ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py
        )
    else()
        add_custom_target (
            ${EXPORT_TARGET_NAME}
            COMMAND ${CONAN} export ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py
            COMMENT "exporting package ${PACKAGE_NAME}-${PACKAGE_VERSION}"
            SOURCES ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py
        )
    endif()

    # add export target as a dependency of the export-all-packages target
    add_dependencies(export-all-packages ${EXPORT_TARGET_NAME})

    # declare the create_<package-name>_<package-version> target
    set(CREATE_TARGET_NAME "create_${PACKAGE_NAME}_${PACKAGE_VERSION}")
    add_custom_target (
        ${CREATE_TARGET_NAME}
        COMMAND ${CONAN} create ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py --build=missing --no-remote
        COMMENT "creating package ${PACKAGE_NAME}-${PACKAGE_VERSION}"
        SOURCES ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py
    )

    # add create target as a dependency of the export-all-packages target
    add_dependencies(create-all-packages ${CREATE_TARGET_NAME})

    set(create_targets_list ${DECLARED_CREATE_TARGETS})
    list(APPEND create_targets_list ${CREATE_TARGET_NAME})
    set(DECLARED_CREATE_TARGETS ${create_targets_list} CACHE INTERNAL "declared create targets" FORCE)

    message(STATUS "declared package ${PACKAGE_NAME}-${PACKAGE_VERSION}")

endfunction()


#######################################################################
#
# add targets from subdirectories
#
#######################################################################

add_subdirectory(ext)


#######################################################################
#
# generate Dockerfile for building package targets
#
#######################################################################

set(DOCKERFILE_CONFIGURE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/docker/Dockerfile.timbre-configure")
set(DOCKERFILE_CONFIGURE_IMAGE "timbre-configure:latest")
set(DOCKERFILE_BUILD_PATH "${CMAKE_CURRENT_BINARY_DIR}/Dockerfile.timbre-build")

set(GENERATE_DOCKERFILE_BUILD_SCRIPT "${CMAKE_CURRENT_BINARY_DIR}/generate_dockerfile_build.py")

file(CONFIGURE OUTPUT ${GENERATE_DOCKERFILE_BUILD_SCRIPT} CONTENT "\

build_dir = '${CMAKE_CURRENT_BINARY_DIR}'
targets_list = '${DECLARED_CREATE_TARGETS}'
docker_file = '${DOCKERFILE_BUILD_PATH}'
docker_preamble = '''
FROM ${DOCKERFILE_CONFIGURE_IMAGE}
'''

targets = targets_list.split(';')

with open(docker_file, 'w') as f:

    f.write(docker_preamble)

    for target in targets:
        f.write('\\n')
        f.write(f'# invoke cmake to build target {target}\\n')
        f.write(f'RUN cmake --build {build_dir} -t {target}\\n')
")

add_custom_target(generate_dockerfile_build
    ALL
    COMMAND ${PYTHON3} ${GENERATE_DOCKERFILE_BUILD_SCRIPT}
    COMMENT
    SOURCES ${GENERATE_DOCKERFILE_BUILD_SCRIPT}
    )