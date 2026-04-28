#!/usr/bin/env python3
"""SpotBot — Camera monoculaire USB via v4l2_camera"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    device_arg = DeclareLaunchArgument(
        'device', default_value='/dev/video0',
        description='Peripherique camera USB'
    )
    width_arg = DeclareLaunchArgument('width', default_value='640')
    height_arg = DeclareLaunchArgument('height', default_value='480')

    camera_node = Node(
        package='v4l2_camera',
        executable='v4l2_camera_node',
        name='v4l2_camera',
        namespace='camera',
        parameters=[{
            'video_device': LaunchConfiguration('device'),
            'image_size': [640, 480],
            'pixel_format': 'YUYV',
            'camera_frame_id': 'camera_link',
        }],
        remappings=[
            ('image_raw', '/camera/image_raw'),
            ('camera_info', '/camera/camera_info'),
        ],
        output='screen'
    )

    return LaunchDescription([
        device_arg, width_arg, height_arg,
        camera_node
    ])
