cmake_minimum_required(VERSION 3.10)
project(MotionDetector)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找 OpenCV
find_package(OpenCV REQUIRED)

# 包含目录
include_directories(
    ${OpenCV_INCLUDE_DIRS}
    ${PROJECT_SOURCE_DIR}/src
)

# 源文件
set(SOURCES
    src/main.cpp
    src/motion_detector.cpp
    src/network_sender.cpp
    src/config.cpp
)

# 生成可执行文件
add_executable(motion_detector ${SOURCES})

# 链接库
target_link_libraries(motion_detector
    ${OpenCV_LIBS}
    pthread
)

# 编译选项
target_compile_options(motion_detector PRIVATE
    -Wall
    -Wextra
    -O2
)

# 安装规则
install(TARGETS motion_detector DESTINATION bin)
