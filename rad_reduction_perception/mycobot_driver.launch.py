from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='mycobot_280',
            executable='mycobot_driver',
            name='mycobot_driver',
            output='screen',
            parameters=[{'serial_port': '/dev/ttyACM0'}],
        ),
    ])
