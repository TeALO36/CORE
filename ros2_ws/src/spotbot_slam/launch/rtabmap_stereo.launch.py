#!/usr/bin/env python3
"""
SpotBot — V-SLAM Stereo avec rtabmap
Prerequis: stereo_image_proc tourne et publie:
  /stereo/left/image_rect_color
  /stereo/right/image_rect_color
  /stereo/disparity
  /stereo/left/camera_info

Lancement:
  ros2 launch spotbot_slam rtabmap_stereo.launch.py
  ros2 launch spotbot_slam rtabmap_stereo.launch.py localization:=true
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    loc_arg = DeclareLaunchArgument(
        'localization', default_value='false',
        description='Mode localisation seule: true | false'
    )
    use_imu_arg = DeclareLaunchArgument(
        'use_imu', default_value='true',
        description='Utiliser IMU: true | false'
    )
    database_arg = DeclareLaunchArgument(
        'database_path', default_value='~/.ros/spotbot_stereo_map.db',
        description='Chemin de la base rtabmap'
    )

    localization  = LaunchConfiguration('localization')
    use_imu       = LaunchConfiguration('use_imu')
    database_path = LaunchConfiguration('database_path')

    params_file = PathJoinSubstitution([
        FindPackageShare('spotbot_slam'), 'params', 'rtabmap_stereo.yaml'
    ])

    # ---- Filtre IMU ----
    imu_filter = Node(
        package='imu_filter_madgwick',
        executable='imu_filter_madgwick_node',
        name='imu_filter_stereo',
        parameters=[{'use_mag': False, 'publish_tf': False}],
        remappings=[
            ('imu/data_raw', '/imu/data_raw'),
            ('imu/data',     '/imu/data'),
        ],
        condition=IfCondition(use_imu),
        output='screen'
    )

    # ---- rtabmap stereo SLAM ----
    rtabmap_slam = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        parameters=[
            params_file,
            {
                'database_path':    database_path,
                'subscribe_stereo': True,
                'subscribe_depth':  False,
                'subscribe_rgb':    False,
                'frame_id':         'base_link',
                'odom_sensor_sync': True,
                # Stereo params
                'Vis/MinInliers':   '15',
                'Vis/MaxDepth':     '10.0',
                'Stereo/MinDisparity': '1',
                'Stereo/MaxDisparity': '128',
                'RGBD/AngularUpdate': '0.05',
                'RGBD/LinearUpdate': '0.05',
                'Mem/STMSize':      '30',
            }
        ],
        remappings=[
            ('left/image_rect',        '/stereo/left/image_rect_color'),
            ('right/image_rect',       '/stereo/right/image_rect_color'),
            ('left/camera_info',       '/stereo/left/camera_info'),
            ('right/camera_info',      '/stereo/right/camera_info'),
            ('imu',                    '/imu/data'),
        ],
        condition=UnlessCondition(localization),
        arguments=['--delete_db_on_start'],
    )

    # ---- rtabmap stereo localisation ----
    rtabmap_loc = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        parameters=[
            params_file,
            {
                'database_path':         database_path,
                'subscribe_stereo':      True,
                'subscribe_depth':       False,
                'Mem/IncrementalMemory': 'false',
                'Mem/InitWMWithAllNodes':'true',
            }
        ],
        remappings=[
            ('left/image_rect',  '/stereo/left/image_rect_color'),
            ('right/image_rect', '/stereo/right/image_rect_color'),
            ('left/camera_info', '/stereo/left/camera_info'),
            ('right/camera_info','/stereo/right/camera_info'),
            ('imu',              '/imu/data'),
        ],
        condition=IfCondition(localization),
    )

    return LaunchDescription([
        loc_arg, use_imu_arg, database_arg,
        imu_filter,
        rtabmap_slam,
        rtabmap_loc,
    ])
