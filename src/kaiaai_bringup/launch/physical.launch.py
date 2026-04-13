from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import Command, PathJoinSubstitution
from ament_index_python.packages import get_package_share_path
import os

# 核心函数，用于动态构建一组节点
from launch import LaunchContext

def make_nodes(context: LaunchContext, robot_model, map, use_sim_time, slam, lidar_model):
    # 从 launch 参数中获取实际的字符串值
    robot_model_str = context.perform_substitution(robot_model)
    map_path_str = context.perform_substitution(map)
    use_sim_time_str = context.perform_substitution(use_sim_time)
    slam_str = context.perform_substitution(slam)
    lidar_model_str = context.perform_substitution(lidar_model)

    # 如果 robot_model 没有传参，则使用默认配置
    if len(robot_model_str) == 0:
        import config  # 注意你应提供 config 模块，包含 get_var 函数
        robot_model_str = config.get_var('robot.model')

    # 获取描述包路径和相关配置文件路径
    description_package_path = get_package_share_path(robot_model_str)
    telem_package_path = get_package_share_path('kaiaai_telemetry')

    rviz_config_path = os.path.join(description_package_path, 'rviz', 'navigation.rviz')
    nav_config_path = os.path.join(description_package_path, 'config', 'navigation.yaml')
    config_telem_path_name = os.path.join(telem_package_path, 'config', 'telem.yaml')
    config_override_path_name = os.path.join(description_package_path, 'config', 'telem.yaml')

    # 控制台打印信息，方便调试
    print('Rviz2 config : {}'.format(rviz_config_path))
    print('Nav2  config : {}'.format(nav_config_path))
    print('Map          : {}'.format(map_path_str))
    print('Lidar model  : {}'.format(lidar_model_str))

    # 返回将被启动的所有节点
    return [
        # 启动 Nav2 bringup
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource([
        #         os.path.join(get_package_share_path('nav2_bringup'), 'launch'),
        #         '/bringup_launch.py'
        #     ]),
        #     launch_arguments={
        #         'map': map_path_str,
        #         'use_sim_time': use_sim_time_str,
        #         'slam': slam_str,
        #         'params_file': nav_config_path
        #     }.items(),
        # ),

        # 启动 RViz2，载入指定配置
        # Node(
        #     package='rviz2',
        #     executable='rviz2',
        #     name='rviz2',
        #     output='screen',
        #     arguments=['-d', rviz_config_path],
        #     parameters=[{'use_sim_time': use_sim_time_str.lower() == 'true'}],
        # ),

        # 启动 telemetry 节点，支持 lidar_model 动态配置
        Node(
            package="kaiaai_telemetry",
            executable="telem",
            output="screen",
            parameters=(
                [config_telem_path_name, config_override_path_name,
                 {'laser_scan.lidar_model': lidar_model_str}]
                if len(lidar_model_str) > 0 else
                [config_telem_path_name, config_override_path_name]
            )
        )
    ]


def generate_launch_description():
    # 定义可配置的 Launch 参数
    return LaunchDescription([
        DeclareLaunchArgument(
            name='robot_model',
            default_value='',
            description='Robot description package name'
        ),

        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(
                get_package_share_path('kaiaai_gazebo'),
                'map',
                'living_room.yaml'),
            description='Full path to an existing map file'
        ),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            choices=['true', 'false'],
            description='Use simulation (Gazebo) clock if true'
        ),

        DeclareLaunchArgument(
            'slam',
            default_value='False',
            choices=['True', 'False'],
            description='Navigate while creating a new map'
        ),

        DeclareLaunchArgument(
            'lidar_model',
            default_value='',
            description='Name of the lidar model (optional)'
        ),

        # 启动节点的函数封装
        OpaqueFunction(function=make_nodes, args=[
            LaunchConfiguration('robot_model'),
            LaunchConfiguration('map'),
            LaunchConfiguration('use_sim_time'),
            LaunchConfiguration('slam'),
            LaunchConfiguration('lidar_model'),
        ]),
    ])
