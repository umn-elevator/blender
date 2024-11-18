import bpy
import sys

# set to use the CPU only and cycles engine
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.render.engine = 'CYCLES'


force_continue = True

for current_argument in sys.argv:

    if force_continue:
        if current_argument == '--':
            force_continue = False
        continue
    
    input_file = current_argument

# use blender 4.0 python to perform operations
# bpy.ops.wm.ply_import(filepath="/scratch/Flagpole_decimated_ply.ply")
# bpy.ops.wm.ply_import(filepath="/scratch/heart_two_color_z_up.ply", forward_axis='Z', up_axis='Y')
bpy.ops.wm.ply_import(filepath=input_file, forward_axis='NEGATIVE_X', up_axis='Z')

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