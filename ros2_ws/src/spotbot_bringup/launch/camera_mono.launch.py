#!/usr/bin/env python3
"""
SpotBot — Camera monoculaire USB
Publie sur /camera/image_raw et /camera/camera_info
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    device_arg = DeclareLaunchArgument(
        'device', default_value='/dev/video0',
        description='Peripherique camera USB (ex: /dev/video0)'
    )
    framerate_arg = DeclareLaunchArgument(
        'framerate', default_value='30.0',
        description='FPS de la camera'
    )
    width_arg  = DeclareLaunchArgument('width',  default_value='640')
    height_arg = DeclareLaunchArgument('height', default_value='480')

    camera_node = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='usb_cam',
        namespace='camera',
        parameters=[{
            'video_device':   LaunchConfiguration('device'),
            'framerate':      LaunchConfiguration('framerate'),
            'image_width':    LaunchConfiguration('width'),
            'image_height':   LaunchConfiguration('height'),
            'pixel_format':   'yuyv2rgb',
            'camera_name':    'spotbot_cam',
            'camera_info_url': PathJoinSubstitution([
                FindPackageShare('spotbot_bringup'), 'config', 'camera_mono.yaml'
            ]),
            'frame_id': 'camera_link',
        }],
        remappings=[
            ('image_raw', '/camera/image_raw'),
            ('camera_info', '/camera/camera_info'),
        ],
        output='screen'
    )

    return LaunchDescription([
        device_arg, framerate_arg, width_arg, height_arg,
        camera_node
    ])
