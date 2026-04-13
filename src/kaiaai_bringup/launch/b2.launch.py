
# 建图，基础建图
# 单纯的手动建图，好控制，建图参数高，因为使用car,不是slam建图
import os

from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription, LaunchContext
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import (
    LaunchConfiguration,
    Command,
    ThisLaunchFileDir,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


# -------------------------------
# robot_description + SLAM nodes
# -------------------------------
def make_nodes(context: LaunchContext,
               robot_model,
               use_sim_time,
               configuration_basename,
               lidar_model):

    robot_model_str = context.perform_substitution(robot_model)
    use_sim_time_str = context.perform_substitution(use_sim_time)
    configuration_basename_str = context.perform_substitution(configuration_basename)
    lidar_model_str = context.perform_substitution(lidar_model)

    description_pkg = get_package_share_path(robot_model_str)
    telem_pkg = get_package_share_path('kaiaai_telemetry')

    # URDF
    urdf_path = os.path.join(
        description_pkg,
        'urdf',
        'robot.urdf.xacro'
    )

    robot_description = ParameterValue(
        Command(['xacro ', urdf_path]),
        value_type=str
    )

    # Cartographer
    carto_config_dir = os.path.join(description_pkg, 'config')
    rviz_cfg = os.path.join(description_pkg, 'rviz', 'cartographer.rviz')

    # Telemetry
    telem_cfg_base = os.path.join(telem_pkg, 'config', 'telem.yaml')
    telem_cfg_override = os.path.join(description_pkg, 'config', 'telem.yaml')

    print('Robot model         :', robot_model_str)
    print('URDF                :', urdf_path)
    print('Cartographer config :', carto_config_dir, configuration_basename_str)

    nodes = []

    # robot_state_publisher（必须最早）
    nodes.append(
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
        )
    )

    # joint_state_publisher
    nodes.append(
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            condition=UnlessCondition(LaunchConfiguration('gui'))
        )
    )
    nodes.append(
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            condition=IfCondition(LaunchConfiguration('gui'))
        )
    )

    # telemetry
    nodes.append(
        Node(
            package='kaiaai_telemetry',
            executable='telem',
            output='screen',
            parameters=(
                [telem_cfg_base, telem_cfg_override,
                 {'laser_scan.lidar_model': lidar_model_str}]
                if lidar_model_str else
                [telem_cfg_base, telem_cfg_override]
            )
        )
    )

    # cartographer
    nodes.append(
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time_str.lower() == 'true'}],
            arguments=[
                '-configuration_directory', carto_config_dir,
                '-configuration_basename', configuration_basename_str
            ]
        )
    )

    # rviz
    nodes.append(
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', rviz_cfg],
            parameters=[{'use_sim_time': use_sim_time_str.lower() == 'true'}],
        )
    )

    return nodes


# -------------------------------
# launch description
# -------------------------------
def generate_launch_description():

    return LaunchDescription([

        # ---------- launch args ----------
        DeclareLaunchArgument(
            'robot_model',
            description='Robot description package name (REQUIRED)'
        ),
        DeclareLaunchArgument(
            'configuration_basename',
            default_value='cartographer_lds_2d.lua'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            choices=['true', 'false']
        ),
        DeclareLaunchArgument(
            'resolution',
            default_value='0.005'
        ),
        DeclareLaunchArgument(
            'publish_period_sec',
            default_value='1.0'
        ),
        DeclareLaunchArgument(
            'lidar_model',
            default_value=''
        ),
        DeclareLaunchArgument(
            'gui',
            default_value='false'
        ),

        # ---------- micro-ROS agent ----------
        Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent',
            output='screen',
            arguments=['udp4', '--port', '8888']
        ),

        # ---------- occupancy grid ----------
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                ThisLaunchFileDir(),
                '/occupancy_grid.launch.py'
            ]),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'resolution': LaunchConfiguration('resolution'),
                'publish_period_sec': LaunchConfiguration('publish_period_sec')
            }.items(),
        ),

        # ---------- core nodes ----------
        OpaqueFunction(
            function=make_nodes,
            args=[
                LaunchConfiguration('robot_model'),
                LaunchConfiguration('use_sim_time'),
                LaunchConfiguration('configuration_basename'),
                LaunchConfiguration('lidar_model'),
            ]
        ),
    ])
# 建图
# ros2 launch kaiaai_bringup b2.launch.py   robot_model:=makerspet_loki   configuration_basename:=backpack_2d.lua
# ros2 launch kaiaai_bringup b2.launch.py   robot_model:=makerspet_loki   configuration_basename:=cartographer_lds_2d.lua
# 键盘控制
# ros2 run kaiaai_teleop teleop_keyboard robot_model:=makerspet_loki
# 地图保存
# ros2 run nav2_map_server map_saver_cli -f ~/map --ros-args -p save_map_timeout:=60.0

# colcon build --packages-select kaiaai_bringup
# colcon build --packages-select makerspet_loki
# 