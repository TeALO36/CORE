#!/usr/bin/env python3
"""SpotBot motion launch."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    gait_arg = DeclareLaunchArgument('gait',      default_value='trot')
    freq_arg = DeclareLaunchArgument('gait_freq', default_value='1.0')
    rate_arg = DeclareLaunchArgument('update_rate', default_value='50.0')

    motion_node = Node(
        package='spotbot_motion',
        executable='motion_node.py',
        name='spotbot_motion',
        parameters=[{
            'gait':        LaunchConfiguration('gait'),
            'gait_freq':   LaunchConfiguration('gait_freq'),
            'update_rate': LaunchConfiguration('update_rate'),
            'max_speed':   0.3,
        }],
        output='screen'
    )

    return LaunchDescription([gait_arg, freq_arg, rate_arg, motion_node])
