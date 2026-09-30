from pathlib import Path
import bpy,bmesh,json,hashlib,shutil
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_island_study_29b/island_c.blend';OUT=R/'captures/lantern_island_study_29c';assert not OUT.exists();OUT.mkdir()
shutil.copy2(__file__,OUT/'builder.py');shutil.copy2(R/'captures/island-29c-shoulder-plan.json',OUT/'shoulder-plan.json')
shutil.copy2(R/'captures/lantern_island_study_29b/terrain-plan.json',OUT/'terrain-plan.json')
plan=json.loads((OUT/'shoulder-plan.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(SRC))
def sig(o):return {'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'materials':[p.material_index for p in o.data.polygons]}
old={role:sig(bpy.data.objects[name]) for role,name in [('terrain','island_c grass and exposed rock terrain'),('path','island_c terrain fitted keeper paths'),('core','island_c faulted bedrock')]}
materials=list(bpy.data.objects['island_c faulted bedrock'].data.materials)
for spec in plan['meshes']:
 data=bpy.data.meshes.new(spec['name']);data.from_pydata(spec['vertices'],[],spec['faces']);data.update();o=bpy.data.objects.new(spec['name'],data);bpy.context.collection.objects.link(o)
 for m in materials:data.materials.append(m)
 for p in data.polygons:p.material_index=2 if p.center.z<.8 else (1 if p.normal.x<-.25 else 0)
 o['authoring_role']='Continuous inclined summit-to-tidal rock buttress'
native=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
 assert all(f.calc_area()>1e-9 for f in bm.faces),o.name
 volume=bm.calc_volume(signed=True);assert volume>0,(o.name,volume)
 bm.to_mesh(o.data);bm.free();native.append({'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'volume_m3':volume})
bpy.context.scene['scope']='29c four continuous diagonal rock buttresses over29b, protected actual support surfaces retained, exact local vertical clearance evidence. Visual pending.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_c.blend'))
protection=json.loads((R/'captures/lantern_island_study_29b/geometry-evidence.json').read_text())['protection']
(OUT/'geometry-evidence.json').write_text(json.dumps({'old':old,'new':{o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'},'protection':protection,'shoulders':plan}),encoding='utf-8')
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
(OUT/'model-report.json').write_text(json.dumps({'label':'29c','source_basis':str(SRC.relative_to(R)),'source_basis_sha256':sha(SRC),'source_sha256':sha(OUT/'island_c.blend'),'glb_sha256':sha(OUT/'island_c.glb'),'native':native,'scope':bpy.context.scene['scope']},indent=2))
print('29c SAVED AND EXPORTED '+str(len(native)),flush=True)
