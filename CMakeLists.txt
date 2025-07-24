cmake_minimum_required(VERSION 3.27)

project(timbre)

#######################################################################
#
# declare options
#
#######################################################################

set(CONAN_PACKAGE_CHANNEL ""
    CACHE STRING
    "The packaging channel. Defaults to ''")

set(CONAN_HOME ""
    CACHE STRING
    "The conan home location. Defaults to ''")

set(DOCKER_REQUIRES_SUDO "FALSE"
    CACHE BOOL
    "TRUE if the docker command requires sudo privileges. Defaults to 'FALSE'")

set(DOCKER_REGISTRY ""
    CACHE STRING
    "The docker registry to export to. If empty then defaults to the local image store. Defaults to ''")


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

# find docker CLI
find_program(Docker docker)

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

set(PYTHON3 ${Python3_EXECUTABLE})

if (CONAN_HOME)
    set(CONAN "${CMAKE_COMMAND} -E env CONAN_HOME=\"${CONAN_HOME}\" ${Conan}")
else()
    set(CONAN ${Conan})
endif ()

if (DOCKER_REQUIRES_SUDO)
    set(DOCKER "sudo;${Docker}")
else ()
    set(DOCKER ${Docker})
endif ()


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
    if(CONAN_PACKAGE_CHANNEL)
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

set(DOCKERFILE_BASE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/docker/Dockerfile.base")
set(DOCKERFILE_BASE_IMAGE "timbre/base:latest")
set(DOCKERFILE_PATH "${CMAKE_CURRENT_BINARY_DIR}/Dockerfile")
set(GENERATE_DOCKERFILE_SCRIPT "${CMAKE_CURRENT_BINARY_DIR}/generate_dockerfile.py")

if (DOCKER_REGISTRY)
    set(BASE_IMAGE "${DOCKER_REGISTRY}/${DOCKERFILE_BASE_IMAGE}")
else()
    set(BASE_IMAGE ${DOCKERFILE_BASE_IMAGE})
endif()

file(CONFIGURE OUTPUT ${GENERATE_DOCKERFILE_SCRIPT} CONTENT "\

build_dir = 'build'
targets_list = '${DECLARED_CREATE_TARGETS}'
#targets_list = ''
docker_file = '${DOCKERFILE_PATH}'

docker_preamble = f'''
FROM ${BASE_IMAGE}
USER jrandomhacker
WORKDIR /home/jrandomhacker/src/timbre
RUN cmake --build {build_dir} -t export-all-packages --parallel 1
'''

targets = [t for t in targets_list.split(';') if t != '']

with open(docker_file, 'w') as f:

    f.write(docker_preamble)

    for target in targets:
        f.write('\\n')
        f.write(f'# invoke cmake to build target {target}\\n')
        f.write(f'RUN cmake --build {build_dir} -t {target}\\n')
")

add_custom_target(generate_dockerfile
    ALL
    COMMAND ${PYTHON3} ${GENERATE_DOCKERFILE_SCRIPT}
    COMMENT "generating Dockerfile"
    SOURCES ${GENERATE_DOCKERFILE_SCRIPT}
    )


#######################################################################
#
#
#
#######################################################################

if (Docker)

    if (DOCKER_REGISTRY)
        set(DOCKER_OUTPUT "type=registry,push=true")
        set(DOCKER_TAG_PREFIX "${DOCKER_REGISTRY}/")
    else()
        set(DOCKER_OUTPUT "type=docker")
        set(DOCKER_TAG_PREFIX "")
    endif ()

add_custom_target(build_docker_base_image
    COMMAND ${DOCKER} build
      --build-arg os=Linux
      --build-arg arch=x86_64
      --build-arg release_type=Debug
      -o ${DOCKER_OUTPUT}
      -t "${DOCKER_TAG_PREFIX}timbre/base"
      -f ${DOCKERFILE_BASE_PATH}
      .
    COMMENT "building timbre/base docker image"
    DEPENDS ${DOCKERFILE_BASE_PATH}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )

add_custom_target(build_docker_image
    COMMAND ${DOCKER} build
      -o ${DOCKER_OUTPUT}
      -t "${DOCKER_TAG_PREFIX}timbre/timbre"
      -f ${DOCKERFILE_PATH}
      .
    COMMENT "building timbre/timbre docker image"
    DEPENDS generate_dockerfile build_docker_base_image
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

else ()
    message(STATUS "docker not found, skipping generation of docker targets")
endif()
