"""Render the modeled airship from a second angle in Blender itself."""
from pathlib import Path
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
bpy.data.collections['Landscape'].hide_render=True
ship=bpy.data.objects['Airship']
target=ship.location+Vector((0,0,2.7))
camera=scene.camera
camera.location=target+Vector((-15,-25,11))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=18.3
scene.render.resolution_x=1200;scene.render.resolution_y=1000
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.57,.65,.70,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
scene.render.film_transparent=False
scene.render.filepath=str(root/'captures/blender-airship.png')
bpy.ops.render.render(write_still=True)
