#!/usr/bin/env python3
"""
SpotBot — V-SLAM Monoculaire avec rtabmap
Prerequis: camera USB publie sur /camera/image_raw et /camera/camera_info
           IMU publie sur /imu/data (via arduino_bridge)

Lancement:
  ros2 launch spotbot_slam rtabmap_mono.launch.py
  ros2 launch spotbot_slam rtabmap_mono.launch.py localization:=true  # navigation seule (map deja faite)
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    loc_arg = DeclareLaunchArgument(
        'localization',
        default_value='false',
        description='Mode localisation seule (map existante): true | false'
    )
    use_imu_arg = DeclareLaunchArgument(
        'use_imu',
        default_value='true',
        description='Utiliser les donnees IMU Arduino: true | false'
    )
    database_path_arg = DeclareLaunchArgument(
        'database_path',
        default_value='~/.ros/spotbot_map.db',
        description='Chemin de la base de donnees rtabmap'
    )

    localization  = LaunchConfiguration('localization')
    database_path = LaunchConfiguration('database_path')
    use_imu       = LaunchConfiguration('use_imu')

    params_file = PathJoinSubstitution([
        FindPackageShare('spotbot_slam'), 'params', 'rtabmap_mono.yaml'
    ])

    # ---- Filtre IMU (Madgwick) ----
    imu_filter = Node(
        package='imu_filter_madgwick',
        executable='imu_filter_madgwick_node',
        name='imu_filter',
        parameters=[{
            'use_mag': False,
            'publish_tf': False,
            'world_frame': 'enu',
        }],
        remappings=[
            ('imu/data_raw', '/imu/data_raw'),
            ('imu/data',     '/imu/data'),
        ],
        condition=IfCondition(use_imu),
        output='screen'
    )

    # ---- rtabmap (SLAM actif) ----
    rtabmap_slam = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        parameters=[
            params_file,
            {
                'database_path': database_path,
                'subscribe_depth': False,
                'subscribe_rgb': True,
                'subscribe_stereo': False,
                'subscribe_odom_info': False,
                'odom_sensor_sync': True,
                'map_negative_poses_ignored': True,
                'map_negative_scan_empty_ray_tracing': False,
                # Parametres visuels mono
                'Vis/MinInliers': '10',
                'Vis/MaxDepth': '5.0',
                'RGBD/AngularUpdate': '0.05',
                'RGBD/LinearUpdate': '0.05',
                'RGBD/OptimizeFromGraphEnd': 'false',
                'Mem/STMSize': '30',
                'Reg/Strategy': '0',  # 0=Visual, 1=ICP
            }
        ],
        remappings=[
            ('rgb/image',       '/camera/image_raw'),
            ('rgb/camera_info', '/camera/camera_info'),
            ('imu',             '/imu/data'),
        ],
        condition=UnlessCondition(localization),
        arguments=['--delete_db_on_start'],
    )

    # ---- rtabmap (localisation seule) ----
    rtabmap_loc = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        parameters=[
            params_file,
            {
                'database_path': database_path,
                'subscribe_rgb': True,
                'subscribe_depth': False,
                'Mem/IncrementalMemory': 'false',
                'Mem/InitWMWithAllNodes': 'true',
            }
        ],
        remappings=[
            ('rgb/image',       '/camera/image_raw'),
            ('rgb/camera_info', '/camera/camera_info'),
            ('imu',             '/imu/data'),
        ],
        condition=IfCondition(localization),
    )

    # ---- Visualisation rtabmap ----
    rtabmap_viz = Node(
        package='rtabmap_viz',
        executable='rtabmap_viz',
        name='rtabmap_viz',
        parameters=[params_file],
        remappings=[
            ('rgb/image', '/camera/image_raw'),
            ('rgb/camera_info', '/camera/camera_info'),
        ],
        output='screen'
    )

    return LaunchDescription([
        loc_arg, use_imu_arg, database_path_arg,
        imu_filter,
        rtabmap_slam,
        rtabmap_loc,
    ])
