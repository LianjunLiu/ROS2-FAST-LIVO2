#!/usr/bin/python3
# -- coding: utf-8 --**
"""FAST-LIVO2 mapping launch for Livox MID360S + RealSense D455F.

前置条件：两个传感器已启动
  ros2 launch fast_livo sensors_mid360s_d455f.launch.py
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():

    # Find path
    config_file_dir = os.path.join(get_package_share_directory("fast_livo"), "config")
    rviz_config_file = os.path.join(get_package_share_directory("fast_livo"), "rviz_cfg", "M300.rviz")

    # Load parameters
    lidar_config_cmd = os.path.join(config_file_dir, "mid360s_d455f.yaml")
    camera_config_cmd = os.path.join(config_file_dir, "camera_d455f.yaml")

    # Param use_rviz
    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="False",
        description="Whether to launch Rviz2",
    )

    lidar_config_arg = DeclareLaunchArgument(
        'lidar_params_file',
        default_value=lidar_config_cmd,
        description='Full path to the ROS2 parameters file for fast_livo2 nodes',
    )

    camera_config_arg = DeclareLaunchArgument(
        'camera_params_file',
        default_value=camera_config_cmd,
        description='Full path to the ROS2 parameters file for camera model',
    )

    use_respawn_arg = DeclareLaunchArgument(
        'use_respawn',
        default_value='True',
        description='Whether to respawn if a node crashes. Applied when composition is disabled.')

    # 覆盖 yaml 里的 imu_topic，默认与 yaml 一致。实车改用飞控 IMU 时传
    # imu_topic:=/fcu/imu（由 x500_plus 的 fcu_imu_to_livox 节点发布）。
    imu_topic_arg = DeclareLaunchArgument(
        'imu_topic',
        default_value='/livox/imu',
        description='IMU topic override (e.g. /fcu/imu to use the flight controller IMU)')

    lidar_params_file = LaunchConfiguration('lidar_params_file')
    camera_params_file = LaunchConfiguration('camera_params_file')
    use_respawn = LaunchConfiguration('use_respawn')

    return LaunchDescription([
        use_rviz_arg,
        lidar_config_arg,
        camera_config_arg,
        use_respawn_arg,
        imu_topic_arg,

        # camera params must be loaded via parameter_blackboard,
        # fastlivo_mapping reads them from this node's parameter server
        Node(
            package='demo_nodes_cpp',
            executable='parameter_blackboard',
            name='parameter_blackboard',
            parameters=[
                camera_params_file,
            ],
            output='screen'
        ),

        # Load the camera params into the mapping node itself as well.
        # vikit's getRemoteParam() checks the local node first, so this hits
        # locally and avoids the cross-node SyncParametersClient whose 100ms
        # service-discovery wait races (too short on Jetson).
        Node(
            package="fast_livo",
            executable="fastlivo_mapping",
            name="laserMapping",
            parameters=[
                lidar_params_file,
                camera_params_file,
                # yaml 里的键是嵌套的 common.imu_topic，覆盖时名字必须一样
                {'common.imu_topic': LaunchConfiguration('imu_topic')},
            ],
            output="screen"
        ),

        Node(
            condition=IfCondition(LaunchConfiguration("use_rviz")),
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", rviz_config_file],
            output="screen"
        ),
    ])
