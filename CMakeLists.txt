cmake_minimum_required(VERSION 3.27)

# read project metadata
file(READ ${CMAKE_SOURCE_DIR}/meta/version TIMBRE_PROJECT_VERSION)
string(STRIP ${TIMBRE_PROJECT_VERSION} TIMBRE_PROJECT_VERSION)
file(READ ${CMAKE_SOURCE_DIR}/meta/url TIMBRE_PROJECT_URL)
string(STRIP ${TIMBRE_PROJECT_URL} TIMBRE_PROJECT_URL)
file(READ ${CMAKE_SOURCE_DIR}/meta/description TIMBRE_PROJECT_DESCRIPTION)
string(STRIP ${TIMBRE_PROJECT_DESCRIPTION} TIMBRE_PROJECT_DESCRIPTION)
file(READ ${CMAKE_SOURCE_DIR}/meta/license TIMBRE_PROJECT_LICENSE)
string(STRIP ${TIMBRE_PROJECT_LICENSE} TIMBRE_PROJECT_LICENSE)

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

function(declare_package_export PACKAGE_NAME PACKAGE_VERSION STAGE_NUMBER)

    # define cache variables for the declared package
    set(PACKAGE_NAME_AND_VERSION "${PACKAGE_NAME}_${PACKAGE_VERSION}")
    set(NAME_${PACKAGE_NAME_AND_VERSION} ${PACKAGE_NAME} CACHE INTERNAL "declared name for ${PACKAGE_NAME_AND_VERSION}")
    set(VERSION_${PACKAGE_NAME_AND_VERSION} ${PACKAGE_VERSION} CACHE INTERNAL "declared version for ${PACKAGE_NAME_AND_VERSION}")
    set(STAGE_${PACKAGE_NAME_AND_VERSION} ${STAGE_NUMBER} CACHE INTERNAL "declared stage for ${PACKAGE_NAME_AND_VERSION}")

    # append the package id ( in '<name>_<version>' format) to DECLARED_PACKAGES
    set(declared_packages_list ${DECLARED_PACKAGES})
    list(APPEND declared_packages_list ${PACKAGE_NAME_AND_VERSION})
    set(DECLARED_PACKAGES ${declared_packages_list} CACHE INTERNAL "declared packages")

    message(STATUS "declared package ${PACKAGE_NAME}-${PACKAGE_VERSION} (stage ${STAGE_NUMBER})")

endfunction()

add_subdirectory(ext)


#######################################################################
#
# enable/disable build targets
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

set(CONAN_HOME ""
    CACHE STRING
    "The conan home location. Defaults to ''")

set(CONAN_PACKAGE_CHANNEL ""
    CACHE STRING
    "The packaging channel. Defaults to ''")

set(CACHE_RESTORE_FILE ""
    CACHE STRING
    "Restore file used to initialize the conan cache. Defaults to '' (cache is not initialized)")

set(CACHE_SAVE_FILE "${CMAKE_BINARY_DIR}/cache_save.tgz"
    CACHE STRING
    "Save file containing the conan cache. Defaults to '<cmake-binary-dir>/cache_save.tgz'")


#######################################################################
#
# find required and optional dependencies
#
#######################################################################

# ensure that pkg-config is available
find_package(PkgConfig REQUIRED)

# find required dependencies which may come from the platform
find_package(ZLIB REQUIRED)
#find_package(BZip2 REQUIRED)
#find_package(LibXml2 REQUIRED)

# find python installation
find_package(Python3 REQUIRED)

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
# define export targets and build separate recipe lists for each stage
#
#######################################################################

add_custom_target(export-packages ALL)

set(STAGE1_RECIPES "")
set(STAGE2_RECIPES "")
set(STAGE3_RECIPES "")
set(STAGE4_RECIPES "")

foreach (PACKAGE_NAME_AND_VERSION ${DECLARED_PACKAGES})

    set(PACKAGE_NAME ${NAME_${PACKAGE_NAME_AND_VERSION}})
    set(PACKAGE_VERSION ${VERSION_${PACKAGE_NAME_AND_VERSION}})
    set(STAGE_NUMBER ${STAGE_${PACKAGE_NAME_AND_VERSION}})

    set(RECIPE "${CMAKE_SOURCE_DIR}/ext/${PACKAGE_NAME}/${PACKAGE_VERSION}/conanfile.py")

    # declare the export_<package-name>_<package-version> target
    set(EXPORT_TARGET_NAME "export_${PACKAGE_NAME}_${PACKAGE_VERSION}")
    if(CONAN_PACKAGE_CHANNEL)
        add_custom_target (
            ${EXPORT_TARGET_NAME}
            COMMAND ${CONAN} export ${RECIPE} --channel ${CONAN_PACKAGE_CHANNEL}
            COMMENT "exporting package ${PACKAGE_NAME}-${PACKAGE_VERSION} into channel '${CONAN_PACKAGE_CHANNEL}'"
            SOURCES ${RECIPE}
        )
    else()
        add_custom_target (
            ${EXPORT_TARGET_NAME}
            COMMAND ${CONAN} export ${RECIPE}
            COMMENT "exporting package ${PACKAGE_NAME}-${PACKAGE_VERSION}"
            SOURCES ${RECIPE}
        )
    endif()

    # add export target as a dependency of the export-packages target
    add_dependencies(export-packages ${EXPORT_TARGET_NAME})

    if (${STAGE_NUMBER} EQUAL 1)
        list(APPEND STAGE1_RECIPES ${RECIPE})
    elseif (${STAGE_NUMBER} EQUAL 2)
        list(APPEND STAGE2_RECIPES ${RECIPE})
    elseif (${STAGE_NUMBER} EQUAL 3)
        list(APPEND STAGE3_RECIPES ${RECIPE})
    elseif (${STAGE_NUMBER} EQUAL 4)
        list(APPEND STAGE4_RECIPES ${RECIPE})
    else()
        message(FATAL_ERROR "invalid stage number '${STAGE_NUMBER}' for package ${PACKAGE_NAME_AND_VERSION}")
    endif ()

