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

# find conan package manager
find_program(Conan conan REQUIRED)

# check the conan version
execute_process(COMMAND Conan --version
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


#######################################################################
#
# define build constants
#
#######################################################################

function(declare_package_export PACKAGE_NAME PACKAGE_VERSION)
    if(${CONAN_PACKAGE_CHANNEL})
        add_custom_target (
            export_${PACKAGE_NAME}_${PACKAGE_VERSION}
            ALL
            COMMAND ${Conan} export ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py --channel ${CONAN_PACKAGE_CHANNEL}
            COMMENT "exporting package ${PACKAGE_NAME}-${PACKAGE_VERSION} into channel '${CONAN_PACKAGE_CHANNEL}'"
            SOURCES ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py
        )
    else()
        add_custom_target (
            export_${PACKAGE_NAME}_${PACKAGE_VERSION}
            ALL
            COMMAND ${Conan} export ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py
            COMMENT "exporting package ${PACKAGE_NAME}-${PACKAGE_VERSION}"
            SOURCES ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py
        )
    endif()
endfunction()


#######################################################################
#
# add targets from subdirectories
#
#######################################################################

add_subdirectory(ext)
