cmake_minimum_required(VERSION 3.5)
project(mycobot_280)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# Include directories
include_directories(include)

# Add executables
add_executable(mycobot_driver src/mycobot_driver.cpp)
ament_target_dependencies(mycobot_driver rclcpp std_msgs)

# Install targets
install(TARGETS
  mycobot_driver
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
