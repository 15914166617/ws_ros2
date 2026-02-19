# 启动rviz2
import os
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory

from launch.actions import (DeclareLaunchArgument, GroupAction,
                            IncludeLaunchDescription, SetEnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import inspect
from launch_ros.actions import Node

# ros2 run teleop_twist_keyboard teleop_twist_keyboard
# ros2 launch example_t1 slam.launch.py 

def generate_launch_description():

    # info
    print(f"QAQ_launch_star")
    print(f"File: {inspect.getfile(inspect.currentframe())}, Line: {inspect.currentframe().f_lineno}, Def: {inspect.currentframe().f_code.co_name}")

    packageName = 'example_t1'
    packageDir = get_package_share_directory(packageName)

    # r2/upper/slam/slamLaunch/config
    # /home/zrc/ws_ros2/src/example_t1/slam/backpack_2d.lua
    configuration_directory = LaunchConfiguration(
        'configuration_directory', default=os.path.join(packageDir, 'slam'))

    # backpack_2d.lua
    configuration_basename = LaunchConfiguration(
        'configuration_basename', default='backpack_2d.lua')

    # resolution = LaunchConfiguration('resolution', default='0.05')
    resolution = LaunchConfiguration('resolution', default='0.001')

    # 地图发布频率，官方内部源码默认为1.0并且有经过后续放大等系列处理，修改时谨慎，因为我把它调成30后，偶发过地图更新特别慢的情况
    publish_period_sec = LaunchConfiguration(
        'publish_period_sec', default='1.0')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # slam

    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        # arguments=['-configuration_directory', configuration_directory,
    #            '-configuration_basename', configuration_basename])
        arguments=['-configuration_directory', '/home/zrc/ws_ros2/src/example_t1/slam/',
                '-configuration_basename', 'backpack_2d.lua'])

    cartographer_occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        # arguments=['-resolution', resolution])
        arguments=['-resolution', resolution, '-publish_period_sec', publish_period_sec])

    # 添加参数声明
    ld = LaunchDescription()

    ld.add_action(cartographer_node)
    ld.add_action(cartographer_occupancy_grid_node)

    return ld
