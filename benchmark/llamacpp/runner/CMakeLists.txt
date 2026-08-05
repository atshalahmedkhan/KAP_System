cmake_minimum_required(VERSION 3.16)
project(token_id_runner LANGUAGES C CXX)

set(LLAMA_BUILD_COMMON OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_SERVER OFF CACHE BOOL "" FORCE)
set(LLAMA_CURL OFF CACHE BOOL "" FORCE)

add_subdirectory(/src/llama.cpp llama.cpp-build)

add_executable(token-id-runner token-id-runner.cpp)
target_link_libraries(token-id-runner PRIVATE llama)
target_compile_features(token-id-runner PRIVATE cxx_std_17)
