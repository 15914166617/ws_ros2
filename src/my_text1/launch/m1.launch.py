from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_path
import os


def make_nodes(context, *args, **kwargs):
    # 获取 launch 参数值
    robot_model_str = context.perform_substitution(LaunchConfiguration('robot_model'))
    map_path_str = context.perform_substitution(LaunchConfiguration('map'))
    use_sim_time_str = context.perform_substitution(LaunchConfiguration('use_sim_time'))
    slam_str = context.perform_substitution(LaunchConfiguration('slam'))
    lidar_model_str = context.perform_substitution(LaunchConfiguration('lidar_model'))

    # 如果未提供 robot_model，可设置默认
    # if len(robot_model_str) == 0:
    #     robot_model_str = 'makerspet_loki'

    # 获取机器人模型包路径（通常包含 URDF、RViz 配置等）
    description_package_path = get_package_share_path(robot_model_str)

    # 构造 URDF 路径（用于 robot_state_publisher）
    urdf_path = PathJoinSubstitution([
        FindPackageShare(robot_model_str),
        'urdf',
        'robot.urdf.xacro'
    ])

    # 构造 robot_description 参数（robot_state_publisher 需要）
    robot_description = ParameterValue(
        # Command(['xacro', urdf_path]),
        Command(['xacro', ' ', urdf_path]),
        value_type=str
    )
    # 构造 robot_description 参数（robot_state_publisher 需要）
    # robot_description = ParameterValue(
    #     Command([
    #         'xacro',
    #         PathJoinSubstitution([
    #             FindPackageShare(robot_model_str),
    #             'urdf',
    #             'robot.urdf.xacro'
    #         ])
    #     ]),
    #     value_type=str
    # )

    # 获取 RViz 配置路径
    rviz_config_path = os.path.join(description_package_path, 'rviz', 'navigation.rviz')

    # 获取导航参数配置文件路径
    nav_config_path = os.path.join(description_package_path, 'config', 'navigation.yaml')

    # 获取 telemetry 配置路径（路径 1：自身配置；路径 2：机器人覆盖配置）
    telem_package_path = get_package_share_path('kaiaai_telemetry')
    config_telem_path_name = os.path.join(telem_package_path, 'config', 'telem.yaml')
    config_override_path_name = os.path.join(description_package_path, 'config', 'telem.yaml')

    # 设置 lidar_model 参数（如有 LaunchConfiguration 可替换此处）
    # lidar_model_str = ''  # 如果你以后想通过 launch 参数指定，可加入 DeclareLaunchArgument('lidar_model')

    # --- 启动节点定义 ---

    # 节点：micro-ROS Agent（接收 STM32/ESP32 发来的话题）
    micro_ros_agent_node = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        name='micro_ros_agent',
        output='screen',
        arguments=['udp4', '-p', '8888']
    )

    # 节点：robot_state_publisher（根据 robot_description 发布 tf）
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time_str.lower() == 'true',
            'robot_description': robot_description
        }]
    )

    # 节点：rviz2（用于导航可视化）
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': use_sim_time_str.lower() == 'true'}]
    )

    # 节点：nav2_bringup 启动（导航主节点集合）
    # nav2_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([
    #         os.path.join(get_package_share_path('nav2_bringup'), 'launch'),
    #         'bringup_launch.py'
    #     ]),
    #     launch_arguments={
    #         'map': map_path_str,
    #         'use_sim_time': use_sim_time_str,
    #         'slam': slam_str,
    #         'params_file': nav_config_path
    #     }.items()
    # )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_path('nav2_bringup'),
                'launch',
                'bringup_launch.py'
            )
        ),
        launch_arguments={
            'map': map_path_str,
            'use_sim_time': use_sim_time_str,
            'slam': slam_str,
            'params_file': nav_config_path
        }.items()
    )


    # 节点：kaiaai_telemetry（发布雷达、电机等传感器状态）
    telemetry_node = Node(
        package='kaiaai_telemetry',
        executable='telem',
        output='screen',
        parameters=[
            config_telem_path_name,
            config_override_path_name,
            {'laser_scan.lidar_model': lidar_model_str}
        ] if len(lidar_model_str) > 0 else [
            config_telem_path_name,
            config_override_path_name
        ]
    )

    # 返回所有节点
    return [
        micro_ros_agent_node,
        robot_state_publisher_node,
        rviz_node,
        nav2_launch,
        telemetry_node
    ]


def generate_launch_description():
    return LaunchDescription([
        # 参数：机器人模型（功能包名）
        DeclareLaunchArgument(
            name='robot_model',
            default_value='makerspet_loki',
            description='Robot description package name'
        ),

        # 参数：地图文件路径（用于导航定位）
        # DeclareLaunchArgument(
        #     name='map',
        #     default_value=os.path.join(
        #         get_package_share_path('kaiaai_gazebo'),
        #         'map',
        #         'living_room.yaml'
        #     ),
        #     description='Full path to an existing map file'
        # ),
        DeclareLaunchArgument(
            name='map',
            default_value=os.path.join(
                os.path.expanduser('~'),
                'map.yaml'
            ),
            description='Full path to an existing map file'
        ),


        # 参数：是否使用仿真时间（比如 gazebo）
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='false',
            choices=['true', 'false'],
            description='Use simulation (Gazebo) clock if true'
        ),

        # 参数：是否启用 SLAM（导航时建图）
        DeclareLaunchArgument(
            name='slam',
            default_value='False',
            choices=['True', 'False'],
            description='Navigate while creating a new map'
        ),
        DeclareLaunchArgument(
            'lidar_model',
            default_value='',
            description='Name of the lidar model (optional)'
        ),

        # 构造所有节点
        OpaqueFunction(function=make_nodes)
    ])
