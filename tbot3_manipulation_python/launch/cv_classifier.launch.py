#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    """Generate launch description for object recognition node"""
    
    # Launch arguments
    camera_topic_arg = DeclareLaunchArgument(
        'camera_topic',
        default_value='/camera/image_raw',
        description='Topic for camera image input'
    )
    
    confidence_threshold_arg = DeclareLaunchArgument(
        'confidence_threshold',
        default_value='0.5',
        description='Confidence threshold for object detection'
    )
    
    visualization_arg = DeclareLaunchArgument(
        'visualization',
        default_value='True',
        description='Enable visualization of detection results'
    )
    
    # Create node
    object_recognition_node = Node(
        package='tbot3_manipulation_python',
        executable='object_recognition_node',
        name='gazebo_object_recognition',
        parameters=[{
            'camera_topic': LaunchConfiguration('camera_topic'),
            'confidence_threshold': LaunchConfiguration('confidence_threshold'),
            'visualization': LaunchConfiguration('visualization'),
        }],
        output='screen'
    )
    
    return LaunchDescription([
        camera_topic_arg,
        confidence_threshold_arg,
        visualization_arg,
        object_recognition_node
    ])