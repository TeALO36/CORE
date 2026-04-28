#!/usr/bin/env python3
"""
SpotBot — GPS + Magnétomètre (OPTIONNEL)
⚠ Ne lancer que si le matériel est installé ET en extérieur
Usage:
  ros2 launch spotbot_bringup gps_mag.launch.py
  ros2 launch spotbot_bringup gps_mag.launch.py enable_gps:=true enable_mag:=true
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    gps_arg = DeclareLaunchArgument(
        'enable_gps', default_value='false',
        description='Activer le GPS (false par défaut, inutile en intérieur)'
    )
    mag_arg = DeclareLaunchArgument(
        'enable_mag', default_value='false',
        description='Activer le magnétomètre (false par défaut, bruyant indoor)'
    )
    gps_port_arg = DeclareLaunchArgument(
        'gps_port', default_value='/dev/ttyUSB1',
        description='Port série du module GPS'
    )

    gps_warn = LogInfo(
        msg='⚠ GPS activé — les données seront vides/imprécises en intérieur!',
        condition=IfCondition(LaunchConfiguration('enable_gps'))
    )

    mag_warn = LogInfo(
        msg='⚠ Magnétomètre activé — calibration requise, données bruitées indoor!',
        condition=IfCondition(LaunchConfiguration('enable_mag'))
    )

    # GPS Node (nmea_navsat_driver ou gpsd_client selon le module)
    # gps_node = Node(
    #     package='nmea_navsat_driver',
    #     executable='nmea_serial_driver',
    #     name='gps',
    #     parameters=[{
    #         'port': LaunchConfiguration('gps_port'),
    #         'baud': 9600,
    #         'frame_id': 'gps_link',
    #     }],
    #     condition=IfCondition(LaunchConfiguration('enable_gps')),
    #     output='screen'
    # )

    return LaunchDescription([
        gps_arg, mag_arg, gps_port_arg,
        gps_warn, mag_warn,
        # gps_node,  # Décommenter quand le driver est installé
    ])
