cmake_minimum_required(VERSION 3.22)
project(reliquary_vulkan_visualizer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Vulkan REQUIRED)

add_executable(reliquary_vulkan_visualizer src/main.cpp)
target_link_libraries(reliquary_vulkan_visualizer PRIVATE Vulkan::Vulkan)
target_compile_definitions(reliquary_vulkan_visualizer PRIVATE RELIQUARY_VULKAN_ENABLED=1)

if(APPLE)
  target_compile_definitions(reliquary_vulkan_visualizer PRIVATE VK_ENABLE_BETA_EXTENSIONS)
endif()
