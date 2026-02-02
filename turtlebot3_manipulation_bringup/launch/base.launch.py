#!/usr/bin/env python3
#
# Copyright 2022 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Darby Lim, Hye-jong KIM

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import RegisterEventHandler
from launch.conditions import IfCondition
from launch.conditions import UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command
from launch.substitutions import FindExecutable
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import ThisLaunchFileDir
from launch.actions import IncludeLaunchDescription


from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(            
        DeclareLaunchArgument(
            'use_joy',
            default_value='True',
            description='Whether to start joystick control nodes'),
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            'start_rviz',
            default_value='false',
            description='Whether execute rviz2'
        )
    )


    declared_arguments.append(
        DeclareLaunchArgument(
            'prefix',
            default_value='""',
            description='Prefix of the joint and link names'
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            'use_sim',
            default_value='false',
            description='Start robot in Gazebo simulation.'
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            'use_fake_hardware',
            default_value='false',
            description='Start robot with fake hardware mirroring command to its states.'
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            'fake_sensor_commands',
            default_value='false',
            description='Enable fake command interfaces for sensors used for simple simulations. \
            Used only if "use_fake_hardware" parameter is true.'
        )
    )

    use_joy = LaunchConfiguration('use_joy')
    start_rviz = LaunchConfiguration('start_rviz')
    prefix = LaunchConfiguration('prefix')
    use_sim = LaunchConfiguration('use_sim')
    use_fake_hardware = LaunchConfiguration('use_fake_hardware')
    fake_sensor_commands = LaunchConfiguration('fake_sensor_commands')

    urdf_file = Command(
        [
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution(
                [
                    FindPackageShare('turtlebot3_manipulation_description'),
                    'urdf',
                    'turtlebot3_manipulation.urdf.xacro'
                ]
            ),
            ' ',
            'prefix:=',
            prefix,
            ' ',
            'use_sim:=',
            use_sim,
            ' ',
            'use_fake_hardware:=',
            use_fake_hardware,
            ' ',
            'fake_sensor_commands:=',
            fake_sensor_commands,
        ]
    )

    controller_manager_config = PathJoinSubstitution(
        [
            FindPackageShare('turtlebot3_manipulation_bringup'),
            'config',
            'hardware_controller_manager.yaml',
        ]
    )

    rviz_config_file = PathJoinSubstitution(
        [
            FindPackageShare('turtlebot3_manipulation_bringup'),
            'rviz',
            'turtlebot3_manipulation.rviz'
        ]
    )

    joy_config_file = PathJoinSubstitution(
        [
            FindPackageShare('turtlebot3_manipulation_bringup'),
            'config',
            'xbox.config.yaml'
        ]
    )

    control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': urdf_file},
            controller_manager_config
        ],
        output="both",
        condition=UnlessCondition(use_sim))

    robot_state_pub_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': urdf_file, 'use_sim_time': use_sim}],
        arguments=['--ros-args', '--log-level', 'INFO'],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_file, '--ros-args', '--log-level', 'INFO'],
        parameters=[{'use_sim_time': use_sim}],
        condition=IfCondition(start_rviz)
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager', 
                   '--ros-args', '--log-level', 'INFO'],
    )

    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '-c', '/controller_manager',
          "--controller-ros-args", "-r diff_drive_controller/cmd_vel:=cmd_vel -r diff_drive_controller/odom:=odom",
          '--ros-args', '--log-level', 'INFO'],       
        output='log',)

    imu_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['imu_broadcaster', '--ros-args', '--log-level', 'INFO'],
    )

    arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_controller', '--ros-args', '--log-level', 'INFO'],
    )

    gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_controller', '--ros-args', '--log-level', 'INFO'],
    )


    # Start robot teleop and if joystick selected enable joystick control
    teleop = IncludeLaunchDescription(PythonLaunchDescriptionSource(
        [ThisLaunchFileDir(), '/teleop.launch.py']),
        condition=IfCondition(use_joy),
        launch_arguments={'config_filepath': joy_config_file,
                        'joy_dev': '0',
                        'joy_vel': 'cmd_vel_teleop',
                    #   'joy_vel': 'cmd_vel',
                        'use_sim_time': use_sim,
                        'publish_stamped_twist': 'true',}.items())   

    delay_rviz_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[rviz_node],
        )
    )

    delay_diff_drive_controller_spawner_after_joint_state_broadcaster_spawner = \
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[diff_drive_controller_spawner],
            )
        )

    delay_imu_broadcaster_spawner_after_joint_state_broadcaster_spawner = \
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[imu_broadcaster_spawner],
            )
        )

    delay_arm_controller_spawner_after_joint_state_broadcaster_spawner = \
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[arm_controller_spawner],
            )
        )

    delay_gripper_controller_spawner_after_joint_state_broadcaster_spawner = \
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[gripper_controller_spawner],
            )
        )

    nodes = [
        control_node,
        robot_state_pub_node,
        joint_state_broadcaster_spawner,
        delay_rviz_after_joint_state_broadcaster_spawner,
        delay_diff_drive_controller_spawner_after_joint_state_broadcaster_spawner,
        delay_imu_broadcaster_spawner_after_joint_state_broadcaster_spawner,
        delay_arm_controller_spawner_after_joint_state_broadcaster_spawner,
        delay_gripper_controller_spawner_after_joint_state_broadcaster_spawner,
        teleop,
    ]

    return LaunchDescription(declared_arguments + nodes)
