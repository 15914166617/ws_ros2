# ros2 launch kaiaai_bringup b6.launch.py robot_model:=makerspet_loki slam:=True
# ros2 launch kaiaai_bringup b6.launch.py robot_model:=makerspet_loki map:=$HOME/map.yaml slam:=False

import os
from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction, # 引入延迟控制器
)
from launch.conditions import UnlessCondition
from launch.launch_context import LaunchContext
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.launch_description_sources import PythonLaunchDescriptionSource

def make_nodes(context: LaunchContext, robot_model, map_path, use_sim_time, slam, lidar_model, urdf_path):
    """
    我们将原本分散的节点整合在这里，方便统一受 TimerAction 控制
    """
    robot_model_str = context.perform_substitution(robot_model)
    use_sim_time_str = context.perform_substitution(use_sim_time)
    slam_bool = context.perform_substitution(slam).lower() == 'true'
    
    description_pkg = get_package_share_path(robot_model_str)
    
    # 1. 模型描述
    robot_description = ParameterValue(Command(['xacro ', urdf_path]), value_type=str)
    
    # 2. 根据状态选择参数文件 (b3/b6 逻辑)
    # if slam_bool:
    #     nav_params = os.path.join(description_pkg, 'config', 'nav2_slam_params.yaml')
    # else:
    #     nav_params = os.path.join(description_pkg, 'config', 'nav2_amcl_params.yaml')
    if slam_bool: # 重新启用根据slam_bool选择参数文件的逻辑         
        nav_params = os.path.join(description_pkg, 'config', 'navigation.yaml')
    else:
        nav_params = os.path.join(description_pkg, 'config', 'navigation.yaml')
        
    rviz_cfg = os.path.join(description_pkg, 'rviz', 'navigation.rviz')

    return [
        # 模型发布
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description, 'use_sim_time': True if use_sim_time_str == 'True' else False}],
            output='screen'
        ),
        
        # 关节发布
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            condition=UnlessCondition(LaunchConfiguration('gui'))
        ),

        # Nav2 Bringup (核心组件)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_path('nav2_bringup'), 'launch', 'bringup_launch.py')
            ),
            launch_arguments={
                'map': map_path,
                'use_sim_time': use_sim_time_str,
                'slam': str(slam_bool),
                'params_file': nav_params,
            }.items()
        ),

        # RViz (放在这里延迟启动可以防止启动初期渲染大量错误 TF)
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', rviz_cfg],
            parameters=[{'use_sim_time': True if use_sim_time_str == 'True' else False}]
        )
    ]

def generate_launch_description():
    # 获取路径
    default_loki_pkg = get_package_share_path('makerspet_loki')
    ekf_config_path = os.path.join(default_loki_pkg, 'config', 'ekf.yaml')

    return LaunchDescription([
        # ---------- 参数声明 ----------
        DeclareLaunchArgument('robot_model', default_value='makerspet_loki'),
        DeclareLaunchArgument('map', default_value=os.path.join(os.path.expanduser('~'), 'map.yaml')),
        DeclareLaunchArgument('use_sim_time', default_value='False'),
        DeclareLaunchArgument('slam', default_value='False'),
        DeclareLaunchArgument('lidar_model', default_value=''),
        DeclareLaunchArgument('gui', default_value='False'),
        DeclareLaunchArgument('urdf_path', default_value=os.path.join(default_loki_pkg, 'urdf', 'robot.urdf.xacro')),

        # ---------- 基础层 (立即启动) ----------
        # 1. micro-ROS Agent
        Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent',
            output='screen',
            arguments=['udp4', '--port', '8888', '-b', '8192']
        ),

        # 2. EKF 定位 (导航的根基)
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_config_path]
        ),

        # ---------- 应用层 (延迟 7 秒启动) ----------
        # 导航比建图更重，多给 2 秒缓冲
        TimerAction(
            period=7.0,
            actions=[
                OpaqueFunction(
                    function=make_nodes,
                    args=[
                        LaunchConfiguration('robot_model'),
                        LaunchConfiguration('map'),
                        LaunchConfiguration('use_sim_time'),
                        LaunchConfiguration('slam'),
                        LaunchConfiguration('lidar_model'),
                        LaunchConfiguration('urdf_path'),
                    ]
                )
            ]
        )
    ])

# # 基于b1得到的导航功能，可以设置使用静态或者动态
# # 基于b1进行修改，现在对slam参数赋予不同的初始值，会选择2个不同的配置文件，分别用于静态和动态导航，
# # （2中状态下，amcl和slam不会同时启动，同时，运动能力参数在2种工况下会不同，一个慢一个快，b1使用了同一套运动参数，在切换时需要频繁修改，所以有了b3）
# # nav2_slam.yaml
# # nav2_amcl.yaml
# # 基于b3得到b6 用于动态导航，主要是使用了新的odom转发tf节点
# # 启动指令
# # ros2 launch kaiaai_bringup b1.launch.py robot_model:=makerspet_loki slam:=True
# # ros2 launch kaiaai_bringup b1.launch.py robot_model:=makerspet_loki map:=$HOME/map.yaml slam:=False

# # colcon build --packages-select kaiaai_bringup makerspet_loki --symlink-install

# import os

