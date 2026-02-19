# 启动rviz2
import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument
import inspect

# ros2 launch example_t1 rviz.launch.py  
# ros2 run teleop_twist_keyboard teleop_twist_keyboard

def generate_launch_description():

    print(f"node rviz star")
    print(f"File: {inspect.getfile(inspect.currentframe())}, Line: {inspect.currentframe().f_lineno}, Def: {inspect.currentframe().f_code.co_name}")

    ld = LaunchDescription()

    DL_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        # 如果希望调试是轮子能根据tf同步转动，启用这个
        default_value='true',
        # default_value='false',
        description='Use simulation (Gazebo) clock if true')

    LC_use_sim_time = LaunchConfiguration('use_sim_time')
    


    packageName = 'example_t1'
    packageDir = get_package_share_directory(packageName)

    # src/example_t1/rviz/myrviz.rviz
    rvizConfigName ='myrviz.rviz'
    rvizConfigFile = os.path.join(packageDir, 'rviz', rvizConfigName)



    # 启动节点rviz2
    node_rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='node_rviz2',
        arguments=['-d', rvizConfigFile],
        parameters=[{'use_sim_time': LC_use_sim_time}],
        output='screen',
    )
    
    
    ld.add_action(DL_use_sim_time)
    ld.add_action(node_rviz2)


    return ld