#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped
from action_msgs.msg import GoalStatus
import sys
import math

"""
 Initial code created with Claude AI https://claude.ai using the prompt:
 write a ros2 nav2 action client for waypoint following with status feedback
"""

class WaypointFollowerClient(Node):
    """Action client for Nav2 waypoint following with status feedback."""

    def __init__(self):
        super().__init__('waypoint_follower_client')
        
        # Create a callback group that allows execution of callbacks in parallel without restrictions
        callback_group = ReentrantCallbackGroup()
        
        # Create an action client for FollowWaypoints action
        self.action_client = ActionClient(
            self,
            FollowWaypoints,
            'follow_waypoints',
            callback_group=callback_group
        )

        # Wait for the action server to become available
        self.get_logger().info('Waiting for follow_waypoints action server...')
        if not self.action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('Action server not available after waiting')
            sys.exit(1)
        self.get_logger().info('Action server available!')
        
        # Initialize waypoints list
        self.waypoints = []
        
    def create_pose(self, x, y, z=0.0, qx=0.0, qy=0.0, qz=0.0, qw=1.0):
        """Create a PoseStamped message."""
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.position.z = float(z)
        
        pose.pose.orientation.x = float(qx)
        pose.pose.orientation.y = float(qy)
        pose.pose.orientation.z = float(qz)
        pose.pose.orientation.w = float(qw)
        
        return pose
        
    def add_waypoint(self, x, y, z=0.0, qx=0.0, qy=0.0, qz=0.0, qw=1.0):
        """Add a waypoint to the list."""
        self.waypoints.append(self.create_pose(x, y, z, qx, qy, qz, qw))
        self.get_logger().info(f'Added waypoint at ({x}, {y})')
        
    def clear_waypoints(self):
        """Clear the waypoints list."""
        self.waypoints = []
        self.get_logger().info('Cleared all waypoints')
        
    def send_waypoints(self):
        """Send all waypoints to the action server."""
        if not self.waypoints:
            self.get_logger().warn('No waypoints to send')
            return
            
        self.get_logger().info(f'Sending {len(self.waypoints)} waypoints to follow')
        
        # Create action goal
        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = self.waypoints
        
        # Send goal and register callbacks
        self.action_client.wait_for_server()
        send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)
        
    def goal_response_callback(self, future):
        """Callback for when the goal is accepted or rejected."""
        goal_handle = future.result()
        
        if not goal_handle.accepted:
            self.get_logger().error('Goal was rejected by server')
            return
            
        self.get_logger().info('Goal accepted by server')
        
        # Get result
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.get_result_callback)
        
    def get_result_callback(self, future):
        """Callback for when the action is completed."""
        status = future.result().status
        result = future.result().result
        
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Navigation completed successfully!')
            if result.missed_waypoints:
                self.get_logger().warn(f'Missed waypoints: {result.missed_waypoints}')
            else:
                self.get_logger().info('All waypoints were reached')
        else:
            self.get_logger().error(f'Navigation failed with status: {status}')
        
    def feedback_callback(self, feedback_msg):
        """Callback for action feedback."""
        feedback = feedback_msg.feedback
        current_waypoint = feedback.current_waypoint
        
        # Calculate completion percentage
        total_waypoints = len(self.waypoints)
        if total_waypoints > 0:
            progress = (current_waypoint + 1) / total_waypoints * 100.0
            self.get_logger().info(f'Current waypoint: {current_waypoint+1}/{total_waypoints} ({progress:.1f}%)')
        else:
            self.get_logger().info(f'Current waypoint: {current_waypoint+1}')


def main():
    rclpy.init()
    
    client = WaypointFollowerClient()
    
    # Example usage: Create some waypoints
    client.add_waypoint(0.35, 2.0, 0.0, 0.0, 0.0, 0.707, 0.707)  # x=1.0, y=1.0
    client.add_waypoint(2.75, 2.0, 0.0, 0.0, 0.0, 0.707, -0.707)  # x=2.0, y=0.0
    client.add_waypoint(3.0, -1.0, 0.0, 0.0, 0.0, 0.707, -0.707)  # x=2.0, y=2.0
    client.add_waypoint(0.0, 0.0, 0.0, 0.0, 0.0, 0.707, 0.707)  # x=1.0, y=1.0

    # Send waypoints
    client.send_waypoints()
    
    # Spin to process callbacks
    rclpy.spin(client)
    
    # Clean up
    client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
