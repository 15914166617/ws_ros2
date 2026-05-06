
# //静态建图完成优化版
import os
from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import UnlessCondition
from launch.substitutions import LaunchConfiguration, Command
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def make_nodes(context, robot_model, use_sim_time, configuration_basename):
    """
    核心计算节点：在传感器数据流稳定后启动
    """
    robot_model_str = context.perform_substitution(robot_model)
    use_sim_time_str = context.perform_substitution(use_sim_time)
    configuration_basename_str = context.perform_substitution(configuration_basename)

    description_pkg = get_package_share_path(robot_model_str)
    
    # 路径解析
    urdf_path = os.path.join(description_pkg, 'urdf', 'robot.urdf.xacro')
    carto_config_dir = os.path.join(description_pkg, 'config')
    rviz_cfg = os.path.join(description_pkg, 'rviz', 'cartographer.rviz')

    # 模型描述
    robot_description = ParameterValue(
        Command(['xacro ', urdf_path]),
        value_type=str
    )

    return [
        # 1. 机器人状态发布：发布静态 TF
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description, 'use_sim_time': False}]
        ),

        # 2. Cartographer 核心：此时 /scan 应已稳定
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
        ),

        # 3. RViz2：界面最后开启
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', rviz_cfg],
            parameters=[{'use_sim_time': use_sim_time_str.lower() == 'true'}],
        )
    ]


def generate_launch_description():
    # 获取包路径
    loki_pkg = get_package_share_path('makerspet_loki')

    # 参数声明
    declared_arguments = [
        DeclareLaunchArgument('robot_model', default_value='makerspet_loki'),
        DeclareLaunchArgument('configuration_basename', default_value='cartographer_lds_2d.lua'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('resolution', default_value='0.05'),
        DeclareLaunchArgument('publish_period_sec', default_value='1.0'), # 缩短发布周期
        DeclareLaunchArgument('gui', default_value='false'),
    ]

    # --- 阶段 A: 基础通信 (立即启动) ---
    micro_ros_agent = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        name='micro_ros_agent',
        output='screen',
        arguments=['udp4', '--port', '8888', '-b', '8192']
    )

    # --- 阶段 B: 滤波定位 (延迟 1 秒) ---
    # 让 Agent 先启动握手，随后开启 EKF 建立 odom -> base_link
    ekf_node = TimerAction(
        period=1.0,
        actions=[
            Node(
                package='robot_localization',
                executable='ekf_node',
                name='ekf_filter_node',
                output='screen',
                parameters=[os.path.join(loki_pkg, 'config', 'ekf.yaml')]
            )
        ]
    )

    # --- 阶段 C: 地图栅格生成 (跟随定位启动) ---
    occupancy_grid = TimerAction(
        period=2.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    os.path.join(get_package_share_path('kaiaai_bringup'), 'launch', 'occupancy_grid.launch.py')
                ]),
                launch_arguments={
                    'use_sim_time': LaunchConfiguration('use_sim_time'),
                    'resolution': LaunchConfiguration('resolution'),
                    'publish_period_sec': LaunchConfiguration('publish_period_sec')
                }.items(),
            )
        ]
    )

    # --- 阶段 D: 核心计算与 UI (延迟 5 秒) ---
    # 模拟手动延时逻辑，确保此时传感器频率正常，TF 无断裂
    core_nodes = TimerAction(
        period=5.0,
        actions=[
            OpaqueFunction(
                function=make_nodes,
                args=[
                    LaunchConfiguration('robot_model'),
                    LaunchConfiguration('use_sim_time'),
                    LaunchConfiguration('configuration_basename'),
                ]
            )
        ]
    )

    ld = LaunchDescription()
    for arg in declared_arguments:
        ld.add_action(arg)
    
    ld.add_action(micro_ros_agent)
    ld.add_action(ekf_node)
    ld.add_action(occupancy_grid)
    ld.add_action(core_nodes)

    return ld

# # //静态建图完成
# import os
# from ament_index_python.packages import get_package_share_path

# from launch import LaunchDescription
# from launch.actions import (
#     DeclareLaunchArgument,
#     OpaqueFunction,
#     IncludeLaunchDescription,
#     TimerAction,  # 新增：用于延迟控制
# )
# from launch.conditions import UnlessCondition
# from launch.substitutions import (
#     LaunchConfiguration,
#     Command,
#     ThisLaunchFileDir,
# )
# from launch.launch_description_sources import PythonLaunchDescriptionSource

