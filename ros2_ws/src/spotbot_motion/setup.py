from setuptools import setup, find_packages

package_name = 'spotbot_motion'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'numpy'],
    zip_safe=True,
    maintainer='SpotBot',
    maintainer_email='spotbot@robot.local',
    description='SpotBot motion controller — IK + gait',
    license='MIT',
    entry_points={
        'console_scripts': [
            'motion_node = spotbot_motion.motion_node:main',
        ],
    },
)
