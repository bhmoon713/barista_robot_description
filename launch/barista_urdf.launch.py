import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    ########## DATA INPUT ##########
    urdf_file = 'barista_robot_model.urdf'
    package_description = 'barista_robot_description'
    ########## DATA INPUT END ##########

    # Paths
    pkg_share = get_package_share_directory(package_description)
    robot_desc_path = os.path.join(pkg_share, "urdf", urdf_file)
    world_path = os.path.join(pkg_share, "worlds", "empty.world")
    rviz_config_dir = os.path.join(pkg_share, 'rviz', 'urdf_vis.rviz')

    # Joint State Publisher Node
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher_node',
        output='screen'
    )

    # Robot State Publisher Node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        emulate_tty=True,
        parameters=[{
            'use_sim_time': True,
            'robot_description': open(robot_desc_path).read()
        }],
        output='screen'
    )

    # RViz Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_dir]
    )

    # Gazebo (with your custom world)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={'world': world_path}.items()
    )

    # Spawn Robot
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'barista_robot',
            '-file', robot_desc_path,
            '-x', '0', '-y', '0', '-z', '0'
        ],
        output='screen'
    )

    return LaunchDescription([
        joint_state_publisher_node,
        robot_state_publisher_node,
        rviz_node,
        gazebo,
        spawn_entity
    ])