# from launch_ros.actions import Node
# from launch_ros.parameter_descriptions import ParameterValue

# # -------------------------------
# # 核心计算节点 (延迟启动的部分)
# # -------------------------------
# def make_nodes(context,
#                robot_model,
#                use_sim_time,
#                configuration_basename,
#                lidar_model):

#     robot_model_str = context.perform_substitution(robot_model)
#     use_sim_time_str = context.perform_substitution(use_sim_time)
#     configuration_basename_str = context.perform_substitution(configuration_basename)

#     description_pkg = get_package_share_path(robot_model_str)
    
#     # URDF 配置
#     urdf_path = os.path.join(description_pkg, 'urdf', 'robot.urdf.xacro')
#     robot_description = ParameterValue(
#         Command(['xacro ', urdf_path]),
#         value_type=str
#     )

#     carto_config_dir = os.path.join(description_pkg, 'config')
#     rviz_cfg = os.path.join(description_pkg, 'rviz', 'cartographer.rviz')

#     nodes = []

#     # 1. robot_state_publisher 
#     nodes.append(
#         Node(
#             package='robot_state_publisher',
#             executable='robot_state_publisher',
#             output='screen',
#             parameters=[{'robot_description': robot_description}]
#         )
#     )

#     # 2. joint_state_publisher
#     nodes.append(
#         Node(
#             package='joint_state_publisher',
#             executable='joint_state_publisher',
#             condition=UnlessCondition(LaunchConfiguration('gui'))
#         )
#     )

#     # 3. Cartographer 核心节点
#     nodes.append(
#         Node(
#             package='cartographer_ros',
#             executable='cartographer_node',
#             name='cartographer_node',
#             output='screen',
#             parameters=[{'use_sim_time': use_sim_time_str.lower() == 'true'}],
#             arguments=[
#                 '-configuration_directory', carto_config_dir,
#                 '-configuration_basename', configuration_basename_str
#             ]
#         )
#     )

#     # 4. 可视化 RViz
#     nodes.append(
#         Node(
#             package='rviz2',
#             executable='rviz2',
#             output='screen',
#             arguments=['-d', rviz_cfg],
#             parameters=[{'use_sim_time': use_sim_time_str.lower() == 'true'}],
#         )
#     )

#     return nodes


# def generate_launch_description():
#     # 参数声明
#     declared_arguments = [
#         DeclareLaunchArgument('robot_model', description='机器人描述包名称'),
#         DeclareLaunchArgument('configuration_basename', default_value='cartographer_lds_2d.lua'),
#         DeclareLaunchArgument('use_sim_time', default_value='false'),
#         DeclareLaunchArgument('resolution', default_value='0.05'),
#         DeclareLaunchArgument('publish_period_sec', default_value='3.0'),
#         DeclareLaunchArgument('lidar_model', default_value=''),
#         DeclareLaunchArgument('gui', default_value='false'),
#     ]

#     # A. 基础通信层：micro-ROS Agent (立即启动)
#     micro_ros_agent = Node(
#         package='micro_ros_agent',
#         executable='micro_ros_agent',
#         name='micro_ros_agent',
#         output='screen',
#         arguments=[
#             'udp4', 
#             '--port', '8888', 
#             '-b', '8192'  # 关键：加大缓冲区防止丢包
#         ]
#     )

#     # B. 滤波定位层：EKF (立即启动，为 SLAM 提供地基)
#     ekf_config_path = os.path.join(
#         get_package_share_path('makerspet_loki'),
#         'config',
#         'ekf.yaml'
#     )
#     ekf_node = Node(
#         package='robot_localization',
#         executable='ekf_node',
#         name='ekf_filter_node',
#         output='screen',
#         parameters=[ekf_config_path]
#     )

#     # C. 栅格地图生成器 (跟随基础层启动)
#     occupancy_grid = IncludeLaunchDescription(
#         PythonLaunchDescriptionSource([
#             os.path.join(get_package_share_path('kaiaai_bringup'), 'launch', 'occupancy_grid.launch.py')
#         ]),
#         launch_arguments={
#             'use_sim_time': LaunchConfiguration('use_sim_time'),
#             'resolution': LaunchConfiguration('resolution'),
#             'publish_period_sec': LaunchConfiguration('publish_period_sec')
#         }.items(),
#     )

