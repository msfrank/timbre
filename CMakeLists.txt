cmake_minimum_required(VERSION 3.27)

# read project metadata
file(READ ${CMAKE_SOURCE_DIR}/meta/version TIMBRE_PROJECT_VERSION)
string(STRIP ${TIMBRE_PROJECT_VERSION} TIMBRE_PROJECT_VERSION)
file(READ ${CMAKE_SOURCE_DIR}/meta/url TIMBRE_PROJECT_URL)
string(STRIP ${TIMBRE_PROJECT_URL} TIMBRE_PROJECT_URL)
file(READ ${CMAKE_SOURCE_DIR}/meta/description TIMBRE_PROJECT_DESCRIPTION)
string(STRIP ${TIMBRE_PROJECT_DESCRIPTION} TIMBRE_PROJECT_DESCRIPTION)

# declare the project
project(timbre
    VERSION ${TIMBRE_PROJECT_VERSION}
    HOMEPAGE_URL ${TIMBRE_PROJECT_URL}
    DESCRIPTION ${TIMBRE_PROJECT_DESCRIPTION}
    )

# if build type was not explicitly defined then default to Debug
if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Debug" CACHE STRING "build type not specified so defaulting to Debug" FORCE)
endif()

# define IS_DEBUG_BUILD boolean to make it easier to check whether we are in debug mode
if("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
    set(IS_DEBUG_BUILD ON)
else()
    set(IS_DEBUG_BUILD OFF)
endif()


#######################################################################
#
# declare packages data
#
#######################################################################

set(DECLARED_PACKAGES "" CACHE INTERNAL "declared packages")

function(declare_package_export PACKAGE_NAME PACKAGE_VERSION)

    # define a NAME_* and VERSION_* cache variable for the declared package
    set(PACKAGE_NAME_AND_VERSION "${PACKAGE_NAME}_${PACKAGE_VERSION}")
    set(NAME_${PACKAGE_NAME_AND_VERSION} ${PACKAGE_NAME} CACHE INTERNAL "declared name for ${PACKAGE_NAME_AND_VERSION}")
    set(VERSION_${PACKAGE_NAME_AND_VERSION} ${PACKAGE_VERSION} CACHE INTERNAL "declared version for ${PACKAGE_NAME_AND_VERSION}")

    # append the package id ( in '<name>_<version>' format) to DECLARED_PACKAGES
    set(declared_packages_list ${DECLARED_PACKAGES})
    list(APPEND declared_packages_list ${PACKAGE_NAME_AND_VERSION})
    set(DECLARED_PACKAGES ${declared_packages_list} CACHE INTERNAL "declared packages")

    message(STATUS "declared package ${PACKAGE_NAME}-${PACKAGE_VERSION}")

endfunction()

add_subdirectory(ext)


#######################################################################
#
#
#
#######################################################################

option(DISABLE_LOCAL_BUILD "Disable local build" FALSE)
option(ENABLE_DOCKER_BUILD "Enable docker build" FALSE)

# if docker build is enabled then add targets from docker directory
if (ENABLE_DOCKER_BUILD)
    add_subdirectory(docker)
endif()

# if local build is disabled then don't process any further targets
if (DISABLE_LOCAL_BUILD)
    return()
endif()


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

string(REGEX REPLACE "Conan version ([0-9]+\\.[0-9]+\\.[0-9]+)\n" "\\1"
    CONAN_FULL_VERSION
    "${CONAN_OUTPUT}")
if (NOT CONAN_FULL_VERSION)
    message(FATAL_ERROR "Failed to detect conan version. Output was: ${CONAN_OUTPUT}")
endif()

string(REGEX REPLACE "([0-9]+)\\.[0-9]+\\.[0-9]+" "\\1"
    CONAN_MAJOR_VERSION
    "${CONAN_FULL_VERSION}")
if (${CONAN_MAJOR_VERSION} EQUAL 2)
    message(STATUS "Found Conan: ${Conan} (found version \"${CONAN_FULL_VERSION}\")")
else()
    message(FATAL_ERROR "Version 2 of conan is required but detected: ${CONAN_FULL_VERSION}")
endif()


#######################################################################
#
# configure tools and paths
#
#######################################################################

if (CONAN_HOME)
    set(CONAN "${CMAKE_COMMAND} -E env CONAN_HOME=\"${CONAN_HOME}\" ${Conan}")
else()
    set(CONAN ${Conan})
endif ()


#######################################################################
#
# define export and create targets
#
#######################################################################

add_custom_target(export-all-packages ALL)
add_custom_target(create-all-packages)

foreach (PACKAGE_NAME_AND_VERSION ${DECLARED_PACKAGES})

    set(PACKAGE_NAME ${NAME_${PACKAGE_NAME_AND_VERSION}})
    set(PACKAGE_VERSION ${VERSION_${PACKAGE_NAME_AND_VERSION}})

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

endforeach()