from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'spotbot_arduino_bridge'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='SpotBot',
    maintainer_email='spotbot@robot.local',
    description='SpotBot Arduino bridge node',
    license='MIT',
    entry_points={
        'console_scripts': [
            'arduino_bridge_node = spotbot_arduino_bridge.arduino_bridge_node:main',
            'arduino_flasher     = spotbot_arduino_bridge.arduino_flasher:main',
        ],
    },
)
