from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import (
    generate_move_group_launch,
    generate_moveit_rviz_launch,
)

def generate_launch_description():
    # Toggle to start RViz
    use_rviz = DeclareLaunchArgument(
        "use_rviz",
        default_value="true",
        choices=["true", "false"],
        description="Start RViz with MoveIt config"
    )

    moveit_config = MoveItConfigsBuilder("turtlebot3_manipulation", package_name="turtlebot3_manipulation_moveit_config").to_moveit_configs()

    ld = LaunchDescription([use_rviz])

    # MoveGroup (planning pipeline, controllers, etc.)
    ld.add_action(generate_move_group_launch(moveit_config))

    # Conditionally launch RViz with MoveIt panels and config
    rviz_launch = generate_moveit_rviz_launch(moveit_config)
    rviz_launch.condition = IfCondition(LaunchConfiguration("use_rviz"))
    ld.add_action(rviz_launch)

    return ld