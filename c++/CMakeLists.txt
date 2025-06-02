#
# cmake -DCMAKE_BUILD_TYPE=Debug .
# cmake -DCMAKE_BUILD_TYPE=Release .
#
cmake_minimum_required(VERSION 3.4...3.18)
project(demo)

# https://stackoverflow.com/questions/38296756/what-is-the-idiomatic-way-in-cmake-to-add-the-fpic-compiler-option
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_subdirectory(pybind11)

pybind11_add_module(
    demo
    c++.cpp
    c++-body.cpp
    cpp.cpp
)

set_target_properties(demo PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}")

set_target_properties(demo PROPERTIES
    CXX_STANDARD 17
    C_STANDARD 99
)

target_compile_definitions(demo PRIVATE
    #-DUNICODE
)

target_include_directories(demo PRIVATE
#    ${PYTHON_INCLUDE_DIRS}
    litehtml/include
#    ${PYBIND11_INCLUDE_DIR}
)

target_link_libraries(demo PRIVATE
#    ${PYTHON_LIBRARIES}
)
