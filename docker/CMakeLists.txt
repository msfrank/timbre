
#######################################################################
#
# declare options
#
#######################################################################

set(DOCKER_PROGRAM ""
    CACHE FILEPATH
    "Path to the docker command. If empty then the program path is auto-detected. Defaults to ''")

set(DOCKER_REQUIRES_SUDO "FALSE"
    CACHE BOOL
    "TRUE if the docker command requires sudo privileges. Defaults to 'FALSE'")

set(DOCKER_PLATFORM ""
    CACHE STRING
    "Target platform for docker image. If empty then the platform is auto-detected. Defaults to ''")

set(DOCKER_CONAN_PROFILE ""
    CACHE FILEPATH
    "Conan profile used when building inside docker. If empty then the profile is auto-detected. Defaults to ''")

set(DOCKER_REGISTRY ""
    CACHE STRING
    "The docker registry to export to. If empty then defaults to the local image store. Defaults to ''")


#######################################################################
#
# find required and optional dependencies
#
#######################################################################

# find python installation
find_package (Python3 COMPONENTS Interpreter)

# find docker CLI
if (DOCKER_PROGRAM)
    set(Docker ${DOCKER_PROGRAM})
    message(STATUS "Using Docker: ${Docker} (specified by DOCKER_PROGRAM)")
else()
    find_program(Docker docker)
    if (Docker EQUAL "Docker-NOTFOUND")
        message(STATUS "Docker not found, skipping generation of docker targets")
    else()
        message(STATUS "Found Docker: ${Docker}")
    endif()
endif()


#######################################################################
#
# configure tools and paths
#
#######################################################################

set(PYTHON3 ${Python3_EXECUTABLE})

if (DOCKER_REQUIRES_SUDO)
    set(DOCKER "sudo;${Docker}")
else ()
    set(DOCKER ${Docker})
endif ()


#######################################################################
#
# define Data tables
#
#######################################################################

set(CONAN_PROFILE_Linux_x86_64_Debug    "Linux.x86_64.Debug")
set(CONAN_PROFILE_Linux_arm64_Debug     "Linux.armv8.Debug")
set(CONAN_PROFILE_Linux_aarch64_Debug   "Linux.armv8.Debug")


#######################################################################
#
# generate timbre/base Dockerfile
#
#######################################################################

set(DOCKERFILE_BASE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/Dockerfile.base")
set(DOCKERFILE_BASE_IMAGE "timbre/base:latest")
set(DOCKERFILE_PATH "${CMAKE_CURRENT_BINARY_DIR}/Dockerfile")
set(GENERATE_DOCKERFILE_SCRIPT "${CMAKE_CURRENT_BINARY_DIR}/generate_dockerfile.py")

if (DOCKER_REGISTRY)
    set(BASE_IMAGE "${DOCKER_REGISTRY}${DOCKERFILE_BASE_IMAGE}")
else()
    set(BASE_IMAGE ${DOCKERFILE_BASE_IMAGE})
endif()

file(CONFIGURE OUTPUT ${GENERATE_DOCKERFILE_SCRIPT} CONTENT "\

build_dir = 'build'
targets_list = '${DECLARED_PACKAGES}'
docker_file = '${DOCKERFILE_PATH}'

docker_preamble = f'''
FROM ${BASE_IMAGE}
ARG is_debug_build=0
USER jrandomhacker
WORKDIR /home/jrandomhacker/src/timbre
RUN cmake --build {build_dir} -t export-all-packages --parallel 1
'''

create_targets = ['create_' + t for t in targets_list.split(';') if t != '']

with open(docker_file, 'w') as f:

    f.write(docker_preamble)

    for target in create_targets:
        f.write('\\n')
        f.write(f'# invoke cmake to build target {target}\\n')
        f.write(f'RUN cmake --build {build_dir} -t {target}\\n')

    f.write('\\n')
    f.write('RUN conan cache clean --download --source --temp --backup-sources \\'*\\'\\n')
    f.write('ENV IS_DEBUG_BUILD=$is_debug_build\\n')
    f.write('RUN if test $IS_DEBUG_BUILD == 0; then conan cache clean --build \\'*\\'; fi\\n')
")

add_custom_target(generate_dockerfile
    COMMAND ${PYTHON3} ${GENERATE_DOCKERFILE_SCRIPT}
    COMMENT "generating base Dockerfile"
    SOURCES ${GENERATE_DOCKERFILE_SCRIPT}
    BYPRODUCTS ${DOCKERFILE_PATH}
)


#######################################################################
#
# define docker build targets
#
#######################################################################

if (DOCKER_REGISTRY)
    set(DOCKER_OUTPUT "type=registry,push=true")
else()
    set(DOCKER_OUTPUT "type=docker")
endif()

# set the PLATFORM_ID
if (DOCKER_PLATFORM)
    set(PLATFORM_ID ${DOCKER_PLATFORM})
else()
    set(PLATFORM_ID "linux/${CMAKE_SYSTEM_PROCESSOR}")
endif()
if (NOT PLATFORM_ID)
    message(FATAL_ERROR "failed to determine docker platform id")
endif()

# set the PROFILE_PATH
if (DOCKER_CONAN_PROFILE)
    set(PROFILE_NAME ${DOCKER_CONAN_PROFILE})
else()
    set(PROFILE_NAME ${CONAN_PROFILE_Linux_${CMAKE_SYSTEM_PROCESSOR}_${CMAKE_BUILD_TYPE}})
endif()
if (NOT PROFILE_NAME)
    message(STATUS "processor: ${CMAKE_SYSTEM_PROCESSOR} build type: ${CMAKE_BUILD_TYPE}")
    message(FATAL_ERROR "failed to determine conan profile name")
endif()

# build the timbre/base image
add_custom_target(build_docker_base_image
    COMMAND ${DOCKER} build
    --platform ${PLATFORM_ID}
    --build-arg profile_name=${PROFILE_NAME}
    -o ${DOCKER_OUTPUT}
    -t "${DOCKER_REGISTRY}timbre/base"
    -t "${DOCKER_REGISTRY}timbre/base:${CMAKE_PROJECT_VERSION}"
    -f ${DOCKERFILE_BASE_PATH}
    --label "org.opencontainers.image.version=${CMAKE_PROJECT_VERSION}"
    .
    COMMENT "building timbre/base docker image"
    DEPENDS ${DOCKERFILE_BASE_PATH}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )

# build the timbre image
add_custom_target(build_docker_image
    COMMAND ${DOCKER} build
    --platform ${PLATFORM_ID}
    --build-arg is_debug_build=$<BOOL:${IS_DEBUG_BUILD}>
    -o ${DOCKER_OUTPUT}
    -t "${DOCKER_REGISTRY}timbre"
    -t "${DOCKER_REGISTRY}timbre:${CMAKE_PROJECT_VERSION}"
    -f ${DOCKERFILE_PATH}
    --label "org.opencontainers.image.version=${CMAKE_PROJECT_VERSION}"
    --label "org.opencontainers.image.source=${CMAKE_PROJECT_HOMEPAGE_URL}"
    --label "org.opencontainers.image.description=${CMAKE_PROJECT_DESCRIPTION}"
    --label "org.opencontainers.image.licenses=${TIMBRE_PROJECT_LICENSE}"
    .
    COMMENT "building timbre docker image"
    DEPENDS generate_dockerfile build_docker_base_image
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )
