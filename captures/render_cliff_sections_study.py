import bpy,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='D:/test6/captures/cliff_sections_prototype.blend')
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1000;scene.render.resolution_y=760;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD'
scene.world.color=(.12,.15,.18);scene.view_settings.view_transform='Standard'
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera
camera.data.type='ORTHO';camera.data.ortho_scale=130
for name,pos in [('front',(95,-150,115)),('back',(-85,150,95))]:
    camera.location=Vector(pos);camera.rotation_euler=(Vector((0,15,25))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath='D:/test6/captures/cliff-sections-study-'+name+'.png'
    bpy.ops.render.render(write_still=True)
