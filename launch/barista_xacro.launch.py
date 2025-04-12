import os

from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_description = get_package_share_directory('barista_robot_description')
    install_dir = get_package_prefix('barista_robot_description')

    gazebo_models_path = os.path.join(pkg_description, 'models')
    mesh_path = os.path.join(pkg_description, 'meshes')

    os.environ['GAZEBO_MODEL_PATH'] = f"{os.environ.get('GAZEBO_MODEL_PATH', '')}:{install_dir}/share:{gazebo_models_path}:{mesh_path}"
    os.environ['GAZEBO_PLUGIN_PATH'] = f"{os.environ.get('GAZEBO_PLUGIN_PATH', '')}:{install_dir}/lib"

    urdf_file = 'barista_robot_model.urdf.xacro'
    robot_desc_path = os.path.join(pkg_description, 'xacro', urdf_file)
    rviz_config_dir = os.path.join(pkg_description, 'rviz', 'urdf_vis.rviz')

    robot_description_content = Command([
        'xacro',
        PathJoinSubstitution([
            FindPackageShare('barista_robot_description'),
            'xacro ',
            'barista_robot_model.urdf.xacro'
        ]),
        'include_laser:=true'
    ])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        parameters=[{'use_sim_time': True, 'robot_description': robot_description_content}],
        output='screen',
        emulate_tty=True
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_node',
        output='screen',
        arguments=['-d', rviz_config_dir],
        parameters=[{'use_sim_time': True}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
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
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_description, 'worlds', 'empty.world'),
            description='SDF world file'
        ),
        robot_state_publisher_node,
        rviz_node,
        gazebo,
        spawn_robot
    ])
