from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("turtlebot3_manipulation", package_name="turtlebot3_manipulation_moveit_config").to_moveit_configs()
    return generate_move_group_launch(moveit_config)


# def generate_launch_description():
#     moveit_config = MoveItConfigsBuilder("turtlebot3_manipulation", package_name="ee484_manipulator").to_moveit_configs()
#     log_action1 = LogInfo(msg=['MMMVVV moveit_config is: ', moveit_config])
#     ld = generate_move_group_launch(moveit_config)
#     log_action2 = LogInfo(msg=['MMMGGG moveit_config is: ', mg_launch])
#     ld.add_action(log_action1)
#     ld.add_action(log_action2)
#     return ld