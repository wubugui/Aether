"""Build one C crown using native Blender positive volumes; no renderer."""
from pathlib import Path
import json,hashlib,bpy,bmesh
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
plan=json.loads((P/'plan52h-c.json').read_text())
old_dirs=['cloud-sea52e','cloud-sea52f','cloud-sea52g','cloud-sea52h','cloud-sea52h-revision-b-plan','cloud-sea52h-revision-b']
protected=[p for folder in old_dirs for p in (P.parent/folder).rglob('*') if p.is_file()]
protected += [ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn',ROOT/'candidates/round40-exclusive-20260930/project/project.godot',ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p) for p in protected}
assert not(P/'cloud_sea52h_c.blend').exists(),'Preserve all built sources; revisions must be independent'
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
source=P.parent/'cloud-sea52f/variants/cloud_sea52f_variants.blend'
with bpy.data.libraries.load(str(source),link=False) as (s,d):d.materials=['Cloud46 diffuse warm crown cool belly']
mat=d.materials[0]
ctrl=bpy.data.collections.new('Editable52hC_3macro_8medium_cages');scene.collection.children.link(ctrl)
stages=bpy.data.collections.new('Editable52hC_union_and_continuous_surface');scene.collection.children.link(stages)
finalcol=bpy.data.collections.new('CloudSea52hC_single_main');scene.collection.children.link(finalcol)
cages={}
for role,row in plan['parts'].items():
 me=bpy.data.meshes.new(role+'_native_control');me.from_pydata(row['vertices_blender_m'],[],row.get('oriented_triangles',[]));me.update()
 bm=bmesh.new();bm.from_mesh(me)
 if row.get('hull_native'):
  ret=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
  if ret['geom_unused']:bmesh.ops.delete(bm,geom=ret['geom_unused'],context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new('CAGE52hC_'+role,me);ctrl.objects.link(ob);ob['role']=role;ob['coordinate_source']='plan52h-c.json';ob['positive_only']=True;ob.hide_render=True;ob.show_wire=True;ob.show_all_edges=True;me.materials.append(mat);cages[role]=ob
work=cages['M_main'].copy();work.data=work.data.copy();work.name='CloudSea52hC_v0_main_crown';finalcol.objects.link(work);work.hide_render=False;work.show_wire=False;work.show_all_edges=False
bpy.ops.object.select_all(action='DESELECT');work.select_set(True);bpy.context.view_layer.objects.active=work
for role,ob in cages.items():
 if role=='M_main':continue
 m=work.modifiers.new('Positive volume '+role,'BOOLEAN');m.operation='UNION';m.solver='EXACT';m.object=ob;bpy.ops.object.modifier_apply(modifier=m.name)
raw=bpy.data.objects.new('CONTROL52hC_exact_positive_union',work.data.copy());stages.objects.link(raw);raw.hide_render=True
m=work.modifiers.new('Native continuous10m volume sample','REMESH');m.mode='VOXEL';m.voxel_size=10;m.use_smooth_shade=False;bpy.ops.object.modifier_apply(modifier=m.name)
m=work.modifiers.new('Two local passes remove voxel steps, retain medium folds','SMOOTH');m.factor=.5;m.iterations=2;bpy.ops.object.modifier_apply(modifier=m.name)
continuous=bpy.data.objects.new('CONTROL52hC_continuous_medium_fold_surface',work.data.copy());stages.objects.link(continuous);continuous.hide_render=True
bpy.ops.object.quadriflow_remesh(target_faces=1000,use_mesh_symmetry=False,use_preserve_sharp=False,use_preserve_boundary=True)
m=work.modifiers.new('Restrained isotropic triangles','TRIANGULATE');m.quad_method='BEAUTY';m.ngon_method='BEAUTY';bpy.ops.object.modifier_apply(modifier=m.name)
work.data.materials.clear();work.data.materials.append(mat)
for attr in list(work.data.color_attributes):work.data.color_attributes.remove(attr)
colors=work.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
for f in work.data.polygons:
 f.use_smooth=False;f.material_index=0;z=sum(work.data.vertices[i].co.z for i in f.vertices)/len(f.vertices);v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
 for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
work['source_editing']='11 positive control meshes plus exact union and continuous pre-retopology surface retained. No bevel, negative volume or random noise.';work['visual_acceptance']=False
ctrl.hide_viewport=True;ctrl.hide_render=True;stages.hide_viewport=True;stages.hide_render=True
bpy.ops.object.select_all(action='DESELECT');work.select_set(True);bpy.context.view_layer.objects.active=work
bpy.ops.export_scene.gltf(filepath=str(P/'cloud_sea_52h_c_main_v0.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52h_c.blend'))
after={str(p):sha(p) for p in protected};assert before==after
(P/'protected-sources52h-c.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
(P/'construction52h-c.json').write_text(json.dumps({'editable_control_meshes':13,'macro_cages':3,'medium_cages':8,'exact_union_retained':True,'continuous_surface_retained':True,'native_voxel_m':10,'relaxation_iterations':2,'relaxation_factor':.5,'quad_target':1000,'bevel':False,'sphere_primitives':False,'random_noise':False,'negative_cutters':False,'material':mat.name,'vertex_color_formula':'v=.76+.16*clamp((z+190)/460,0,1); linear=((v+.055)/1.055)**2.4','rendered':False,'world_modified':False,'visual_acceptance':False},indent=2)+'\n')
print('52H C NATIVE SOURCE BUILT; NOT RENDERED OR VISUALLY ACCEPTED')
