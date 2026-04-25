from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import ThisLaunchFileDir
from launch.actions import ExecuteProcess



from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import (
    generate_move_group_launch,
    generate_moveit_rviz_launch,
)

def generate_launch_description():

    use_rviz = LaunchConfiguration('use_rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')

    moveit_config = MoveItConfigsBuilder("turtlebot3_manipulation", package_name="turtlebot3_manipulation_moveit_config").to_moveit_configs()

    rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Whether execute rviz2')

    sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Whether execute use_sim_time')    
    
    rviz_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([ThisLaunchFileDir(), '/moveit_rviz2.launch.py']),
            condition=IfCondition(use_rviz),
        )
    
    set_sim_time = ExecuteProcess(
            cmd=['ros2', 'param', 'set', '/move_group', 'use_sim_time', 'true'],
            output='screen',
            condition=IfCondition(use_sim_time),
        )
    
    ld = LaunchDescription()
    ld.add_action(rviz_arg)  
    ld.add_action(sim_time_arg)

    # MoveGroup (planning pipeline, controllers, etc.)
    ld.add_action(generate_move_group_launch(moveit_config))
    ld.add_action(rviz_launch)
    ld.add_action(set_sim_time)

    # Conditionally launch RViz with MoveIt panels and config
    # rviz_launch = generate_moveit_rviz_launch(moveit_config)
    # rviz_launch.condition = IfCondition(LaunchConfiguration("use_rviz"))
    # ld.add_action(rviz_launch)
    return ld