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

set(DECLARED_EXPORT_TARGETS "" CACHE INTERNAL "declared export targets" FORCE)

function(declare_package_export PACKAGE_NAME PACKAGE_VERSION)

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
    add_dependencies(export-all-packages ${EXPORT_TARGET_NAME})

    set(export_targets_list ${DECLARED_EXPORT_TARGETS})
    list(APPEND export_targets_list ${EXPORT_TARGET_NAME})
    set(DECLARED_EXPORT_TARGETS ${export_targets_list} CACHE INTERNAL "declared export targets" FORCE)

    #
    set(CREATE_TARGET_NAME "create_${PACKAGE_NAME}_${PACKAGE_VERSION}")
    add_custom_target (
        ${CREATE_TARGET_NAME}
        COMMAND ${CONAN} create ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py --build=missing
        COMMENT "creating package ${PACKAGE_NAME}-${PACKAGE_VERSION}"
        SOURCES ${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py
    )
    add_dependencies(create-all-packages ${CREATE_TARGET_NAME})

    message(STATUS "declared export target ${PACKAGE_NAME}-${PACKAGE_VERSION}")

endfunction()


#######################################################################
#
# add targets from subdirectories
#
#######################################################################

add_subdirectory(ext)