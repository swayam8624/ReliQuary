cmake_minimum_required(VERSION 3.22)
project(reliquary_vulkan_visualizer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(FetchContent)

find_package(Vulkan REQUIRED)
find_package(glfw3 REQUIRED)
find_package(CURL REQUIRED)
find_package(nlohmann_json REQUIRED)

FetchContent_Declare(
  imgui
  URL https://github.com/ocornut/imgui/archive/refs/tags/v1.90.9.zip
  DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
FetchContent_MakeAvailable(imgui)

add_library(imgui STATIC
  ${imgui_SOURCE_DIR}/imgui.cpp
  ${imgui_SOURCE_DIR}/imgui_draw.cpp
  ${imgui_SOURCE_DIR}/imgui_tables.cpp
  ${imgui_SOURCE_DIR}/imgui_widgets.cpp
  ${imgui_SOURCE_DIR}/backends/imgui_impl_glfw.cpp
  ${imgui_SOURCE_DIR}/backends/imgui_impl_vulkan.cpp
)

target_include_directories(imgui PUBLIC
  ${imgui_SOURCE_DIR}
  ${imgui_SOURCE_DIR}/backends
)

target_link_libraries(imgui PUBLIC Vulkan::Vulkan glfw)

add_executable(reliquary_vulkan_visualizer src/main.cpp)
target_link_libraries(reliquary_vulkan_visualizer PRIVATE
  Vulkan::Vulkan
  glfw
  imgui
  CURL::libcurl
  nlohmann_json::nlohmann_json
)
target_compile_definitions(reliquary_vulkan_visualizer PRIVATE RELIQUARY_VULKAN_ENABLED=1)

if(APPLE)
  target_compile_definitions(reliquary_vulkan_visualizer PRIVATE VK_ENABLE_BETA_EXTENSIONS)
endif()
