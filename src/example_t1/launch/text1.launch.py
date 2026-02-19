
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
# from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
# from launch.substitutions import LaunchConfiguration, PythonExpression
# from launch_ros.actions import Node

# 启动 rviz  slam

def generate_launch_description():
   
    packageName = 'example_t1'
    packageDir = get_package_share_directory(packageName)

    # ros2 launch example_t1 text1.launch.py 
    # ros2 bag play t1/rosbag2_2024_08_28-09_03_34_0.db3 -l
    # ros2 bag play t3/rosbag2_2024_08_28-09_03_20_0.db3 -l

    # ros2 run teleop_twist_keyboard teleop_twist_keyboard
    # ros2 run teleop_twist_keyboard teleop_twist_keyboard
    # ros2 bag  play rosbag2_2024_08_24-09_30_17_0.db3 -l

    # /home/zrc/ws_ros2/src/example_t1/rviz/rviz.launch.py
    # /home/zrc/ws_ros2/src/example_t1/slam/slam.launch.py
    launch_rviz=IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(packageDir,'rviz','rviz.launch.py')),
            launch_arguments={
            }.items())
    launch_slam=IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(packageDir,'slam','slam.launch.py')),
            launch_arguments={
            }.items())


    ld = LaunchDescription()
    ld.add_action(launch_rviz)
    ld.add_action(launch_slam)

    return ld
