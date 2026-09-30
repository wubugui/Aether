"""Correct31g replacement-face native material assignment; geometry exactly retained."""
from pathlib import Path
import bpy,bmesh,json,hashlib,shutil
from mathutils import Vector
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_island_study_31g/island_c.blend';OUT=R/'captures/lantern_island_study_31h'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
bpy.ops.wm.open_mainfile(filepath=str(SRC));tn='island_c grass and exposed rock terrain';terrain=bpy.data.objects[tn]
def sig(o):return dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons])
old={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
plan=json.loads((SRC.parent/'proportion-plan.json').read_text());reform=json.loads((SRC.parent/'reform-plan.json').read_text())
lv=reform['replacement_local_vertices'];keys={tuple(sorted(tuple(Vector(lv[i])) for i in f)) for f in reform['replacement_local_triangles']}
selected=[]
for p in terrain.data.polygons:
 key=tuple(sorted(tuple(terrain.data.vertices[i].co) for i in p.vertices))
 if key not in keys:continue
 center=sum((terrain.data.vertices[i].co for i in p.vertices),Vector())/3
 # Restrict grass to the upper, upward-facing shoulder. Native stone slot2 elsewhere.
 mat=0 if center.z>8.8 and p.normal.z>.78 else 2
 selected.append(dict(polygon=p.index,before=p.material_index,after=mat,center=list(center),normal=list(p.normal),xyz=[list(terrain.data.vertices[i].co) for i in p.vertices]))
 p.material_index=mat
assert len(selected)==84
reform['scope']='31h native material correction over unchanged31g true retopology. All84 replacement faces were wrongly assigned grass in31g. Restore existing stone slot2 on exposed slopes/root; allow native grass only on upper upward shoulder (centroid z>8.8 and normal.z>.78). Geometry, actual boundary and full support unchanged; no claim that material correction completes rock form.'
reform['material_revision']=dict(source='31g',slots=[m.name for m in terrain.data.materials],faces=selected,geometry_unchanged=True)
plan['scope']=reform['scope'];plan['slope_reform']=reform
new={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
for name,s in new.items():
 assert s['vertices']==old[name]['vertices'] and s['polygons']==old[name]['polygons']
 if name!=tn:assert s==old[name]
shutil.copy2(SRC.parent/'shoulder_operands.blend',OUT/'shoulder_operands.blend')
(OUT/'reform-plan.json').write_text(json.dumps(reform,indent=2));(OUT/'proportion-plan.json').write_text(json.dumps(plan,indent=2))
bpy.context.scene['scope']=reform['scope'];terrain['slope_reform_scope']=reform['scope']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_c.blend'))
(OUT/'geometry-evidence.json').write_text(json.dumps(dict(old=old,new=new,sites=plan['sites'],additions=plan['additions'],historical_additions_only=True,slope_reform=reform)),encoding='utf-8')
native=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);volume=bm.calc_volume(signed=True);bm.free()
 native.append(dict(name=o.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),volume_m3=volume))
groups={}
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':groups.setdefault(o.data.materials[0].name,[]).append(o)
for mat,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 if len(objects)>1:bpy.ops.object.join()
 bpy.context.object.name='island_c_'+mat
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(OUT/'island_c.glb'),export_format='GLB',use_selection=True,export_apply=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'model-report.json').write_text(json.dumps(dict(label='31h',source_basis=str(SRC.relative_to(R)),source_basis_sha256=sha(SRC),source_sha256=sha(OUT/'island_c.blend'),glb_sha256=sha(OUT/'island_c.glb'),native=native,scope=reform['scope'],replacement_faces=len(selected),stone_faces=sum(a['after']==2 for a in selected),grass_faces=sum(a['after']==0 for a in selected)),indent=2))
print('31h MATERIAL REVISION SAVED',len(selected),sum(a['after']==2 for a in selected),[m.name for m in terrain.data.materials],flush=True)
