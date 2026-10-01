"""Native 52h single crown: irregular polyhedral cage with broad rounded folds."""
import bpy,bmesh,hashlib,json,math
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
SOURCE=P.parent/'cloud-sea52f/variants/cloud_sea52f_variants.blend'
protected=[p for dirname in ['cloud-sea52e','cloud-sea52f','cloud-sea52g'] for p in (P.parent/dirname).rglob('*') if p.is_file() and p.suffix in ('.blend','.glb')]
protected += [ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn',ROOT/'candidates/round40-exclusive-20260930/project/project.godot',ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p) for p in protected}
assert not (P/'cloud_sea52h_main.blend').exists(),'New stage only; do not overwrite an authored source'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
with bpy.data.libraries.load(str(SOURCE),link=False) as (s,d):d.materials=[n for n in s.materials if n=='Cloud46 diffuse warm crown cool belly']
mat=d.materials[0]
finalcol=bpy.data.collections.new('CloudSea52h_single_main');scene.collection.children.link(finalcol)
ctrl=bpy.data.collections.new('Editable52h_irregular_volume_cages');scene.collection.children.link(ctrl)
layout=json.loads((P/'layout52h.json').read_text());verts=layout['vertices'];faces=layout['faces']
# Bake only the established placement into vertices; every object transform stays identity.
verts=[(x-350,y-360,z) for x,y,z in verts]
me=bpy.data.meshes.new('52h_unstructured_closed_macro_faces');me.from_pydata(verts,[],faces);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
cage=bpy.data.objects.new('CONTROL52h_v0_closed_polyhedral_cage',me);ctrl.objects.link(cage)
for name,indices in layout['groups'].items():cage.vertex_groups.new(name=name).add(indices,1,'REPLACE')
cage['construction']=layout['construction'];cage['open_saddle_route']=layout['open_saddle_route']
cage['source_coordinates']='Blender x/y horizontal, z up; placement offset (-350,-360,0)'
cage['edit_instruction']='Edit the 63 cage vertices/groups. Main/medium/small share one continuous roof and belly; no overlapping ellipsoid parts.'
bev=cage.modifiers.new('Broad rounded macro edges, retain oblique face regions','BEVEL');bev.width=30;bev.segments=3;bev.limit_method='ANGLE';bev.angle_limit=.30;bev.use_clamp_overlap=True
cage.hide_render=True
work=cage.copy();work.data=cage.data.copy();work.name='CloudSea52h_v0_main_crown';finalcol.objects.link(work);work.hide_render=False
bpy.context.view_layer.objects.active=work;work.select_set(True)
bpy.ops.object.modifier_apply(modifier=work.modifiers[0].name)
# A closed remesh keeps a single editable, continuous rounded volume. No union/cutter.
m=work.modifiers.new('Continuous closed surface sampled at6m','REMESH');m.mode='VOXEL';m.voxel_size=6.0;m.use_smooth_shade=False
bpy.ops.object.modifier_apply(modifier=m.name)
m=work.modifiers.new('Local corner relaxation retains large face direction','SMOOTH');m.factor=.65;m.iterations=5
bpy.ops.object.modifier_apply(modifier=m.name)
continuous=bpy.data.objects.new('CONTROL52h_v0_continuous_rounded_surface',work.data.copy());ctrl.objects.link(continuous);continuous.hide_render=True
continuous['construction']='Full editable surface after30m macro-edge bevel,6m remesh and five local relaxation steps; before native quad retopology'
# Native isotropic quad retopology avoids the thin planar slivers produced by
# collapse decimation. The pre-retopology volume remains editable in controls.
bpy.ops.object.quadriflow_remesh(target_faces=1000,use_mesh_symmetry=False,use_preserve_sharp=False,use_preserve_boundary=True)
m=work.modifiers.new('Restrained triangles from native quad flow','TRIANGULATE');m.quad_method='BEAUTY';m.ngon_method='BEAUTY'
bpy.ops.object.modifier_apply(modifier=m.name)
work.data.materials.clear();work.data.materials.append(mat)
colors=work.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
for f in work.data.polygons:
 f.use_smooth=False;z=sum(work.data.vertices[i].co.z for i in f.vertices)/len(f.vertices)
 v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
 for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
for name,indices in layout['groups'].items():
 h=bpy.data.objects.new('CONTROL52h_'+name,None);ctrl.objects.link(h);h.empty_display_type='PLAIN_AXES';h.empty_display_size=50
 h.location=tuple(sum(verts[i][k] for i in indices)/len(indices) for k in range(3));h['cage_vertex_indices']=indices;h.hide_render=True
ctrl.hide_viewport=True;ctrl.hide_render=True
bpy.ops.object.select_all(action='DESELECT');work.select_set(True);bpy.context.view_layer.objects.active=work
bpy.ops.export_scene.gltf(filepath=str(P/'cloud_sea_52h_main_v0.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52h_main.blend'))
after={str(p):sha(p) for p in protected};assert before==after
(P/'protected-sources52h.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
(P/'construction52h.json').write_text(json.dumps({'control_vertices':len(verts),'control_faces':len(faces),'editable_control_meshes':2,'reference_handles':4,'bevel_width_m':30,'bevel_segments':3,'bevel_angle_limit_radians':.30,'voxel_m':6,'relaxation_iterations':5,'quad_target_before_triangulation':1000,'material':mat.name,'vertex_color_formula':'v=.76+.16*clamp((z+190)/460,0,1); linear=((v+.055)/1.055)**2.4','source_material_modified':False,'renderer_executed':False,'world_integration':False,'visual_acceptance':False},indent=2)+'\n')
print('52H SINGLE NATIVE MAIN SOURCE READY; NO RENDER / NO WORLD')
