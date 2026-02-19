from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    package_name = 'fishbot_description'
    urdf_name = 'robot.urdf.xacro'

    # 使用 Command + PathJoinSubstitution 正确拼接
    robot_description = ParameterValue(
        Command(['xacro ', PathJoinSubstitution([FindPackageShare(package_name), 'urdf', urdf_name])]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )

    fishbot_bringup_node = Node(
        package='fishbot_bringup',
        executable='fishbot_bringup',
        name='fishbot_bringup',
        output='screen'
    )

    return LaunchDescription([
        joint_state_publisher_node,
        robot_state_publisher_node,
        fishbot_bringup_node
    ])
