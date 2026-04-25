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
# Author: Darby Lim

import os
import time

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch.substitutions import ThisLaunchFileDir

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition

def is_valid_to_launch():
    # Path includes model name of Raspberry Pi series
    path = '/sys/firmware/devicetree/base/model'
    if os.path.exists(path):
        return False
    else:
        return True

def generate_launch_description():
    if not is_valid_to_launch():
        print('Can not launch fake robot in Raspberry Pi')
        return LaunchDescription([])
    
    # current_unix_time = time.mktime(time.localtime())


    # Add the package resources to GZ environmental variables
    bringup_world_dir = os.path.join(get_package_share_directory('turtlebot3_manipulation_bringup'), 'worlds')
    bringup_model_dir = os.path.join(get_package_share_directory('turtlebot3_manipulation_bringup'), 'models')
    desc_mesh_dir = get_package_share_directory('turtlebot3_manipulation_description').rsplit('/',1)[0]
    desc_urdf_dir = os.path.join(get_package_share_directory('turtlebot3_manipulation_description'), 'urdf')
    # print(f'\n\t bringup_world_dir: {bringup_world_dir}\n\t desc_mesh_dir: {desc_mesh_dir}\n\t desc_urdf_dir: {desc_urdf_dir}\n')

    start_rviz = LaunchConfiguration('start_rviz')
    prefix = LaunchConfiguration('prefix')
    use_sim_time = LaunchConfiguration('use_sim_time')

    namespace = LaunchConfiguration('namespace')
    robot_name = LaunchConfiguration('robot_name')

    ros_gz_bridge_config = PathJoinSubstitution([
            FindPackageShare('turtlebot3_manipulation_bringup'),
            'config',
            'tb3_bridge.yaml',
        ])

    world = LaunchConfiguration(
        'world',
        default=PathJoinSubstitution(
            [
                FindPackageShare('turtlebot3_manipulation_bringup'),
                'worlds',
                # 'turtlebot3_world.model'
                'turtlebot3_maze.world'
            ]
        )
    )

    pose = {'x': LaunchConfiguration('x_pose', default='0.00'),
            'y': LaunchConfiguration('y_pose', default='0.00'),
            'z': LaunchConfiguration('z_pose', default='0.01'),
            'R': LaunchConfiguration('roll', default='0.00'),
            'P': LaunchConfiguration('pitch', default='0.00'),
            'Y': LaunchConfiguration('yaw', default='0.00')}

    return LaunchDescription([
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', bringup_world_dir),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', bringup_model_dir),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH',desc_mesh_dir),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH',desc_urdf_dir),

        DeclareLaunchArgument(
            'start_rviz',
            default_value='false',
            description='Whether execute rviz2'),

        DeclareLaunchArgument(
            'prefix',
            default_value='""',
            description='Prefix of the joint and link names'),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Start robot in Gazebo simulation.'),

        DeclareLaunchArgument(
            'world',
            default_value=world,
            description='Directory of gazebo world file'),

        DeclareLaunchArgument(
            'x_pose',
            default_value=pose['x'],
            description='position of turtlebot3'),

        DeclareLaunchArgument(
            'y_pose',
            default_value=pose['y'],
            description='position of turtlebot3'),

        DeclareLaunchArgument(
            'z_pose',
            default_value=pose['z'],
            description='position of turtlebot3'),

        DeclareLaunchArgument(
            'roll',
            default_value=pose['R'],
            description='orientation of turtlebot3'),

        DeclareLaunchArgument(
            'pitch',
            default_value=pose['P'],
            description='orientation of turtlebot3'),

        DeclareLaunchArgument(
            'yaw',
            default_value=pose['Y'],
            description='orientation of turtlebot3'),

        DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='Top-level namespace'),

        DeclareLaunchArgument(
            'robot_name',
            default_value='turtlebot3',
            description='name of the robot'),

        # If selected then start RVIZ
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([ThisLaunchFileDir(), '/base.launch.py']),
            launch_arguments={
                'start_rviz': start_rviz,
                'prefix': prefix,
                'use_sim': use_sim_time,
            }.items(),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([ThisLaunchFileDir(), '/joystick.launch.py']),
            launch_arguments={
                'prefix': prefix,
                'use_sim': use_sim_time,
            }.items(),
        ),

        # Start Gazebosim server
        IncludeLaunchDescription(PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare('ros_gz_sim'),
                    'launch',
                    'gz_sim.launch.py'])
            ]),
            launch_arguments={
                'gz_args': [f'-r -s -v1 ', world], 
                'use_sim': use_sim_time,
            }.items(),
            # launch_arguments={'gz_args': [f'-r -s -v1 --initial-sim-time {current_unix_time} ', world] }.items(),
        ),
            
        # Start Gazebosim client
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('ros_gz_sim'),
                            'launch',
                            'gz_sim.launch.py')
            ),
            launch_arguments={
                'gz_args': ['-g '],
                'use_sim': use_sim_time,
            }.items(),
        ),

        # Map Gazebo topics into ROS2
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='bridge_ros_gz',
            namespace=namespace,
            parameters=[{
                    'config_file': ros_gz_bridge_config,
                    'use_sim_time': use_sim_time,
            }],
            output='log',
        ),        

        # Bring Gazebo camera output into ROS2
        Node(
            package='ros_gz_image',
            executable='image_bridge',
            name='bridge_gz_ros_camera_image',
            namespace=namespace,
            output='log',
            parameters=[{
                'use_sim_time': use_sim_time,
            }],
            arguments=['/image_raw']
        ),

        # Spawn the TurtleBot3
        Node(
            package='ros_gz_sim',
            executable='create',
            namespace=namespace,
            output='log',
            arguments=[
                '-name', robot_name,
                '-topic', 'robot_description',
                '-x', pose['x'], '-y', pose['y'], '-z', pose['z'],
                '-R', pose['R'], '-P', pose['P'], '-Y', pose['Y']],
            parameters=[{'use_sim_time': use_sim_time}]
        )
    ])
