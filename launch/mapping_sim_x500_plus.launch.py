#!/usr/bin/python3
# FAST-LIVO2 for gz-sim x500_plus (Livox MID360S + RealSense D455F)

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("fast_livo")

    lidar_config_cmd = os.path.join(pkg_share, "config", "sim_x500_plus.yaml")
    camera_config_cmd = os.path.join(pkg_share, "config", "camera_x500_plus.yaml")
    rviz_config_cmd = os.path.join(pkg_share, "rviz_cfg", "fast_livo2.rviz")

    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="False",
        description="Launch RViz2 with the bundled FAST-LIVO2 config (fast_livo2.rviz)",
    )
    lidar_config_arg = DeclareLaunchArgument(
        "lidar_params_file",
        default_value=lidar_config_cmd,
        description="Full path to the FAST-LIVO2 parameters file",
    )
    camera_config_arg = DeclareLaunchArgument(
        "camera_params_file",
        default_value=camera_config_cmd,
        description="Full path to the camera model parameters file",
    )

    lidar_params_file = LaunchConfiguration("lidar_params_file")
    camera_params_file = LaunchConfiguration("camera_params_file")
    use_rviz = LaunchConfiguration("use_rviz")

    return LaunchDescription([
        use_rviz_arg,
        lidar_config_arg,
        camera_config_arg,

        # camera params are loaded into the same node (no demo_nodes_cpp
        # parameter_blackboard required; vikit getRemoteParam finds them locally)
        Node(
            package="fast_livo",
            executable="fastlivo_mapping",
            name="laserMapping",
            parameters=[
                lidar_params_file,
                camera_params_file,
                {"use_sim_time": True},
            ],
            output="screen",
        ),

        # optional visualization: ros2 launch fast_livo mapping_sim_x500_plus.launch.py use_rviz:=true
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", rviz_config_cmd],
            parameters=[{"use_sim_time": True}],
            condition=IfCondition(use_rviz),
        ),
    ])