endforeach()

add_custom_target(restore-cache)

if (CACHE_RESTORE_FILE)
    add_custom_target(restore-cache-file
        COMMAND ${CONAN} cache restore ${CACHE_RESTORE_FILE}
        COMMENT "restoring package cache from ${CACHE_RESTORE_FILE}"
        )
    add_dependencies(restore-cache, restore-cache-file)
endif ()

set(STAGE1_PACKAGE_CACHE_FILE ${CMAKE_BINARY_DIR}/timbre_stage1_cache.tgz)
add_custom_target(stage1
    COMMAND
      ${Python_EXECUTABLE} ${CMAKE_SOURCE_DIR}/build_stage.py
        --conan-path ${Conan} $<$<NOT:$<STREQUAL:${CONAN_HOME},>>:"--conan-home ${CONAN_HOME}">
        --binary-dir ${CMAKE_BINARY_DIR}
        --cache-file ${STAGE1_PACKAGE_CACHE_FILE}
        ${STAGE1_RECIPES}
    BYPRODUCTS ${STAGE1_PACKAGE_CACHE_FILE}
    DEPENDS restore-cache
    COMMENT "building stage1 package cache"
    )

set(STAGE2_PACKAGE_CACHE_FILE ${CMAKE_BINARY_DIR}/timbre_stage2_cache.tgz)
add_custom_target(stage2
    COMMAND
    ${Python_EXECUTABLE} ${CMAKE_SOURCE_DIR}/build_stage.py
    --conan-path ${Conan} $<$<NOT:$<STREQUAL:${CONAN_HOME},>>:"--conan-home ${CONAN_HOME}">
    --binary-dir ${CMAKE_BINARY_DIR}
    --cache-file ${STAGE2_PACKAGE_CACHE_FILE}
    ${STAGE2_RECIPES}
    BYPRODUCTS ${STAGE2_PACKAGE_CACHE_FILE}
    DEPENDS restore-cache
    COMMENT "building stage2 package cache"
)

set(STAGE3_PACKAGE_CACHE_FILE ${CMAKE_BINARY_DIR}/timbre_stage3_cache.tgz)
add_custom_target(stage3
    COMMAND
    ${Python_EXECUTABLE} ${CMAKE_SOURCE_DIR}/build_stage.py
    --conan-path ${Conan} $<$<NOT:$<STREQUAL:${CONAN_HOME},>>:"--conan-home ${CONAN_HOME}">
    --binary-dir ${CMAKE_BINARY_DIR}
    --cache-file ${STAGE3_PACKAGE_CACHE_FILE}
    ${STAGE3_RECIPES}
    BYPRODUCTS ${STAGE3_PACKAGE_CACHE_FILE}
    DEPENDS restore-cache
    COMMENT "building stage3 package cache"
)

set(STAGE4_PACKAGE_CACHE_FILE ${CMAKE_BINARY_DIR}/timbre_stage4_cache.tgz)
add_custom_target(stage4
    COMMAND
    ${Python_EXECUTABLE} ${CMAKE_SOURCE_DIR}/build_stage.py
    --conan-path ${Conan} $<$<NOT:$<STREQUAL:${CONAN_HOME},>>:"--conan-home ${CONAN_HOME}">
    --binary-dir ${CMAKE_BINARY_DIR}
    --cache-file ${STAGE4_PACKAGE_CACHE_FILE}
    ${STAGE4_RECIPES}
    BYPRODUCTS ${STAGE4_PACKAGE_CACHE_FILE}
    DEPENDS restore-cache
    COMMENT "building stage4 package cache"
)

add_custom_target(save-cache
    COMMAND ${CONAN} cache save '*:*' --no-source --file=${CACHE_SAVE_FILE}
    COMMENT "saving package cache to ${CACHE_SAVE_FILE}"
)
