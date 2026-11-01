#!/usr/bin/python3
"""同时启动 Livox MID360S 与 RealSense D455F 两个传感器。

用法：
    ros2 launch fast_livo sensors_mid360s_d455f.launch.py

话题：
    /livox/lidar, /livox/imu            （MID360S，参数固化在 MID360s_config.json）
    /camera/color/image_raw, camera_info（D455F，848x480@30 RGB8）
"""

import os
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # --- Livox MID360S ---
    livox_launch_dir = os.path.join(get_package_share_directory('livox_ros_driver2'), 'launch_ROS2')

    # --- RealSense D455F ---
    realsense_node = Node(
        package='realsense2_camera',
        executable='realsense2_camera_node',
        name='camera',
        namespace='',
        output='screen',
        parameters=[{
            'enable_color': True,
            'rgb_camera.color_profile': '640,360,15',
            'rgb_camera.color_format': 'RGB8',
            'enable_depth': False,
            'enable_infra1': False,
            'enable_infra2': False,
            'enable_gyro': False,
            'enable_accel': False,
            'pointcloud.enable': False,
            'publish_tf': True,
        }],
    )

    return LaunchDescription([
        IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(livox_launch_dir, 'msg_MID360s_launch.py'))),
        realsense_node,
    ])
