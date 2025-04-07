import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient, ActionServer
from nav2_msgs.action import NavigateToPose, FollowWaypoints, ComputePathToPose
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped

class Simple_Navigator(Node):
    def __init__(self):
        super().__init__('test_node')
        self.get_logger().info(f'     =====     Starting Test Node     =====     ')
        self.wp_client = ActionClient(self, FollowWaypoints, 'follow_waypoints')
        self.wp_client.wait_for_server()
        self.goal_msg = FollowWaypoints.Goal()
        self.goal_handle = None
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.set_waypoints()
        self.send_goals()

    def set_waypoints(self):
        goal_poses = []
        goal_pose1 = PoseStamped()
        goal_pose1.header.frame_id = 'map'
        goal_pose1.header.stamp = self.get_clock().now().to_msg()
        goal_pose1.pose.position.x = 0.35
        goal_pose1.pose.position.y = 2.0
        goal_pose1.pose.orientation.w = 0.707
        goal_pose1.pose.orientation.z = 0.707
        goal_poses.append(goal_pose1)

        # additional goals can be appended
        goal_pose2 = PoseStamped()
        goal_pose2.header.frame_id = 'map'
        goal_pose2.header.stamp = self.get_clock().now().to_msg()
        goal_pose2.pose.position.x = 2.75
        goal_pose2.pose.position.y = 2.0
        goal_pose2.pose.orientation.w = 0.0
        goal_pose2.pose.orientation.z = -1.0
        goal_poses.append(goal_pose2)

        goal_pose3 = PoseStamped()
        goal_pose3.header.frame_id = 'map'
        goal_pose3.header.stamp = self.get_clock().now().to_msg()
        goal_pose3.pose.position.x = 3.0
        goal_pose3.pose.position.y = 1.0
        goal_pose3.pose.orientation.w = 0.707
        goal_pose3.pose.orientation.z = -0.707
        goal_poses.append(goal_pose3)
        self.goal_msg.poses = goal_poses  # Replace waypoint_list with your list of PoseStamped messages        
        
    def feedbackCallback(self, msg):    
        #self.get_logger().info(f'FFFFeedback: {msg}')
        pass

    def timer_callback(self):
        status = 'None' 
        if not self.goal_handle is None:           
            result_future = self.goal_handle.get_result_async()   
            if not result_future.result() is None:
                status = result_future.result().status
        self.get_logger().info(f'FFFF result.status: {status}') 

    def send_goals(self):
        # Send the goal to the action server
        send_goal_future = self.wp_client.send_goal_async(self.goal_msg, self.feedbackCallback)
        rclpy.spin_until_future_complete(self, send_goal_future)
        self.goal_handle = send_goal_future.result()
        if self.goal_handle.accepted:
            self.get_logger().info(f'FFFF goal_handle.accepted')
        else:
            self.get_logger().info(f'FFFF goal_handle.NOT accepted')


def main(args=None):
    rclpy.init(args=args)
    sn_node = Simple_Navigator()
    rclpy.spin(sn_node)
    
    sn_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
    
        


    





'''




class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0
        self.follow_waypoints_client = ActionClient(self, FollowWaypoints, 'follow_waypoints')
        self.wp_client = ActionClient(self, 'follow_waypoints', FollowWaypoints)
        self.wp_client.wait_for_server()
        goal = FollowWaypoints.Goal()
        

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1

    def set_waypoints(self):    
        # set our demo's goal poses to follow
        goal_poses = []
        goal_pose1 = PoseStamped()
        goal_pose1.header.frame_id = 'map'
        goal_pose1.header.stamp = self.get_clock().now().to_msg()
        goal_pose1.pose.position.x = 1.0
        goal_pose1.pose.position.y = 1.0
        goal_pose1.pose.orientation.w = 1.0
        goal_pose1.pose.orientation.z = 0.0
        goal_poses.append(goal_pose1)

        # additional goals can be appended
        goal_pose2 = PoseStamped()
        goal_pose2.header.frame_id = 'map'
        goal_pose2.header.stamp = self.get_clock().now().to_msg()
        goal_pose2.pose.position.x = 1.0
        goal_pose2.pose.position.y = -6.0
        goal_pose2.pose.orientation.w = 0.707
        goal_pose2.pose.orientation.z = 0.707
        goal_poses.append(goal_pose2)

        goal_pose3 = PoseStamped()
        goal_pose3.header.frame_id = 'map'
        goal_pose3.header.stamp = self.get_clock().now().to_msg()
        goal_pose3.pose.position.x = -5.0
        goal_pose3.pose.position.y = 3.0
        goal_pose3.pose.orientation.w = 0.707
        goal_pose3.pose.orientation.z = 0.707
        goal_poses.append(goal_pose3)

def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()


'''