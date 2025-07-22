FROM fedora:latest

# install build tools
RUN dnf install -y g++ git cmake conan patchelf readelf

# install platform dependencies
RUN dnf install -y libxml2-devel zlib-devel bzip2-devel java-21-openjdk-devel libuuid-devel

# install build dependencies
RUN dnf install -y perl-File-Copy perl-File-Compare perl-IPC-Cmd perl-FindBin

# create user
RUN adduser jrandomhacker

# switch current user
USER jrandomhacker

# change to home directory
WORKDIR /home/jrandomhacker

# check out timbre repository
ADD --exclude .git . /home/jrandomhacker/src/timbre

# change to timbre repository directory
WORKDIR /home/jrandomhacker/src/timbre

# generate the buildsystem
RUN cmake -B build

# run the export-all-packages build target
RUN cmake --build build/ -t export-all-packages --parallel 1
