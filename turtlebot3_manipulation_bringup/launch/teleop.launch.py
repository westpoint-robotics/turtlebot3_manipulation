import os

from ament_index_python.packages import get_package_share_directory

import launch
import launch_ros.actions
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    joy_config = launch.substitutions.LaunchConfiguration('joy_config')
    joy_dev = launch.substitutions.LaunchConfiguration('joy_dev')
    publish_stamped_twist = launch.substitutions.LaunchConfiguration('publish_stamped_twist')
    config_filepath = launch.substitutions.LaunchConfiguration('config_filepath')
    joymux_configs = launch.substitutions.LaunchConfiguration('joymux_configs')


    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument('joy_vel', default_value='cmd_vel'),
        launch.actions.DeclareLaunchArgument('joy_config', default_value='ps3'),
        launch.actions.DeclareLaunchArgument('joy_dev', default_value='0'),
        launch.actions.DeclareLaunchArgument('publish_stamped_twist', default_value='false'),
        launch.actions.DeclareLaunchArgument('config_filepath', default_value=[
            launch.substitutions.TextSubstitution(text=os.path.join(
                get_package_share_directory('teleop_twist_joy'), 'config', '')),
            joy_config, launch.substitutions.TextSubstitution(text='.config.yaml')]),

        launch.actions.DeclareLaunchArgument('joymux_configs', default_value=[
            PathJoinSubstitution([FindPackageShare('turtlebot3_manipulation_bringup'),
                'config',
                'twist_mux_config.yaml'])]),    

        launch_ros.actions.Node(
            package='joy', executable='joy_node', name='joy_node',
            arguments=['--ros-args', '--log-level', 'WARN'],
            parameters=[{
                'device_id': joy_dev,
                'deadzone': 0.3,
                'autorepeat_rate': 20.0,
            }, config_filepath]),
        launch_ros.actions.Node(
            package='teleop_twist_joy', executable='teleop_node',
            name='teleop_twist_joy_node',
            parameters=[config_filepath, {'publish_stamped_twist': publish_stamped_twist}],
            remappings={('/cmd_vel', launch.substitutions.LaunchConfiguration('joy_vel'))},
            arguments=['--ros-args', '--log-level', 'WARN'],
            ),
        launch_ros.actions.Node(
            package='twist_mux', executable='twist_mux',
            name='twist_mux',
            parameters=[config_filepath, {'use_stamped': publish_stamped_twist}],
            remappings=[('/cmd_vel_in', launch.substitutions.LaunchConfiguration('joy_vel')),
                        ('/cmd_vel_out', 'cmd_vel')],
            arguments=['--ros-args', '--log-level', 'WARN'],
            ),
    ])