#     # D. 核心计算层：延迟 5 秒执行 (确保 TF 和通信已就绪)
#     core_nodes_timer = TimerAction(
#         period=5.0,
#         actions=[
#             OpaqueFunction(
#                 function=make_nodes,
#                 args=[
#                     LaunchConfiguration('robot_model'),
#                     LaunchConfiguration('use_sim_time'),
#                     LaunchConfiguration('configuration_basename'),
#                     LaunchConfiguration('lidar_model'),
#                 ]
#             )
#         ]
#     )

#     # 构建启动描述
#     ld = LaunchDescription()
#     for arg in declared_arguments:
#         ld.add_action(arg)
    
#     ld.add_action(micro_ros_agent)
#     ld.add_action(ekf_node)
#     ld.add_action(occupancy_grid)
#     ld.add_action(core_nodes_timer)

#     return ld




# # 建图，基础建图
# # 单纯的手动建图，好控制，建图参数高
# # 静态导航
# # 修改了下位机函数接收函数，odom转tf现在使用官方节点
# import os

# from ament_index_python.packages import get_package_share_path

# from launch import LaunchDescription, LaunchContext
# from launch.actions import (
#     DeclareLaunchArgument,
#     OpaqueFunction,
#     IncludeLaunchDescription,
# )
# from launch.conditions import IfCondition, UnlessCondition
# from launch.substitutions import (
#     LaunchConfiguration,
#     Command,
#     ThisLaunchFileDir,
# )
# from launch.launch_description_sources import PythonLaunchDescriptionSource

# from launch_ros.actions import Node
# from launch_ros.parameter_descriptions import ParameterValue


# # -------------------------------
# # robot_description + SLAM nodes
# # -------------------------------
# def make_nodes(context: LaunchContext,
#                robot_model,
#                use_sim_time,
#                configuration_basename,
#                lidar_model):

#     robot_model_str = context.perform_substitution(robot_model)
#     use_sim_time_str = context.perform_substitution(use_sim_time)
#     configuration_basename_str = context.perform_substitution(configuration_basename)
#     lidar_model_str = context.perform_substitution(lidar_model)

#     description_pkg = get_package_share_path(robot_model_str)
#     telem_pkg = get_package_share_path('kaiaai_telemetry')

#     # URDF
#     urdf_path = os.path.join(
#         description_pkg,
#         'urdf',
#         'robot.urdf.xacro'
#     )

#     robot_description = ParameterValue(
#         Command(['xacro ', urdf_path]),
#         value_type=str
#     )

#     # Cartographer
#     carto_config_dir = os.path.join(description_pkg, 'config')
#     rviz_cfg = os.path.join(description_pkg, 'rviz', 'cartographer.rviz')

#     # Telemetry
#     telem_cfg_base = os.path.join(telem_pkg, 'config', 'telem.yaml')
#     telem_cfg_override = os.path.join(description_pkg, 'config', 'telem.yaml')

#     print('Robot model         :', robot_model_str)
#     print('URDF                :', urdf_path)
#     print('Cartographer config :', carto_config_dir, configuration_basename_str)
#     ekf_config_path = os.path.join(
#         get_package_share_path('makerspet_loki'),
#         'config',
#         'ekf.yaml'
#     )
#     nodes = []

#     # robot_state_publisher（必须最早）
#     nodes.append(
#         Node(
#             package='robot_state_publisher',
#             executable='robot_state_publisher',
#             output='screen',
#             parameters=[{'robot_description': robot_description}]
#         )
#     )

#     # joint_state_publisher
#     nodes.append(
#         Node(
#             package='joint_state_publisher',
#             executable='joint_state_publisher',
#             condition=UnlessCondition(LaunchConfiguration('gui'))
#         )
#     )

#     nodes.append(   
#         Node(
#             package='robot_localization',
#             executable='ekf_node',
#             name='ekf_filter_node',
#             output='screen',
#             parameters=[ekf_config_path]
#         ),
#     )
#     # nodes.append(
#     #     Node(
#     #         package='joint_state_publisher_gui',
#     #         executable='joint_state_publisher_gui',
#     #         condition=IfCondition(LaunchConfiguration('gui'))
#     #     )
#     # )

