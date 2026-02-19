ros2 pkg create <package_name> --build-type ament_cmake --dependencies rclcpp std_msgs
ros2 pkg create my_text1 --build-type ament_cmake --dependencies rclcpp std_msgs
colcon build --packages-select my_text1
source install/setup.bash
ros2 launch my_text1 m1.launch.py 

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

