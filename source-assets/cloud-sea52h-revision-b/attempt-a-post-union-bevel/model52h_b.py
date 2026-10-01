"""Native exact positive union plus limited12m rounding; no global smoothing."""
from pathlib import Path
import json,hashlib,math,bpy,bmesh
P=Path(__file__).resolve().parent;ROOT=P.parents[1];PLAN=P.parent/'cloud-sea52h-revision-b-plan'
source=PLAN/'cage52h_b_plan.blend';layout=json.loads((PLAN/'cage52h_b.json').read_text())
protected=[p for folder in ['cloud-sea52e','cloud-sea52f','cloud-sea52g','cloud-sea52h','cloud-sea52h-revision-b-plan'] for p in (P.parent/folder).rglob('*') if p.is_file() and p.suffix in ('.blend','.glb')]
protected+=[ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn',ROOT/'candidates/round40-exclusive-20260930/project/project.godot',ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p) for p in protected}
assert not(P/'cloud_sea52h_b.blend').exists(),'Do not overwrite a previously built source'
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
ctrl=bpy.data.collections.new('Editable52hB_authored_closed_polyhedral_cages');scene.collection.children.link(ctrl)
rawcol=bpy.data.collections.new('Control52hB_exact_raw_union');scene.collection.children.link(rawcol)
finalcol=bpy.data.collections.new('CloudSea52hB_primary_limited_rounding');scene.collection.children.link(finalcol)
with bpy.data.libraries.load(str(source),link=False) as (s,d):d.objects=[n for n in s.objects if n.startswith('CAGE52hB_')]
cages={}
for ob in d.objects:ctrl.objects.link(ob);cages[ob['role']]=ob
mat=cages['M_main'].data.materials[0]
main=cages['M_main'];raw=main.copy();raw.data=main.data.copy();raw.name='CloudSea52hB_v0_raw_union';rawcol.objects.link(raw);raw.show_wire=False;raw.show_all_edges=False
bpy.context.view_layer.objects.active=raw;raw.select_set(True)
for role in ['S_medium_rear_oblique','T_small_front_fold']:
 m=raw.modifiers.new('Positive union '+role,'BOOLEAN');m.operation='UNION';m.solver='EXACT';m.object=cages[role];bpy.ops.object.modifier_apply(modifier=m.name)
bm=bmesh.new();bm.from_mesh(raw.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(raw.data);bm.free()
raw['construction']='Exact positive union of three authored polyhedral cages; no subtractive valley or common base'
raw['source_coordinate_file']=str(PLAN/'cage52h_b.json');raw['visual_acceptance']=False
primary=raw.copy();primary.data=raw.data.copy();primary.name='CloudSea52hB_v0_main_crown';finalcol.objects.link(primary)
raw.select_set(False);primary.select_set(True);bpy.context.view_layer.objects.active=primary
m=primary.modifiers.new('Limited12m rounding of large turns only','BEVEL');m.width=12;m.segments=2;m.limit_method='ANGLE';m.angle_limit=.5;m.use_clamp_overlap=True
bpy.ops.object.modifier_apply(modifier=m.name)
primary['construction']='Raw union with12m two-segment bevel only at dihedral turns above0.5rad. No voxel remesh, global smooth, subdivision or QuadriFlow.'
for ob in [raw,primary]:
 bpy.context.view_layer.objects.active=ob
 m=ob.modifiers.new('Native restrained face triangulation','TRIANGULATE');m.quad_method='BEAUTY';m.ngon_method='BEAUTY';bpy.ops.object.modifier_apply(modifier=m.name)
 ob.data.materials.clear();ob.data.materials.append(mat)
 for attr in list(ob.data.color_attributes):ob.data.color_attributes.remove(attr)
 colors=ob.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
 for f in ob.data.polygons:
  f.use_smooth=False;f.material_index=0;z=sum(ob.data.vertices[i].co.z for i in f.vertices)/len(f.vertices);v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
  for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
for ob in cages.values():ob.hide_render=True
ctrl.hide_render=True;ctrl.hide_viewport=True;rawcol.hide_render=True
# Export each variant separately; neither export includes the overlapping cages.
for ob,filename in [(raw,'cloud_sea_52h_b_raw_union.glb'),(primary,'cloud_sea_52h_b_main_v0.glb')]:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.gltf(filepath=str(P/filename),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.ops.object.select_all(action='DESELECT');primary.select_set(True);bpy.context.view_layer.objects.active=primary
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52h_b.blend'))
after={str(p):sha(p) for p in protected};assert before==after
(P/'protected-sources52h-b.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
(P/'construction52h-b.json').write_text(json.dumps({'primary':'CloudSea52hB_v0_main_crown','raw_control':'CloudSea52hB_v0_raw_union','editable_authored_cages':3,'authored_cage_vertices':48,'authored_cage_faces':84,'bevel_width_m':12,'bevel_segments':2,'bevel_dihedral_threshold_radians':.5,'global_smooth':False,'voxel_remesh':False,'quadriflow':False,'negative_cutters':False,'material':mat.name,'vertex_color_formula':'v=.76+.16*clamp((z+190)/460,0,1); linear=((v+.055)/1.055)**2.4','world_modified':False,'rendered':False,'visual_acceptance':False},indent=2)+'\n')
print('52H B SOURCE BUILT; RAW UNION AND LIMITED ROUNDING; REVIEW PENDING')
