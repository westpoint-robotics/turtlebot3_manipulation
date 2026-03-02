# West Point Documentation in this section:

## What has been tested in Simulation
- Start the simulation:  
`ros2 launch turtlebot3_manipulation_bringup gazebo.launch.py`

- Options to run in simulation:

  1. Run NAV2 with a known map  
  `ros2 launch turtlebot3_manipulation_navigation2 navigation2_use_sim_time.launch.py slam:='False'`
      - After RVIZ opens, you need to set the initial pose using the "2d Pose Estimate" button
      - Then drop a goal to navigate toward with the "Nav2 Goal" button  

  2. Run NAV2 with SLAM (No known map)  
  `ros2 launch turtlebot3_manipulation_navigation2 navigation2_use_sim_time.launch.py use_slam:='True'`
      - After RVIZ opens, wait about 1 minute for initial map to be generated
      - Then drop a goal to navigate toward with the "Nav2 Goal" button

  3. Run example arm control code from git@github.com:westpoint-robotics/ee484_projects.git (Drives in circle and moves manipulator repeatedly between 4 poses):  
  `ros2 launch tbot3_manipulation_python test_joint_control.launch.py`

## What has been tested on Real Hardware
- On the Raspberry Pi5 bring up the Turtlebot:  
`ros2 launch turtlebot3_manipulation_bringup hardware.launch.py`

- Options to run on real hardware:

  1. Run NAV2 with SLAM with no known map (usually run on a remote computer to facilitate the useage of GUIs):  
`ros2 launch turtlebot3_navigation2  navigation2.launch.py slam:='False' use_sim_time:="False" use_rviz:="True"`

  2. Run NAV2 with a known map (usually run on a remote computer to facilitate the useage of GUIs):  
`ros2 launch turtlebot3_navigation2  navigation2.launch.py slam:='True' use_sim_time:="False" use_rviz:="True"`

  3. Run example arm control code from git@github.com:westpoint-robotics/ee484_projects.git  
(Drives in circle and moves manipulator repeatedly between 4 poses):  
`ros2 launch tbot3_manipulation_python test_joint_control.launch.py`

# TurtleBot3 with OpenMANIPULATOR
<img src="https://raw.githubusercontent.com/ROBOTIS-GIT/emanual/master/assets/images/platform/turtlebot3/manipulation/tb3_with_opm_logo.png" width="500">

<img src="https://raw.githubusercontent.com/ROBOTIS-GIT/emanual/master/assets/images/platform/turtlebot3/manipulation/hardware_setup.png" width="500">

- Active Branches: noetic, humble, jazzy, main(rolling)
- Legacy Branches: *-devel

## Open Source Projects Related to TurtleBot3 and OpenMANIPULATOR
- [turtlebot3](https://github.com/ROBOTIS-GIT/turtlebot3)
- [turtlebot3_msgs](https://github.com/ROBOTIS-GIT/turtlebot3_msgs)
- [turtlebot3_simulations](https://github.com/ROBOTIS-GIT/turtlebot3_simulations)
- [turtlebot3_manipulation](https://github.com/ROBOTIS-GIT/turtlebot3_manipulation)
- [turtlebot3_manipulation_simulations](https://github.com/ROBOTIS-GIT/turtlebot3_manipulation_simulations)
- [turtlebot3_applications](https://github.com/ROBOTIS-GIT/turtlebot3_applications)
- [turtlebot3_applications_msgs](https://github.com/ROBOTIS-GIT/turtlebot3_applications_msgs)
- [turtlebot3_machine_learning](https://github.com/ROBOTIS-GIT/turtlebot3_machine_learning)
- [turtlebot3_autorace](https://github.com/ROBOTIS-GIT/turtlebot3_autorace)
- [turtlebot3_home_service_challenge](https://github.com/ROBOTIS-GIT/turtlebot3_home_service_challenge)
- [hls_lfcd_lds_driver](https://github.com/ROBOTIS-GIT/hls_lfcd_lds_driver)
- [ld08_driver](https://github.com/ROBOTIS-GIT/ld08_driver)
- [open_manipulator](https://github.com/ROBOTIS-GIT/open_manipulator)
- [dynamixel_sdk](https://github.com/ROBOTIS-GIT/DynamixelSDK)
- [dynamixel_workbench](https://github.com/ROBOTIS-GIT/dynamixel-workbench)
- [OpenCR-Hardware](https://github.com/ROBOTIS-GIT/OpenCR-Hardware)
- [OpenCR](https://github.com/ROBOTIS-GIT/OpenCR)

## Documentation, Videos, and Community

### Official Documentation
- ⚙️ **[ROBOTIS DYNAMIXEL](https://dynamixel.com/)**
- 📚 **[ROBOTIS e-Manual for Dynamixel SDK](http://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/)**
- 📚 **[ROBOTIS e-Manual for TurtleBot3](http://turtlebot3.robotis.com/)**
- 📚 **[ROBOTIS e-Manual for OpenMANIPULATOR-X](https://emanual.robotis.com/docs/en/platform/openmanipulator_x/overview/)**

### Learning Resources
- 🎥 **[ROBOTIS YouTube Channel](https://www.youtube.com/@ROBOTISCHANNEL)**
- 🎥 **[ROBOTIS Open Source YouTube Channel](https://www.youtube.com/@ROBOTISOpenSourceTeam)**
- 🎥 **[ROBOTIS TurtleBot3 YouTube Playlist](https://www.youtube.com/playlist?list=PLRG6WP3c31_XI3wlvHlx2Mp8BYqgqDURU)**
- 🎥 **[ROBOTIS OpenMANIPULATOR YouTube Playlist](https://www.youtube.com/playlist?list=PLRG6WP3c31_WpEsB6_Rdt3KhiopXQlUkb)**

### Community & Support
- 💬 **[ROBOTIS Community Forum](https://forum.robotis.com/)**
- 💬 **[TurtleBot category from ROS Community](https://discourse.ros.org/c/turtlebot/)**
