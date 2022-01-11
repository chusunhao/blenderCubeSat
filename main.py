import bpy
import os


def import_obj():
    # folder path for importing data files
    in_dir_ply = r"C:\Users\chusu\UnityProjects\cube_sat_obj"
    lst_ply = os.listdir(in_dir_ply)

    # Filter file list by valid file types.
    file = []
    for item in lst_ply:
        fileName, fileExtension = os.path.splitext(item)
        if fileExtension == ".obj":
            file.append(item)

    # To import mesh.ply in batches
    for i in range(len(file)):
        bpy.ops.import_scene.obj(filepath=os.path.join(in_dir_ply, file[i]))


def set_camera():
    tx = 0.0
    ty = 0.0
    tz = -5.0

    rx = 180.0
    ry = 0.0
    rz = 0.0

    pi = 3.14159265

    camera = bpy.data.objects['Camera']

    # Set camera rotation in euler angles
    camera.rotation_mode = 'XYZ'
    camera.rotation_euler[0] = rx * (pi / 180.0)
    camera.rotation_euler[1] = ry * (pi / 180.0)
    camera.rotation_euler[2] = rz * (pi / 180.0)

    # Set camera translation
    camera.location.x = tx
    camera.location.y = ty
    camera.location.z = tz


def rendering():
    # Set up rendering of depth map.
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    bpy.context.scene.render.image_settings.color_depth = '32'
    bpy.context.scene.render.image_settings.color_mode = 'RGB'

    # 必须设置，否则无法输出深度
    bpy.context.scene.render.image_settings.file_format = "OPEN_EXR"

    # 必须设置，否则无法输出法向
    bpy.context.view_layer.use_pass_normal = True

    # Clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # Create input render layer node.
    render_layers = tree.nodes.new('CompositorNodeRLayers')

    depth_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
    depth_file_output.label = 'Depth Output'
    links.new(render_layers.outputs['Depth'], depth_file_output.inputs[0])

    scale_normal = tree.nodes.new(type="CompositorNodeMixRGB")
    scale_normal.blend_type = 'MULTIPLY'
    scale_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
    links.new(render_layers.outputs['Normal'], scale_normal.inputs[1])
    bias_normal = tree.nodes.new(type="CompositorNodeMixRGB")
    bias_normal.blend_type = 'ADD'
    bias_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 0)
    links.new(scale_normal.outputs[0], bias_normal.inputs[1])
    normal_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
    normal_file_output.label = 'Normal Output'
    links.new(bias_normal.outputs[0], normal_file_output.inputs[0])

    image_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
    image_file_output.label = 'Image'
    links.new(render_layers.outputs['Image'], image_file_output.inputs[0])

    scene = bpy.context.scene
    # 设置输出分辨率，可以自行修改
    scene.render.resolution_x = 300
    scene.render.resolution_y = 200

    scene.render.resolution_percentage = 100
    cam = scene.objects['Camera']

    # fov
    cam.data.angle = 10 * (3.1415926 / 180.0)

    for output_node in [depth_file_output, normal_file_output, image_file_output]:
        output_node.base_path = ''

    # 输出路径
    scene.render.filepath = r'C:\Users\chusu\UnityProjects\cube_sat_obj'
    depth_file_output.file_slots[0].path = scene.render.filepath + 'depth_'
    normal_file_output.file_slots[0].path = scene.render.filepath + 'normal_'
    image_file_output.file_slots[0].path = scene.render.filepath + 'image_'

    bpy.ops.render.render()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import_obj()
    set_camera()
    rendering()


