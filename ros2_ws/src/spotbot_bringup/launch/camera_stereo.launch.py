#!/usr/bin/env python3
"""
SpotBot — Cameras stereo (2x USB cam)
Camera gauche: /dev/video0 -> /stereo/left/image_raw
Camera droite: /dev/video1 -> /stereo/right/image_raw
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    left_dev_arg  = DeclareLaunchArgument('left_device',  default_value='/dev/video0')
    right_dev_arg = DeclareLaunchArgument('right_device', default_value='/dev/video1')
    width_arg     = DeclareLaunchArgument('width',  default_value='640')
    height_arg    = DeclareLaunchArgument('height', default_value='480')
    fps_arg       = DeclareLaunchArgument('framerate', default_value='20.0')

    calib_left  = PathJoinSubstitution([
        FindPackageShare('spotbot_bringup'), 'config', 'camera_stereo_left.yaml'
    ])
    calib_right = PathJoinSubstitution([
        FindPackageShare('spotbot_bringup'), 'config', 'camera_stereo_right.yaml'
    ])

    cam_params_base = {
        'framerate':    LaunchConfiguration('framerate'),
        'image_width':  LaunchConfiguration('width'),
        'image_height': LaunchConfiguration('height'),
        'pixel_format': 'yuyv2rgb',
        'frame_id':     'camera_link',
    }

    left_cam = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='usb_cam_left',
        namespace='stereo/left',
        parameters=[{
            **cam_params_base,
            'video_device':    LaunchConfiguration('left_device'),
            'camera_name':     'spotbot_left',
            'camera_info_url': calib_left,
        }],
        output='screen'
    )

    right_cam = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='usb_cam_right',
        namespace='stereo/right',
        parameters=[{
            **cam_params_base,
            'video_device':    LaunchConfiguration('right_device'),
            'camera_name':     'spotbot_right',
            'camera_info_url': calib_right,
        }],
        output='screen'
    )

    # Stereo rectification
    stereo_proc = Node(
        package='stereo_image_proc',
        executable='stereo_image_proc',
        name='stereo_proc',
        namespace='stereo',
        parameters=[{'approximate_sync': True}],
        remappings=[
            ('left/image_raw',   '/stereo/left/image_raw'),
            ('left/camera_info', '/stereo/left/camera_info'),
            ('right/image_raw',  '/stereo/right/image_raw'),
            ('right/camera_info','/stereo/right/camera_info'),
        ],
        output='screen'
    )

    return LaunchDescription([
        left_dev_arg, right_dev_arg, width_arg, height_arg, fps_arg,
        left_cam, right_cam, stereo_proc
    ])
