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
scaling_ratio = 1.0
loopCount = 0
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
        scaling_ratio = float(current_argument)

    loopCount = loopCount + 1


root, current_extension = os.path.splitext(filePath)
current_basename = os.path.basename(root)
current_directory = os.path.dirname(filePath)
if current_extension != ".abc" and current_extension != ".blend" and current_extension != ".dae" and current_extension != ".fbx" and current_extension != ".obj" and current_extension != ".ply" and current_extension != ".stl" and current_extension != ".usd" and current_extension != ".usda" and current_extension != ".usdc" and current_extension != ".wrl" and current_extension != ".x3d":
    exit

bpy.ops.wm.read_factory_settings(use_empty=True)
print("Converting: '" + filePath + "'")

#

if current_extension == ".abc":
    bpy.ops.wm.alembic_import(filepath=filePath)    

if current_extension == ".blend":
    bpy.ops.wm.open_mainfile(filepath=filePath)

if current_extension == ".dae":
    bpy.ops.wm.collada_import(filepath=filePath)    

if current_extension == ".fbx":
    bpy.ops.import_scene.fbx(filepath=filePath)    

if current_extension == ".obj":
    bpy.ops.wm.obj_import(filepath=filePath)    

if current_extension == ".ply":
    bpy.ops.import_mesh.ply(filepath=filePath)    

if current_extension == ".stl":
    bpy.ops.import_mesh.stl(filepath=filePath)

if current_extension == ".usd" or filePath == ".usda" or current_extension == ".usdc":
    bpy.ops.wm.usd_import(filepath=filePath)

if current_extension == ".wrl" or filePath == ".x3d":
    bpy.ops.import_scene.x3d(filepath=filePath)

#
# automatically decimate the model
obj = bpy.context.selected_objects[0]

# Add the Decimate Modifier
decimate_modifier = obj.modifiers.new(name='DecimateMod', type='DECIMATE')
decimate_modifier.ratio = scaling_ratio

# Apply the modifier
bpy.ops.object.modifier_apply(modifier='DecimateMod')
for image in bpy.data.images:
    if(image.size[0] == image.size[1]):
        if(image.size[0] >= 4096 or image.size[1] >= 4096):
            if(scaling_ratio <= 0.2):
                image.scale(1024,1024)
            elif(scaling_ratio <= 0.5):
                image.scale(2048, 2048)
            else:
                image.scale(4096, 4096)




export_file = current_directory + "/" + current_basename + ".glb"
print("Writing: '" + export_file + "'")
bpy.ops.export_scene.gltf(filepath=export_file,export_draco_mesh_compression_enable=True )