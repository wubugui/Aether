"""Explicitly scheduled source previews only; this script was prepared, not executed."""
import bpy,sys,argparse,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--out',default=str(P/'source-previews'))
parser.add_argument('--white',action='store_true')
parser.add_argument('--variant',type=int,choices=[0],default=0)
parser.add_argument('--isolated',action='store_true')
parser.add_argument('--pair',action='store_true')
a=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(P/'cloud_sea52g_prototype.blend'))
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
# Read-only camera preflight, no renderer initialization
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=900;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Preview52f same as sea46');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.37,.53,.7,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.4,-.6,-.4);bpy.context.object.data.energy=2.5;bpy.context.object.data.angle=.15
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=2250;cam.data.clip_end=50000
if a.white:
    mat=bpy.data.materials.new('Diagnostic white only');mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.65,.65,.65,1);bs.inputs['Roughness'].default_value=1
    for ob in bpy.data.objects:
        if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(mat)
for c in bpy.data.collections:
    if c.name.startswith(('cloud_sea_52e_','cloud_sea_52f_')):c.hide_render=False;c.hide_viewport=False
framing=[]
for vi in [a.variant]:
    for ob in bpy.data.objects:
        if ob.type=='MESH':ob.hide_render=not ((ob.name.startswith('CloudSea52g_v0_') and not a.pair) or (not a.isolated and ob.name.startswith('CloudSea52f_v0_')))
    for name,pos in [('front',(0,-5000,700)),('back',(2500,4500,800)),('side',(4800,0,600)),('underside',(1800,-2500,-2400)),('top',(0,-1500,4200))]:
        cam.location=pos;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
        bpy.context.view_layer.update()
        projected=[world_to_camera_view(scene,cam,ob.matrix_world@v.co) for ob in bpy.data.objects if ob.type=='MESH' and not ob.hide_render for v in ob.data.vertices]
        bounds=[[min(v[k] for v in projected) for k in range(2)],[max(v[k] for v in projected) for k in range(2)]]
        margin=min(bounds[0]+[1-x for x in bounds[1]])
        framing.append({'variant':vi,'view':name,'target':[0,0,0],'normalized_bounds':bounds,'minimum_margin':margin})
        (P/'camera-framing-preflight52g.json').write_text(json.dumps(framing,indent=2))
        assert margin>.03, f'Framing clips or has insufficient margin: {name} {bounds}'
        scene.render.filepath=str(out/f'sea52g-prototype-{vi}-{name}{"-upper-only" if a.isolated else ("-pair" if a.pair else "-combined")}{"-white" if a.white else ""}.png')
        print(name,bounds,margin)
# Deliberately no save: source file and its materials remain unchanged.
