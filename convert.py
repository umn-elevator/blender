import bpy
import sys
import os

# set to use the CPU only and cycles engine
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.render.engine = 'CYCLES'


force_continue = True

for current_argument in sys.argv:

    if force_continue:
        if current_argument == '--':
            force_continue = False
        continue
    
    filePath = current_argument


root, current_extension = os.path.splitext(filePath)
current_basename = os.path.basename(root)
current_directory = os.path.dirname(filePath)
if current_extension != ".abc" and current_extension != ".blend" and current_extension != ".dae" and current_extension != ".fbx" and current_extension != ".obj" and current_extension != ".ply" and current_extension != ".stl" and current_extension != ".usd" and current_extension != ".usda" and current_extension != ".usdc" and current_extension != ".wrl" and current_extension != ".x3d" and current_extension != ".glb":
    exit

tryVertexColorMapping = False

# use blender 4.0 python to perform operations
# bpy.ops.wm.ply_import(filepath="/scratch/Flagpole_decimated_ply.ply")
# bpy.ops.wm.ply_import(filepath="/scratch/heart_two_color_z_up.ply", forward_axis='Z', up_axis='Y')
if current_extension == ".abc":
    bpy.ops.wm.alembic_import(filepath=filePath)    

if current_extension == ".blend":
    bpy.ops.wm.open_mainfile(filepath=filePath)

if current_extension == ".dae":
    bpy.ops.wm.collada_import(filepath=filePath)    

if current_extension == ".fbx":
    bpy.ops.import_scene.fbx(filepath=filePath)    

if current_extension == ".obj":
    bpy.ops.wm.obj_import(filepath=filePath, use_split_objects=False, forward_axis='NEGATIVE_X', up_axis='Z')    
if current_extension == ".glb":
    bpy.ops.import_scene.gltf(filepath=filePath)   

if current_extension == ".ply":
    bpy.ops.wm.ply_import(filepath=filePath, forward_axis='NEGATIVE_X', up_axis='Z')
    tryVertexColorMapping= True

if current_extension == ".stl":
    bpy.ops.import_mesh.stl(filepath=filePath, forward_axis='NEGATIVE_X', up_axis='Z')

if current_extension == ".usd" or filePath == ".usda" or current_extension == ".usdc":
    bpy.ops.wm.usd_import(filepath=filePath, forward_axis='NEGATIVE_X', up_axis='Z')

if current_extension == ".wrl" or filePath == ".x3d":
    bpy.ops.import_scene.x3d(filepath=filePath)

# Get the imported object
obj = bpy.context.active_object


# Set the maximum dimension
maxDimension = 6.0

# Calculate the scale factor
scaleFactor = maxDimension / max(obj.dimensions)

# Scale the object
obj.scale = (scaleFactor, scaleFactor, scaleFactor)

# Set the origin to the geometry's median point
bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')


if(tryVertexColorMapping):
    newmat = bpy.data.materials.new("VertCol")
    newmat.use_nodes = True
    node_tree = newmat.node_tree
    nodes = node_tree.nodes

    bsdf = nodes.get("Principled BSDF") 


    vcol = nodes.new(type="ShaderNodeVertexColor")
    vcol.layer_name = "Col" # the vertex color layer name
    node_tree.links.new(vcol.outputs[0], bsdf.inputs[0])

    # add material output for bsdf
    output = nodes.get("Material Output")

    node_tree.links.new(bsdf.outputs[0], output.inputs[0])


    bpy.context.active_object.data.materials.append(newmat)
    print(bpy.context.active_object.data.materials)


    bpy.context.scene.world.use_nodes = False
    bpy.context.scene.world.color = (1, 1, 1)
# Set render resolution

render = bpy.context.scene.render
bpy.context.scene.cycles.samples = 8
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.cycles.use_adaptive_sampling = False
bpy.context.scene.cycles.max_bounces = 8
render.threads_mode = 'AUTO'

render.resolution_x = 1000
render.resolution_y = 1000
render.resolution_percentage = 100
render.dither_intensity = 0.0
def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))
# dump(render)


# bpy.data.scenes["Scene"].render.filepath = "/scratch/"
# bpy.ops.render.render(use_viewport=True, write_still=True)