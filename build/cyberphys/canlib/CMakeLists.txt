cmake_minimum_required(VERSION 3.10)
set(CMAKE_C_STANDARD 99)

# output all the examples to bin directory
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)


project(SSITH-Cyberphys
  VERSION 1.0
  LANGUAGES C)

add_subdirectory(lib)
add_subdirectory(examples)
