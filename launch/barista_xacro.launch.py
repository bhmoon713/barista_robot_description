import os
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # Setup package paths
    pkg_description = get_package_share_directory('barista_robot_description')
    install_dir = get_package_prefix('barista_robot_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # Set Gazebo paths
    gazebo_models_path = os.path.join(pkg_description, 'models')
    mesh_path = os.path.join(pkg_description, 'meshes')

    os.environ['GAZEBO_MODEL_PATH'] = f"{os.environ.get('GAZEBO_MODEL_PATH', '')}:{install_dir}/share:{gazebo_models_path}:{mesh_path}"
    os.environ['GAZEBO_PLUGIN_PATH'] = f"{os.environ.get('GAZEBO_PLUGIN_PATH', '')}:{install_dir}/lib"

    # Xacro processing    # convert XACRO file into URDF
    xacro_file = os.path.join(pkg_description, 'xacro', 'barista_robot_model.urdf.xacro')
    doc = xacro.parse(open(xacro_file))
    # xacro.process_doc(doc, mappings={'include_laser': 'true'})
    xacro.process_doc(doc) 
    params = {'robot_description': doc.toxml()}

    # Nodes
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        output='screen',
        parameters=[params]
    )

    rviz_config = os.path.join(pkg_description, 'rviz', 'urdf_vis.rviz')

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_node',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        )
    )

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', 'barista_bot',
            '-topic', '/robot_description',
            '-x', '0.0', '-y', '0.0', '-z', '0.0',
            '-R', '0.0', '-P', '0.0', '-Y', '0.0'
        ]
    )

    return LaunchDescription([
        robot_state_publisher_node,
        rviz_node,
        gazebo,
        spawn_robot
    ])
