# 
# The MIT License (MIT)
#
# Copyright (c) since 2017 UX3D GmbH
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 

#
# Imports
#

import bpy
import sys
import os



#
# Globals
#

#
# Functions
#
def resize_texture(image, max_size=1024):
    # Get the image file path
    image_path = bpy.path.abspath(image.filepath)
    
    # Open the image using PIL
    with Image.open(image_path) as img:
        width, height = img.size
        if width <= max_size and height <= max_size:
            return  # No need to resize

        # Calculate the new size while maintaining the aspect ratio
        scale = min(max_size / width, max_size / height)
        new_width = int(width * scale)
        new_height = int(height * scale)

        # Resize the image
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Save the resized image back to the same path
        img.save(image_path)



force_continue = True

filePath = ""
scaling_ratio = "large"
loopCount = 0
outputFormat = "glb"
# this is a terrible hack which i haven't refactored because i haven't wanted to coordinate
# the change on the invocation side. Someone, please redo this with actual commandline args.
for current_argument in sys.argv:

    if force_continue:
        if current_argument == '--':
            force_continue = False
        continue

    if(force_continue == False and loopCount == 0):
        filePath = current_argument

    if(force_continue == False and loopCount == 1):
        scaling_ratio = current_argument

    if(force_continue == False and loopCount == 2):
        outputFormat = current_argument
    loopCount = loopCount + 1


root, current_extension = os.path.splitext(filePath)
current_basename = os.path.basename(root)
current_directory = os.path.dirname(filePath)
if current_extension != ".abc" and current_extension != ".blend" and current_extension != ".dae" and current_extension != ".fbx" and current_extension != ".obj" and current_extension != ".ply" and current_extension != ".stl" and current_extension != ".usd" and current_extension != ".usda" and current_extension != ".usdc" and current_extension != ".wrl" and current_extension != ".x3d" and current_extension != ".glb":
    exit


bpy.ops.wm.read_factory_settings(use_empty=True)
print("Converting: '" + filePath + "'")

#
tryVertexColorMapping = False

if current_extension == ".abc":
    bpy.ops.wm.alembic_import(filepath=filePath)    

if current_extension == ".blend":
    bpy.ops.wm.open_mainfile(filepath=filePath)

if current_extension == ".dae":
    bpy.ops.wm.collada_import(filepath=filePath)    

if current_extension == ".fbx":
    bpy.ops.import_scene.fbx(filepath=filePath)    

if current_extension == ".obj":
    bpy.ops.wm.obj_import(filepath=filePath, use_split_objects=False, forward_axis='NEGATIVE_Z', up_axis='Y')
if current_extension == ".glb":
    bpy.ops.import_scene.gltf(filepath=filePath)   

if current_extension == ".ply":
    bpy.ops.wm.ply_import(filepath=filePath, forward_axis='NEGATIVE_Z', up_axis='Y')
    tryVertexColorMapping= True

if current_extension == ".stl":
    bpy.ops.wm.stl_import(filepath=filePath, forward_axis='NEGATIVE_Z', up_axis='Y')

if current_extension == ".usd" or filePath == ".usda" or current_extension == ".usdc":
    bpy.ops.wm.usd_import(filepath=filePath, forward_axis='NEGATIVE_Z', up_axis='Y')

if current_extension == ".wrl" or filePath == ".x3d":
    bpy.ops.import_scene.x3d(filepath=filePath)

#
# automatically decimate the model
obj = bpy.context.selected_objects[0]


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


# Add the Decimate Modifier
decimate_modifier = obj.modifiers.new(name='DecimateMod', type='DECIMATE')

# get the current face count
original_face_count = len(obj.data.polygons)
scaling_ratio_float = 1.0
if(scaling_ratio == "thumb" and original_face_count > 10000):
    scaling_ratio_float = 10000 / original_face_count

if(scaling_ratio == "medium" and original_face_count > 150000):
    scaling_ratio_float = 150000 / original_face_count
if(scaling_ratio == "large" and original_face_count > 150000):
    scaling_ratio_float = 150000 / original_face_count

print("Computed a scaling ratio of " + str(scaling_ratio_float) + " to get face count under " + str(scaling_ratio))

decimate_modifier.ratio = scaling_ratio_float

# Apply the modifier
bpy.ops.object.modifier_apply(modifier='DecimateMod')
for image in bpy.data.images:
    if(image.size[0] == image.size[1]):
        if(image.size[0] >= 4096 or image.size[1] >= 4096):
            if(scaling_ratio == "thumb"):
                image.scale(512,512)
            elif(scaling_ratio == "medium"):
                image.scale(2048, 2048)
            else:
                image.scale(4096, 4096)


bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')



if outputFormat == "glb":
    export_file = current_directory + "/" + current_basename + "_output.glb"
    print("Writing: '" + export_file + "'")
    bpy.ops.export_scene.gltf(filepath=export_file,export_draco_mesh_compression_enable=False, export_yup=True)
elif outputFormat == "usdz":
    export_file = current_directory + "/" + current_basename + "_output.usdz"
    print("Writing: '" + export_file + "'")
    # Set the maximum dimension
    maxDimension = 1.0
    obj = bpy.context.active_object

    # Calculate the scale factor
    scaleFactor = maxDimension / max(obj.dimensions)

    # Scale the object
    obj.scale = (scaleFactor, scaleFactor, scaleFactor)

    # us bpy.ops.wm.usd_export to export the mesh to usdz
    bpy.ops.wm.usd_export(filepath=export_file)