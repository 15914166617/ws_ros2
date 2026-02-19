ros2 pkg create --build-type ament_cmake fishbot_bringup
ros2 pkg create --build-type ament_python fishbot_description


colcon build --packages-select fishbot_bringup
colcon build --packages-select fishbot_description

source install/setup.bash

ros2 run fishbot_bringup fishbot_bringup

ros2 run rqt_tf_tree rqt_tf_tree


ros2 run micro_ros_agent micro_ros_agent udp4 --port 8888
ros2 run teleop_twist_keyboard teleop_twist_keyboard
ros2 launch fishbot_bringup fishbot_bringup.launch.py

rqt