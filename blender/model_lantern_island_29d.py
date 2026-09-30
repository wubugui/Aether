"""Remodel the actual island surface and bedrock, starting saved29b."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,shutil
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_island_study_29b/island_c.blend';OUT=R/'captures/lantern_island_study_29d';assert not OUT.exists();OUT.mkdir()
shutil.copy2(__file__,OUT/'builder.py');shutil.copy2(R/'captures/island-29d-terrain-plan.json',OUT/'terrain-plan.json');plan=json.loads((OUT/'terrain-plan.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(SRC))
terrain=bpy.data.objects['island_c grass and exposed rock terrain'];path=bpy.data.objects['island_c terrain fitted keeper paths'];core=bpy.data.objects['island_c faulted bedrock']
def sig(o):return {'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'materials':[p.material_index for p in o.data.polygons]}
old={role:sig(o) for role,o in [('terrain',terrain),('path',path),('core',core)]}
for i,p in enumerate(plan['terrain_vertices']):terrain.data.vertices[i].co=p
materials=list(core.data.materials);terrain.data.materials.append(materials[0]);terrain.data.update();protected=set(plan['protected_face_indices']);n=plan['top_vertex_count']
for p in terrain.data.polygons:
 if max(p.vertices)>=n or p.index in protected:continue
 x,y=p.center.x,p.center.y
 close=min(((x-cx)/sx)**2+((y-cy)/sy)**2 for cx,cy,sx,sy,h in plan['knuckles'])
 if p.normal.z>.82 and p.center.z>10 and close>.45:p.material_index=0
 else:p.material_index=2 if p.normal.x<-.60 else 3
data=bpy.data.meshes.new('C/D irregular unified bedrock side');data.from_pydata(plan['core_vertices'],[],plan['core_faces']);data.update();core.data=data
for m in materials:data.materials.append(m)
for p in data.polygons:p.material_index=2 if p.center.z<.8 else (1 if p.normal.x<-.60 and p.normal.z<.5 else 0)
native=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),(o.name,'not closed')
 assert all(f.calc_area()>1e-9 for f in bm.faces),(o.name,'zero face')
 volume=bm.calc_volume(signed=True);assert volume>0,(o.name,volume)
 bm.to_mesh(o.data);bm.free();native.append({'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'volume_m3':volume})
assert sig(path)==old['path']
for i in plan['protected_vertex_indices']:assert list(terrain.data.vertices[i].co)==old['terrain']['vertices'][i]
bpy.context.scene['scope']='29d native connected terrain shoulder and bedrock topology remodeling;29b protected support retained; no29c long wedge objects. Visual pending.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_c.blend'))
e=json.loads((R/'captures/lantern_island_study_29b/geometry-evidence.json').read_text());(OUT/'geometry-evidence.json').write_text(json.dumps({'old':old,'new':{o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'},'protection':e['protection'],'protected_face_indices':plan['protected_face_indices'],'protected_vertex_indices':plan['protected_vertex_indices']}),encoding='utf-8')
groups={}
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':groups.setdefault(o.data.materials[0].name,[]).append(o)
for material,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 if len(objects)>1:bpy.ops.object.join()
 bpy.context.object.name='island_c_'+material
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(OUT/'island_c.glb'),export_format='GLB',use_selection=True,export_apply=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'model-report.json').write_text(json.dumps({'label':'29d','source_basis':str(SRC.relative_to(R)),'source_basis_sha256':sha(SRC),'source_sha256':sha(OUT/'island_c.blend'),'glb_sha256':sha(OUT/'island_c.glb'),'native':native,'changed_top_vertices':plan['changed_top_vertices'],'old_high_steep_faces':len(plan['old_selected_steep_faces']),'new_high_steep_faces':len(plan['new_selected_steep_faces']),'scope':bpy.context.scene['scope']},indent=2))
print('29d SAVED AND EXPORTED '+str(len(native)),flush=True)
