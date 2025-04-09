import math

from geometry_msgs.msg import Twist

import rclpy
from rclpy.node import Node

from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import numpy as np
import transforms3d

class FrameListener(Node):

    def __init__(self):
        super().__init__('turtle_tf2_frame_listener')
        self.get_logger().info(f'Starting TF2 FRame Listener')

        # Declare and acquire `target_frame` parameter
        self.target_frame = self.declare_parameter(
          'target_frame', 'turtle1').get_parameter_value().string_value

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Call on_timer function every second
        self.timer = self.create_timer(1.0, self.on_timer)

    def on_timer(self):
        # Store frame names in variables that will be used to
        # compute transformations
        from_frame_rel = 'odom'
        to_frame_rel = 'base_link'

        # Look up for the transformation between target_frame and turtle2 frames
        # and send velocity commands for turtle2 to reach target_frame
        try:
            t = self.tf_buffer.lookup_transform(
                to_frame_rel,
                from_frame_rel,
                rclpy.time.Time())
            
                    # Extract quaternion from the message
            quat = [t.transform.rotation.x,t.transform.rotation.y,t.transform.rotation.z,t.transform.rotation.w]
        
            # Convert quaternion to Euler angles (roll, pitch, yaw)
            # transforms3d uses XYZW order, ROS 2 uses XYZW order too
            euler = transforms3d.euler.quat2euler(quat, 'sxyz')
        
            # Convert to degrees for better readability
            euler_degrees = [np.degrees(angle) for angle in euler]
        
             # Print results
            # self.get_logger().info(f'Quaternion: [{quat[0]:.4f}, {quat[1]:.4f}, {quat[2]:.4f}, {quat[3]:.4f}]')
            # self.get_logger().info(f'Euler angles (rad): [{euler[0]:.4f}, {euler[1]:.4f}, {euler[2]:.4f}]')
            # self.get_logger().info(f'Euler angles (deg): [{euler_degrees[0]:.4f}, {euler_degrees[1]:.4f}, {euler_degrees[2]:.4f}]')


            self.get_logger().info(f'Transformed {to_frame_rel} to {from_frame_rel}: \
                                   \n\tTaranslation: {t.transform.translation.x:.4f}, {t.transform.translation.y:.4f} \
                                   \n\tEuler angles (deg): [{euler_degrees[0]:.4f}, {euler_degrees[1]:.4f}, {euler_degrees[2]:.4f}]')
            
        except TransformException as ex:
            self.get_logger().info(
                f'Could not transform {to_frame_rel} to {from_frame_rel}: {ex}')
            return

        # msg = Twist()
        # scale_rotation_rate = 1.0
        # msg.angular.z = scale_rotation_rate * math.atan2(
        #     t.transform.translation.y,
        #     t.transform.translation.x)

        # scale_forward_speed = 0.5
        # msg.linear.x = scale_forward_speed * math.sqrt(
        #     t.transform.translation.x ** 2 +
        #     t.transform.translation.y ** 2)

        # self.publisher.publish(msg)
           
def main():
    rclpy.init()
    node = FrameListener()
    node.get_logger().info(f'Starting TF2 FRame Listener2')
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()