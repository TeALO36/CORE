#!/usr/bin/env python3
"""SpotBot — Streaming launch file."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    cameras_arg  = DeclareLaunchArgument('cameras',     default_value='auto',
                                          description='auto | mono | stereo')
    alfa_arg     = DeclareLaunchArgument('prefer_alfa', default_value='true',
                                          description='Préférer Alfa si dispo')
    watchdog_arg = DeclareLaunchArgument('wifi_watchdog', default_value='true',
                                          description='Activer WiFi watchdog Alfa')
    rtsp_host_arg = DeclareLaunchArgument('rtsp_host', default_value='82.66.150.66')
    rtsp_port_arg = DeclareLaunchArgument('rtsp_port', default_value='8554')

    stream_node = Node(
        package='spotbot_streaming',
        executable='camera_stream_node',
        name='camera_stream',
        parameters=[{
            'cameras':           LaunchConfiguration('cameras'),
            'prefer_alfa':       LaunchConfiguration('prefer_alfa'),
            'remote_rtsp_host':  LaunchConfiguration('rtsp_host'),
            'remote_rtsp_port':  LaunchConfiguration('rtsp_port'),
        }],
        output='screen'
    )

    watchdog_node = Node(
        package='spotbot_streaming',
        executable='wifi_watchdog_node',
        name='wifi_watchdog',
        parameters=[{
            'signal_threshold': -70,
            'check_interval':    5.0,
            'enabled': True,
        }],
        condition=IfCondition(LaunchConfiguration('wifi_watchdog')),
        output='screen'
    )

    return LaunchDescription([
        cameras_arg, alfa_arg, watchdog_arg, rtsp_host_arg, rtsp_port_arg,
        stream_node,
        watchdog_node,
    ])
