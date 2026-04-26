#!/usr/bin/env python3
"""
SpotBot — Description Launch (Robot State Publisher)
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    use_gui_arg = DeclareLaunchArgument(
        'use_gui', default_value='false',
        description='Lancer joint_state_publisher_gui'
    )

    urdf_path = PathJoinSubstitution([
        FindPackageShare('spotbot_description'), 'urdf', 'spotbot.urdf.xacro'
    ])

    robot_description = ParameterValue(
        Command(['xacro ', urdf_path]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen'
    )

    joint_state_pub = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )

    return LaunchDescription([
        use_gui_arg,
        robot_state_publisher,
        joint_state_pub,
    ])
