#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
import time
import sys
import os
import subprocess

class GazeboObjectRecognition(Node):
    """
    ROS2 node for object recognition in Gazebo simulation environment
    """
    def __init__(self):
        super().__init__('gazebo_object_recognition')
        
        # Parameters
        self.declare_parameter('camera_topic', '/camera/image')
        self.declare_parameter('detection_topic', '/object_detection')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('visualization', True)
        self.declare_parameter('visualization_topic', '/object_detection/visualization')
        
        # Get parameters
        camera_topic = self.get_parameter('camera_topic').value
        detection_topic = self.get_parameter('detection_topic').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.visualization = self.get_parameter('visualization').value
        visualization_topic = self.get_parameter('visualization_topic').value        
        # Create subscribers and publishers
        self.image_subscription = self.create_subscription(
            Image, 
            camera_topic, 
            self.image_callback,
            10)
        
        self.detection_publisher = self.create_publisher(
            Detection2DArray,
            detection_topic,
            10)
        
        if self.visualization:
            self.visualization_publisher = self.create_publisher(
                Image,
                visualization_topic,
                10)
        
        # CV Bridge and model
        self.bridge = CvBridge()
        self.get_logger().info('Loading MobileNetV2 model...')
        self.model = MobileNetV2(weights='imagenet')
        self.get_logger().info('Model loaded successfully!')
        
        # Processing stats
        self.frame_count = 0
        self.last_time = time.time()
        self.processing_fps = 0.0
        
        self.get_logger().info('Gazebo Object Recognition Node initialized')
    
    def image_callback(self, msg):
        """Process incoming image messages and perform object detection"""
        try:
            # Convert ROS Image message to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Prepare image for model
            input_image = cv2.resize(cv_image, (224, 224))
            input_tensor = preprocess_input(np.expand_dims(input_image, axis=0))
            
            # Run inference
            predictions = self.model.predict(input_tensor)
            results = decode_predictions(predictions, top=5)[0]
            for result in results:
                name, desc, score  = result
                print(f'RESULTS name: {name}, desc: {desc} score: {score}')
            detection_msg = Detection2DArray()
            
            # Createnamedimagenet_id, label, score) in enumerate(results):
            if score >= self.confidence_threshold:
                detection = Detection2D()
                detection.header = msg.header
                
                # Set detection results
                hypothesis = ObjectHypothesisWithPose()
                hypothesis.id = label
                hypothesis.score = float(score)
                detection.results.append(hypothesis)
                
                # Add to detection array
                detection_msg.detections.append(detection)
            
            # Publish detection results
            self.detection_publisher.publish(detection_msg)
            
            # Visualize if needed
            if self.visualization:
                # Create visualization image
                vis_image = cv_image.copy()
                
                # Draw detections
                font = cv2.FONT_HERSHEY_SIMPLEX
                y_pos = 30
                for i, (imagenet_id, label, score) in enumerate(results):
                    if score >= self.confidence_threshold:
                        text = f"{label}: {score:.2f}"
                        cv2.putText(vis_image, text, (10, y_pos), 
                                   font, 0.8, (0, 255, 0), 2)
                        y_pos += 30
                
                # Add FPS counter
                self.frame_count += 1
                if self.frame_count >= 10:
                    current_time = time.time()
                    self.processing_fps = self.frame_count / (current_time - self.last_time)
                    self.last_time = current_time
                    self.frame_count = 0
                
                cv2.putText(vis_image, f"FPS: {self.processing_fps:.1f}", 
                           (10, vis_image.shape[0] - 10), font, 0.8, (0, 255, 0), 2)
                
                # Publish visualization
                vis_msg = self.bridge.cv2_to_imgmsg(vis_image, encoding='bgr8')
                vis_msg.header = msg.header
                self.visualization_publisher.publish(vis_msg)
            
        except Exception as e:
            self.get_logger().error(f'Error processing image: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    
    node = GazeboObjectRecognition()
    print(f"Python sys.version: {sys.version}")
    print(f"WHICH PYTHON {subprocess.getoutput("which python3")}")
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt, shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()