# from launch import LaunchDescription
# from launch.actions import (
#     DeclareLaunchArgument,
#     IncludeLaunchDescription,
#     OpaqueFunction,
# )
# from launch.conditions import IfCondition, UnlessCondition
# from launch.launch_context import LaunchContext
# from launch.substitutions import LaunchConfiguration, Command
# from launch_ros.actions import Node
# from launch_ros.parameter_descriptions import ParameterValue
# from launch.launch_description_sources import PythonLaunchDescriptionSource

# from ament_index_python.packages import get_package_share_path


# def make_robot_description(context: LaunchContext, urdf_path):
#     """生成 robot_description 并启动 robot_state_publisher"""
#     robot_description = ParameterValue(
#         Command(['xacro ', urdf_path]),
#         value_type=str
#     )

#     return [
#         Node(
#             package='robot_state_publisher',
#             executable='robot_state_publisher',
#             parameters=[{'robot_description': robot_description}],
#             output='screen'
#         )
#     ]

# def make_runtime_nodes(context: LaunchContext,
#                        robot_model, map_, use_sim_time, slam, lidar_model):
#     """启动 telemetry / Nav2 / RViz"""
#     robot_model_str = context.perform_substitution(robot_model)
#     map_path = context.perform_substitution(map_)
#     use_sim_time_str = context.perform_substitution(use_sim_time)
#     slam_str = context.perform_substitution(slam).lower() == 'true'  # True/False
#     lidar_model_str = context.perform_substitution(lidar_model)

#     description_pkg = get_package_share_path(robot_model_str)
#     # telem_pkg = get_package_share_path('kaiaai_telemetry')

#     # 根据 slam 参数选择不同的 nav2 配置文件
#     if slam_str:
#         nav_params = os.path.join(description_pkg, 'config', 'nav2_slam.yaml')
#     else:
#         nav_params = os.path.join(description_pkg, 'config', 'nav2_amcl.yaml')

#     rviz_cfg = os.path.join(description_pkg, 'rviz', 'navigation.rviz')

#     # telem_cfg_base = os.path.join(telem_pkg, 'config', 'telem.yaml')
#     telem_cfg_override = os.path.join(description_pkg, 'config', 'telem.yaml')

#     nodes = []



#     # Nav2 bringup
#     nodes.append(
#         IncludeLaunchDescription(
#             PythonLaunchDescriptionSource(
#                 os.path.join(
#                     get_package_share_path('nav2_bringup'),
#                     'launch',
#                     'bringup_launch.py'
#                 )
#             ),
#             launch_arguments={
#                 'map': map_path,
#                 'use_sim_time': use_sim_time_str,
#                 'slam': str(slam_str),  # 注意要传字符串
#                 'params_file': nav_params,
#             }.items()
#         )
#     )

#     # RViz
#     nodes.append(
#         Node(
#             package='rviz2',
#             executable='rviz2',
#             output='screen',
#             arguments=['-d', rviz_cfg],
#             parameters=[{'use_sim_time': use_sim_time_str.lower() == 'true'}]
#         )
#     )

#     return nodes


# def generate_launch_description():
#     """整合后的单文件 launch"""

#     # Launch 参数
#     robot_model = LaunchConfiguration('robot_model')
#     default_urdf = os.path.join(
#         get_package_share_path('makerspet_loki'),  # 可改为默认模型
#         'urdf',
#         'robot.urdf.xacro'
#     )
#     ekf_config_path = os.path.join(
#         get_package_share_path('makerspet_loki'),
#         'config',
#         'ekf.yaml'
#     )
#     return LaunchDescription([

#         # ---------- 全局 LaunchArgument ----------
#         DeclareLaunchArgument('robot_model', default_value='makerspet_loki'),
#         DeclareLaunchArgument(
#             'map',
#             default_value=os.path.join(
#                 os.path.expanduser('~'),
#                 'map.yaml'
#             )
#         ),
#         DeclareLaunchArgument('use_sim_time', default_value='False'),
#         # DeclareLaunchArgument('slam', default_value='False'),
#         DeclareLaunchArgument('slam', default_value='False'),
#         DeclareLaunchArgument('lidar_model', default_value=''),
#         DeclareLaunchArgument('gui', default_value='False'),
#         DeclareLaunchArgument('urdf_path', default_value=default_urdf),

#         # ---------- micro-ROS agent ---------
#         # A. 基础通信层：micro-ROS Agent (立即启动)
#         Node(
#             package='micro_ros_agent',
#             executable='micro_ros_agent',
#             name='micro_ros_agent',
#             output='screen',
#             arguments=[
#                 'udp4', 
#                 '--port', '8888', 
#                 '-b', '8192'  # 关键：加大缓冲区防止丢包
#             ]
#         ),
#         Node(
#             package='robot_localization',
#             executable='ekf_node',
#             name='ekf_filter_node',
#             output='screen',
#             parameters=[ekf_config_path]
#         ),

#         # ---------- robot_description ----------
#         OpaqueFunction(
#             function=make_robot_description,
#             args=[LaunchConfiguration('urdf_path')]
#         ),

#         # ---------- joint states ----------
#         Node(
#             package='joint_state_publisher',
#             executable='joint_state_publisher',
#             condition=UnlessCondition(LaunchConfiguration('gui'))
#         ),

#         # ---------- telemetry / nav / rviz ----------
#         OpaqueFunction(
#             function=make_runtime_nodes,
#             args=[
#                 robot_model,
#                 LaunchConfiguration('map'),
#                 LaunchConfiguration('use_sim_time'),
#                 LaunchConfiguration('slam'),
#                 LaunchConfiguration('lidar_model'),
#             ]
#         ),
#     ])





