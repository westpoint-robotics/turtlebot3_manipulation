#!/usr/bin/env python3

import sys
import time
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from threading import Thread

# Import Gazebo-related libraries
try:
    import gz
    from gz.common import Image as GzImage
    from gz.math import Vector3d
    from gz.sim import Entity, EntityComponentManager, System, World
    from gz.transport import Node, Publisher, SubscriberOptions
except ImportError:
    print("ERROR: Gazebo libraries not found. Please install gz-python.")
    sys.exit(1)

# Import TensorFlow for object classification
try:
    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
except ImportError:
    print("ERROR: TensorFlow not found. Please install tensorflow.")
    sys.exit(1)

class ObjectClassifier:
    """Class for object classification using MobileNetV2."""
    
    def __init__(self):
        """Initialize the model for object classification."""
        print("Loading MobileNetV2 model...")
        self.model = MobileNetV2(weights='imagenet')
        print("Model loaded successfully!")
        
        # Warm up the model
        dummy_input = np.zeros((1, 224, 224, 3), dtype=np.float32)
        self.model.predict(dummy_input)
        
    def classify(self, image):
        """
        Classify objects in the image.
        
        Args:
            image: RGB image as numpy array of shape (height, width, 3)
            
        Returns:
            List of (class_name, description, probability) tuples
        """
        # Resize image to 224x224
        img = cv2.resize(image, (224, 224))
        
        # Convert to RGB if it's BGR
        if img.shape[-1] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Preprocess the image
        img = preprocess_input(np.expand_dims(img, axis=0))
        
        # Make prediction
        preds = self.model.predict(img)
        
        # Decode and return top 5 predictions
        return decode_predictions(preds, top=5)[0]

class GazeboVisionSystem:
    """System for processing camera data from Gazebo Sim Harmonic."""
    
    def __init__(self, camera_topic="/camera/image"):
        """
        Initialize the Gazebo vision system.
        
        Args:
            camera_topic: Topic of the camera to subscribe to
        """
        self.camera_topic = camera_topic
        self.node = Node()
        self.latest_image = None
        self.running = False
        self.classifier = ObjectClassifier()
        
        # Configure subscriber options
        self.sub_options = SubscriberOptions()
        self.sub_options.set_thread_count(1)
        
        print(f"Initializing Gazebo Vision System, listening on {camera_topic}")
    
    def start(self):
        """Start the vision system."""
        self.running = True
        
        # Subscribe to camera topic
        if not self.node.subscribe(self.camera_topic, self.on_image, self.sub_options):
            print(f"ERROR: Could not subscribe to {self.camera_topic}")
            return False
        
        print(f"Subscribed to {self.camera_topic}")
        
        # Start processing thread
        self.processing_thread = Thread(target=self.process_images)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        return True
    
    def stop(self):
        """Stop the vision system."""
        self.running = False
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join(timeout=1.0)
    
    def on_image(self, msg):
        """
        Callback for receiving images from Gazebo.
        
        Args:
            msg: The image message
        """
        # Convert Gazebo image to OpenCV format
        gz_img = GzImage()
        if not gz_img.from_msg(msg):
            print("ERROR: Failed to convert message to Gazebo image")
            return

        # Convert to numpy array
        width = gz_img.width()
        height = gz_img.height()
        
        if gz_img.pixel_format() == GzImage.PixelFormatType.RGB_INT8:
            img_data = np.frombuffer(gz_img.data(), dtype=np.uint8)
            img_data = img_data.reshape((height, width, 3))
        else:
            print(f"Unsupported pixel format: {gz_img.pixel_format()}")
            return
            
        self.latest_image = img_data
    
    def process_images(self):
        """Processing thread for continuous classification."""
        last_process_time = 0
        
        while self.running:
            current_time = time.time()
            
            # Process at most 10 times per second
            if current_time - last_process_time >= 0.1 and self.latest_image is not None:
                img = self.latest_image.copy()
                
                # Classify objects
                results = self.classifier.classify(img)
                
                # Display results
                self.display_results(img, results)
                
                last_process_time = current_time
            
            time.sleep(0.01)
    
    def display_results(self, image, classification_results):
        """
        Display the image with classification results.
        
        Args:
            image: The camera image
            classification_results: Results from the classifier
        """
        # Create a copy of the image for display
        display_img = image.copy()
        
        # Draw classification results on image
        y_pos = 30
        for idx, (class_id, class_name, probability) in enumerate(classification_results):
            text = f"{class_name}: {probability*100:.1f}%"
            cv2.putText(display_img, text, (10, y_pos), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            y_pos += 30
        
        # Display the image
        cv2.imshow("Gazebo Object Classification", display_img)
        cv2.waitKey(1)
        
        # Print top prediction to console
        top_class = classification_results[0]
        print(f"Top prediction: {top_class[1]} ({top_class[2]*100:.1f}%)")

def main():
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Object classification in Gazebo Sim Harmonic')
    parser.add_argument('--camera_topic', type=str, default='/camera/image',
                        help='Camera topic to subscribe to')
    args = parser.parse_args()
    
    # Initialize the vision system
    vision_system = GazeboVisionSystem(camera_topic=args.camera_topic)
    
    try:
        # Start the vision system
        if not vision_system.start():
            return 1
        
        print("Vision system running. Press Ctrl+C to exit.")
        
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nExiting...")
    
    finally:
        # Clean up
        vision_system.stop()
        cv2.destroyAllWindows()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())