#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
import tf2_ros
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import Pose, Point, Quaternion
import numpy as np
from transforms3d.quaternions import qmult, qinverse, quat2mat, mat2quat
from transforms3d.euler import quat2euler, euler2quat


class OdomRepublisherNode(Node):
    """
    A ROS2 node that subscribes to an odometry topic, 
    republishes it to another topic, and broadcasts the pose as a TF transform.
    """
    
    def __init__(self):
        super().__init__('odom_republisher')
        
        # Declare parameters with default values
        self.declare_parameter('input_odom_topic', 'diff_drive_controller/odom')
        self.declare_parameter('output_odom_topic', 'odom')
        self.declare_parameter('parent_frame', 'odom')
        self.declare_parameter('child_frame', 'base_footprint')
        
        # Get parameter values
        self.input_topic = self.get_parameter('input_odom_topic').value
        self.output_topic = self.get_parameter('output_odom_topic').value
        self.parent_frame = self.get_parameter('parent_frame').value
        self.child_frame = self.get_parameter('child_frame').value
        
        # Create a subscriber to the input odometry topic
        self.subscription = self.create_subscription(
            Odometry,
            self.input_topic,
            self.odom_callback,
            10)
        
        # Create a publisher for the output odometry topic
        self.publisher = self.create_publisher(
            Odometry,
            self.output_topic,
            10)
        
        # Create a TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)
        
        self.get_logger().info(f"Started odometry republisher")
        self.get_logger().info(f"Input topic: {self.input_topic}")
        self.get_logger().info(f"Output topic: {self.output_topic}")
        self.get_logger().info(f"Broadcasting TF from {self.parent_frame} to {self.child_frame}")
        self.offset = None

    def subtract_poses(self, pose1, pose2):
        """
        Subtract pose2 from pose1 (pose1 - pose2)
        Returns the relative pose that would transform from pose2 to pose1
        """
        # Handle the position component (simple vector subtraction)
        result_position = Point()
        result_position.x = pose1.position.x - pose2.position.x
        result_position.y = pose1.position.y - pose2.position.y
        result_position.z = pose1.position.z - pose2.position.z
        
        # Handle the orientation component (quaternion operations)
        # Convert ROS2 quaternions to numpy arrays
        q1 = np.array([pose1.orientation.w, pose1.orientation.x, 
                    pose1.orientation.y, pose1.orientation.z])
        q2 = np.array([pose2.orientation.w, pose2.orientation.x, pose2.orientation.y, 
                    pose2.orientation.z])
        
        # Invert q2 and multiply: q1 * q2^-1
        q2_inv = qinverse([q2[0], q2[1], q2[2], q2[3]])  # Note: transforms3d uses wxyz order
        result_q = qmult([q1[0], q1[1], q1[2], q1[3]], q2_inv)
        
        # Convert back to ROS2 quaternion message
        result_orientation = Quaternion()
        result_orientation.x = result_q[1]
        result_orientation.y = result_q[2]
        result_orientation.z = result_q[3]
        result_orientation.w = result_q[0]
        
        # Create the result pose
        result_pose = Pose()
        result_pose.position = result_position
        result_pose.orientation = result_orientation
                # result_q = euler2quat(result_yaw, result_pitch, result_roll, 'sxyz')

        return result_pose
    

    def subtract_poses2(self, pose1, pose2):
        """
        Subtract pose2 from pose1 (pose1 - pose2)
        Returns the relative pose that would transform from pose2 to pose1
        """
        # Handle the position component (simple vector subtraction)
        result_position = Point()
        result_position.x = pose1.position.x - pose2.position.x
        result_position.y = pose1.position.y - pose2.position.y
        result_position.z = pose1.position.z - pose2.position.z
        
        # Convert quaternions to rotation matrices
        q1 = [pose1.orientation.x, pose1.orientation.y, pose1.orientation.z, pose1.orientation.w]
        q2 = [pose2.orientation.x, pose2.orientation.y, pose2.orientation.z, pose2.orientation.w]
        
        mat1 = quat2mat(q1)
        mat2 = quat2mat(q2)
        
        # Calculate the relative rotation matrix: R_rel = R1 * R2^T
        mat2_inv = np.transpose(mat2)
        result_mat = np.dot(mat1, mat2_inv)
        
        # Convert the result back to quaternion
        result_q = mat2quat(result_mat)
        
        # Create the result pose
        result_pose = Pose()
        result_pose.position = result_position
        result_pose.orientation = Quaternion(
            x=result_q[1], 
            y=result_q[2], 
            z=result_q[3],
            w=result_q[0], 
        )
        
        return result_pose

    def subtract_poses3(self, pose1, pose2):
        """
        Subtract pose2 from pose1 (pose1 - pose2)
        Returns the relative pose that would transform from pose2 to pose1
        """
        # Handle the position component (simple vector subtraction)
        result_position = Point()
        result_position.x = pose1.position.x - pose2.position.x
        result_position.y = pose1.position.y - pose2.position.y
        result_position.z = pose1.position.z - pose2.position.z
        
        # Convert quaternions to rotation matrices
        q1 = [pose1.orientation.w, pose1.orientation.x, pose1.orientation.y, pose1.orientation.z]
        q2 = [pose2.orientation.w, pose2.orientation.x, pose2.orientation.y, pose2.orientation.z]
        
        # Convert quaternion to Euler angles (roll, pitch, yaw)
        # transforms3d uses XYZW order, ROS 2 uses XYZW order too
        pose1_euler = quat2euler(q1, 'sxyz')
        pose2_euler = quat2euler(q2, 'sxyz')
        
        result_roll = pose1_euler[0] - pose2_euler[0]
        result_pitch = pose1_euler[1] - pose2_euler[1]
        result_yaw = pose1_euler[2] - pose2_euler[2]
        poseF_euler = (result_roll,result_pitch,result_yaw)

        # self.get_logger().info(f"\n\tpose1_euler: {pose1_euler} radians \
        #                          \n\tpose2_euler: {pose2_euler} radians \
        #                          \n\tposeF_euler: {poseF_euler} radians")

        result_q = euler2quat(result_roll, result_pitch, result_yaw, 'sxyz')

        
        # Create the result pose
        result_pose = Pose()
        result_pose.position = result_position
        result_pose.orientation = Quaternion(
            x=result_q[1], 
            y=result_q[2], 
            z=result_q[3],
            w=result_q[0], 
        )
        
        return result_pose
    
    def odom_callback(self, msg: Odometry):
        """
        Callback function for the odometry subscription.
        Republishes the odometry message and broadcasts the transform.
        
        Args:
            msg: The incoming Odometry message
        """
        if not self.offset:
            self.offset = msg.pose.pose
            self.get_logger().info(f"\nUSING ODOM OFFEST: \n\tPose: {self.offset.position}\n\tRotation:{self.offset.orientation}")

        odom_out_msg = msg

        odom_out_msg.pose.pose = self.subtract_poses(msg.pose.pose, self.offset)

        # Republish the odometry message
        self.publisher.publish(odom_out_msg)
        
        # Create and broadcast the transform
        transform = TransformStamped()
        
        # Set header information
        transform.header.stamp = odom_out_msg.header.stamp
        transform.header.frame_id = self.parent_frame
        
        # Set child frame
        transform.child_frame_id = self.child_frame
        
        # Set translation
        transform.transform.translation.x = odom_out_msg.pose.pose.position.x
        transform.transform.translation.y = odom_out_msg.pose.pose.position.y
        transform.transform.translation.z = odom_out_msg.pose.pose.position.z
        
        # Set rotation
        transform.transform.rotation = odom_out_msg.pose.pose.orientation
        
        # Broadcast the transforms
        self.tf_broadcaster.sendTransform(transform)


def main(args=None):
    rclpy.init(args=args)
    
    node = OdomRepublisherNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()