# 可以选择加载地图，然后静态导航，也可以选择SLAM导航，slam启动后可以把动态获得的地图保存下来

# 静态导航
# ros2 launch kaiaai_bringup b4.launch.py robot_model:=makerspet_loki map:=$HOME/map.yaml
# ros2 launch kaiaai_bringup b4.launch.py   robot_model:=makerspet_loki   slam:=True
# 基础导航功能，基于吧b1,但是修改了下位机参数接受节点

# 基于b1改变了下位机数据的接受方式为官方里程计转tf的节点而不是自写代码
import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_context import LaunchContext
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_path


def make_robot_description(context: LaunchContext, urdf_path):
    """生成 robot_description 并启动 robot_state_publisher"""
    robot_description = ParameterValue(
        Command(['xacro ', urdf_path]),
        value_type=str
    )


    # return [
    #     Node(
    #         package='robot_state_publisher',
    #         executable='robot_state_publisher',
    #         parameters=[{'robot_description': robot_description}],
    #         output='screen'
    #     )
    # ]
    return [
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                name='robot_state_publisher',
                output='screen',
                parameters=[{
                    'robot_description': robot_description,
                    # 关键点：显式关闭仿真时间，强制同步系统时钟
                    'use_sim_time': False,
                    # 提高静态 TF 的发布频率（可选，默认 0.5Hz，通常足够）
                    'publish_frequency': 30.0 
                }]
            )
        ]

def make_runtime_nodes(context: LaunchContext,
                       robot_model, map_, use_sim_time, slam, lidar_model):
    """启动 telemetry / Nav2 / RViz"""
    robot_model_str = context.perform_substitution(robot_model)
    map_path = context.perform_substitution(map_)
    use_sim_time_str = context.perform_substitution(use_sim_time)
    slam_str = context.perform_substitution(slam)
    lidar_model_str = context.perform_substitution(lidar_model)

    description_pkg = get_package_share_path(robot_model_str)
    telem_pkg = get_package_share_path('kaiaai_telemetry')

    nav_params = os.path.join(description_pkg, 'config', 'navigation.yaml')
    rviz_cfg = os.path.join(description_pkg, 'rviz', 'navigation.rviz')

    telem_cfg_base = os.path.join(telem_pkg, 'config', 'telem.yaml')
    telem_cfg_override = os.path.join(description_pkg, 'config', 'telem.yaml')

    ekf_config_path = os.path.join(
        get_package_share_path('makerspet_loki'),
        'config',
        'ekf.yaml'
    )
    nodes = []
    nodes.append(   
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_config_path]
        ),
    )
    # telemetry 节点
    # nodes.append(
    #     Node(
    #         package='kaiaai_telemetry',
    #         executable='telem',
    #         output='screen',
    #         parameters=(
    #             [telem_cfg_base, telem_cfg_override,
    #              {'laser_scan.lidar_model': lidar_model_str}]
    #             if lidar_model_str else
    #             [telem_cfg_base, telem_cfg_override]
    #         )
    #     )
    # )

    # Nav2 bringup
    nodes.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_path('nav2_bringup'),
                    'launch',
                    'bringup_launch.py'
                )
            ),
            launch_arguments={
                'map': map_path,
                'use_sim_time': use_sim_time_str,
                'slam': slam_str,
                'params_file': nav_params,
            }.items()
        )
    )

    # RViz
    nodes.append(
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', rviz_cfg],
            parameters=[{'use_sim_time': use_sim_time_str.lower() == 'true'}]
        )
    )

    return nodes


def generate_launch_description():
    """整合后的单文件 launch"""

    # Launch 参数
    robot_model = LaunchConfiguration('robot_model')
    default_urdf = os.path.join(
        get_package_share_path('makerspet_loki'),  # 可改为默认模型
        'urdf',
        'robot.urdf.xacro'
    )
    # ekf_config_path = os.path.join(
    #     get_package_share_path('makerspet_loki'),
    #     'config',
    #     'ekf.yaml'
    # )

    return LaunchDescription([

        # ---------- 全局 LaunchArgument ----------
        DeclareLaunchArgument('robot_model', default_value='makerspet_loki'),
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(
                os.path.expanduser('~'),
                'map.yaml'
            )
        ),
        DeclareLaunchArgument('use_sim_time', default_value='False'),
        # DeclareLaunchArgument('slam', default_value='False'),
        DeclareLaunchArgument('slam', default_value='False'),
        DeclareLaunchArgument('lidar_model', default_value=''),
        DeclareLaunchArgument('gui', default_value='False'),
        DeclareLaunchArgument('urdf_path', default_value=default_urdf),

        # ---------- micro-ROS agent ----------
        Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent',
            output='screen',
            arguments=['udp4', '--port', '8888']
        ),

        # ---------- robot_description ----------
        OpaqueFunction(
            function=make_robot_description,
            args=[LaunchConfiguration('urdf_path')]
        ),

        # ---------- joint states ----------
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            condition=UnlessCondition(LaunchConfiguration('gui'))
        ),
        # Node(
        #     package='joint_state_publisher_gui',
        #     executable='joint_state_publisher_gui',
        #     condition=IfCondition(LaunchConfiguration('gui'))
        # ),


        # Node(
        #     package='robot_localization',
        #     executable='ekf_node',
        #     name='ekf_filter_node',
        #     output='screen',
        #     parameters=[ekf_config_path]
        # ),

        # ---------- telemetry / nav / rviz ----------
        OpaqueFunction(
            function=make_runtime_nodes,
            args=[
                robot_model,
                LaunchConfiguration('map'),
                LaunchConfiguration('use_sim_time'),
                LaunchConfiguration('slam'),
                LaunchConfiguration('lidar_model'),
            ]
        ),
    ])