#     # telemetry
#     # nodes.append(
#     #     Node(
#     #         package='kaiaai_telemetry',
#     #         executable='telem',
#     #         output='screen',
#     #         parameters=(
#     #             [telem_cfg_base, telem_cfg_override,
#     #              {'laser_scan.lidar_model': lidar_model_str}]
#     #             if lidar_model_str else
#     #             [telem_cfg_base, telem_cfg_override]
#     #         )
#     #     )
#     # )

#     # cartographer
#     nodes.append(
#         Node(
#             package='cartographer_ros',
#             executable='cartographer_node',
#             name='cartographer_node',
#             output='screen',
#             parameters=[{'use_sim_time': use_sim_time_str.lower() == 'true'}],
#             arguments=[
#                 '-configuration_directory', carto_config_dir,
#                 '-configuration_basename', configuration_basename_str
#             ]
#         )
#     )

#     # rviz
#     nodes.append(
#         Node(
#             package='rviz2',
#             executable='rviz2',
#             output='screen',
#             arguments=['-d', rviz_cfg],
#             parameters=[{'use_sim_time': use_sim_time_str.lower() == 'true'}],
#         )
#     )

#     return nodes


# # -------------------------------
# # launch description
# # -------------------------------
# def generate_launch_description():

#     return LaunchDescription([

#         # ---------- launch args ----------
#         DeclareLaunchArgument(
#             'robot_model',
#             description='Robot description package name (REQUIRED)'
#         ),
#         DeclareLaunchArgument(
#             'configuration_basename',
#             default_value='cartographer_lds_2d.lua'
#         ),
#         DeclareLaunchArgument(
#             'use_sim_time',
#             default_value='false',
#             choices=['true', 'false']
#         ),
#         DeclareLaunchArgument(
#             'resolution',
#             default_value='0.05'# 地图精度5厘米 0.05
#         ),
#         DeclareLaunchArgument(
#             'publish_period_sec',
#             default_value='3.0'#发布频率3秒
#         ),
#         DeclareLaunchArgument(
#             'lidar_model',
#             default_value=''
#         ),
#         DeclareLaunchArgument(
#             'gui',
#             default_value='false'
#         ),

#         # ---------- micro-ROS agent ----------
#         # 为了确定是否真的是网络掉线，暂时吧这个功能分开执行
#         # Node(
#         #     package='micro_ros_agent',
#         #     executable='micro_ros_agent',
#         #     name='micro_ros_agent',
#         #     output='screen',
#         #     arguments=['udp4', '--port', '8888']
#         # ),
#         Node(
#             package='micro_ros_agent',
#             executable='micro_ros_agent',
#             name='micro_ros_agent',
#             output='screen',
#             # 这里的每一项都对应命令行中的一个空格后的参数
#             arguments=[
#                 'udp4', 
#                 '--port', '8888', 
#                 '-b', '8192'
#             ]
#         ),

#         # ---------- occupancy grid ----------
#         IncludeLaunchDescription(
#             PythonLaunchDescriptionSource([
#                 ThisLaunchFileDir(),
#                 '/occupancy_grid.launch.py'
#             ]),
#             launch_arguments={
#                 'use_sim_time': LaunchConfiguration('use_sim_time'),
#                 'resolution': LaunchConfiguration('resolution'),
#                 'publish_period_sec': LaunchConfiguration('publish_period_sec')
#             }.items(),
#         ),

#         # ---------- core nodes ----------
#         OpaqueFunction(
#             function=make_nodes,
#             args=[
#                 LaunchConfiguration('robot_model'),
#                 LaunchConfiguration('use_sim_time'),
#                 LaunchConfiguration('configuration_basename'),
#                 LaunchConfiguration('lidar_model'),
#             ]
#         ),
#     ])
# # 建图
# # ros2 launch kaiaai_bringup b5.launch.py   robot_model:=makerspet_loki   configuration_basename:=backpack_2d.lua
# # ros2 launch kaiaai_bringup b5.launch.py   robot_model:=makerspet_loki   configuration_basename:=cartographer_lds_2d.lua
# # 键盘控制
# # ros2 run kaiaai_teleop teleop_keyboard robot_model:=makerspet_loki
# # 地图保存
# # ros2 run nav2_map_server map_saver_cli -f ~/map --ros-args -p save_map_timeout:=60.0

# # colcon build --packages-select kaiaai_bringup
# # colcon build --packages-select makerspet_loki
# # 