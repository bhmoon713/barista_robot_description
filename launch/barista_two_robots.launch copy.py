import os
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro
from launch.substitutions import Command


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
    
    
    robot_name_1 = "rick"
    robot_name_2 = "morty"
    robot_color_1 = "Red"
    robot_color_2 = "Blue"

    urdf_content_1 = Command([
        'xacro', ' ',
        xacro_file,' ',
        ' include_laser:=' , "true", ' ',
        ' robot_name:=', robot_name_1, ' ',
        'robot_color:=', robot_color_1,
    ])




    # Nodes
    # robot_state_publisher_node = Node(
    #     package='robot_state_publisher',
    #     executable='robot_state_publisher',
    #     name='robot_state_publisher_node',
    #     output='screen',
    #     parameters=[params]
    # )

    robot_state_publisher_node_rick = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node_rick',
        emulate_tty=True,
        namespace=robot_name_1,
        # parameters=[params],
        parameters=[{'frame_prefix': robot_name_1+'/', 'use_sim_time': "true", 'robot_description': urdf_content_1}],
        output="screen"
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
    static_tf_pub_rick = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher_odom1',
        output='screen',
        emulate_tty=True,
        arguments=['1', '0', '0', '0', '0', '0', 'world', robot_name_1+'/odom']
    )
    return LaunchDescription([
        robot_state_publisher_node_rick,
        # robot_state_publisher_node,
        rviz_node,
        gazebo,
        spawn_robot,
        static_tf_pub_rick,
    ])
