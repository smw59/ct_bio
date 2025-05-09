#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
# from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np
from geometry_msgs.msg import Twist

class MySubscriber(Node):
    def __init__(self):
        super().__init__('my_subscriber')
        self.bridge = CvBridge()
        # add image_topic variable, change camera name 
        # image_sub = self.create_subscription(CompressedImage, 'camera/image', self.image_callback, 10)
        # get rid of image_transport

        self.subscription = self.create_subscription(
            CompressedImage, '/image_raw/compressed', self.image_callback, 10
        )

        self.twist_pub = self.create_publisher(Twist, 'servo_cmd_vel', 10)

        self.cv_image = None

        # Timer (30Hz)
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)

        self.get_logger().info('Image Subscriber node initialized.')

    def image_callback(self, msg):
        try:
            # self.cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            np_arr = np.frombuffer(msg.data, np.uint8)
            self.cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge Error: {e}')
            return

        # if self.cv_image.shape[1] > 60 and self.cv_image.shape[0] > 60:
        #     cv2.circle(self.cv_image, (50, 50), 10, (0, 255, 0), -1)

        # ArUco marker detection code commented out
        if self.cv_image is not None and self.cv_image.shape[1] > 60 and self.cv_image.shape[0] > 60:
            # Detect ArUco marker

            # Convert the image to grayscale
            gray = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)

            # Define the dictionary and parameters
            aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
            parameters = cv2.aruco.DetectorParameters_create()

            # Create the ArUco detector + detect the markers
            corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters) 


            if ids is not None:
                cv2.aruco.drawDetectedMarkers(self.cv_image, corners, ids) # draws detected markers on the image by marking corners and displaying id

                # Use the first detected marker
                marker_center = np.mean(corners[0][0], axis=0) # corner[0] is first marker and corner[0][0] is the 4 corner coordinates of the marker and mean takes the mean
                image_center = np.array([self.cv_image.shape[1] / 2, self.cv_image.shape[0] / 2]) # finds the center of the image
                
                displacement = marker_center - image_center

                # Draw direction vector
                cv2.arrowedLine(
                    self.cv_image,
                    tuple(image_center.astype(int)),
                    tuple(marker_center.astype(int)),
                    (255, 0, 0),
                    2
                )

                # Create and publish Twist message
                twist = Twist()
                scale = 0.002  # Tune this value
                twist.linear.x = displacement[1] * scale  # Vertical movement
                twist.linear.y = displacement[0] * scale  # Horizontal movement
                self.twist_pub.publish(twist)

                self.get_logger().info(f'Displacement vector: {displacement}')
            else:
                self.get_logger().info('No ArUco marker detected.')
        

    def timer_callback(self):
        if self.cv_image is not None:
            cv2.imshow('Processed Image', self.cv_image)
            cv2.waitKey(1)  

def main(args=None):
    rclpy.init(args=args)
    node = MySubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard Interrupt, shutting down.')
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()



# #!/usr/bin/env python3
# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import CompressedImage
# from cv_bridge import CvBridge, CvBridgeError
# import cv2
# import numpy as np
# from geometry_msgs.msg import Twist

# class MySubscriber(Node):
#     def __init__(self):
#         super().__init__('my_subscriber')
#         self.bridge = CvBridge()

#         # Direct subscription to the compressed image topic
#         self.image_sub = self.create_subscription(
#             CompressedImage,
#             '/image_raw/compressed',  # <-- Update this topic if needed
#             self.image_callback,
#             10
#         )

#         self.twist_pub = self.create_publisher(Twist, 'servo_cmd_vel', 10)
#         self.cv_image = None

#         # Timer (30Hz)
#         self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)

#         self.get_logger().info('Image Subscriber node initialized.')


#     def image_callback(self, msg):
#         try:
#             # Convert from CompressedImage to cv::Mat
#             np_arr = np.frombuffer(msg.data, np.uint8)
#             self.cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
#         except Exception as e:
#             self.get_logger().error(f"Image decode failed: {e}")
#             return

#         if self.cv_image is not None and self.cv_image.shape[1] > 60 and self.cv_image.shape[0] > 60:
#             cv2.circle(self.cv_image, (50, 50), 10, (0, 255, 0), -1)

#         # ArUco marker detection code commented out
#         """
#         aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
#         parameters = cv2.aruco.DetectorParameters_create()
#         corners, ids, _ = cv2.aruco.detectMarkers(self.cv_image, aruco_dict, parameters=parameters)
#         if ids is not None:
#             cv2.aruco.drawDetectedMarkers(self.cv_image, corners, ids)
#             marker_center = np.mean(corners[0].reshape((4, 2)), axis=0)
#             image_center = np.array([cols / 2, rows / 2])
#             displacement = marker_center - image_center
#             cv2.arrowedLine(self.cv_image,
#                             (int(image_center[0]), int(image_center[1])),
#                             (int(marker_center[0]), int(marker_center[1])),
#                             (255, 0, 0), 2)
#             twist = Twist()
#             scale = 0.001
#             twist.linear.x = displacement[1] * scale
#             twist.linear.y = displacement[0] * scale
#             twist.angular.z = 0.0
#             self.twist_pub.publish(twist)
#             self.get_logger().info('Displacement vector: {}'.format(displacement))
#         """

#     def timer_callback(self):
#         if self.cv_image is not None:
#             cv2.imshow('Processed Image', self.cv_image)
#             cv2.waitKey(1)  

# def main(args=None):
#     rclpy.init(args=args)
#     node = MySubscriber()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         node.get_logger().info('Keyboard Interrupt, shutting down.')
#     finally:
#         node.destroy_node()
#         rclpy.shutdown()
#         cv2.destroyAllWindows()

# if __name__ == '__main__':
#     main()