"""Native cross-seam rear shell retopology with editable authored controls."""
from pathlib import Path
import bpy,bmesh,json,hashlib,shutil,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_island_study_31h/island_c.blend';OUT=R/'captures/lantern_island_study_31i'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
plan=json.loads((SRC.parent/'proportion-plan.json').read_text());reform=json.loads((R/'captures/island-31i-slope-reform-plan.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(SRC))
tn='island_c grass and exposed rock terrain'
def sig(o):return dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons])
old={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'};terrain=bpy.data.objects[tn]
shutil.copy2(SRC.parent/'shoulder_operands.blend',OUT/'shoulder_operands.blend')
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==reform['source_sha256']
prior=json.loads((SRC.parent/'reform-plan.json').read_text());lv=prior['replacement_local_vertices'];rear_keys={tuple(sorted(tuple(Vector(lv[i])) for i in f)) for f in prior['replacement_local_triangles']}
bm=bmesh.new();bm.from_mesh(terrain.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
verts=list(bm.verts);selected=[]
for f in bm.faces:
    if tuple(sorted(tuple(v.co) for v in f.verts)) in rear_keys:f.material_index=2;selected.append(f)
assert len(selected)==84
moved=[]
for change in reform['vertex_changes']:
    v=verts[change['index']];assert (v.co-Vector(change['before'])).length<1e-5
    moved.append(dict(before=list(v.co),after=change['after'],index=change['index']))
    v.co=change['after']
splits=[]
for band in reform['bands']:
    wanted={verts[i] for i in band['face_vertices']};face=next(f for f in bm.faces if set(f.verts)==wanted)
    new=[]
    for step in band['edge_splits']:
        a,b=[verts[i] for i in step['edge']];edge=next(e for e in a.link_edges if b in e.verts)
        _,v=bmesh.utils.edge_split(edge,a,step['ratio']);before=list(v.co);v.co=step['xyz'];new.append(v)
        splits.append(dict(name=band['name'],source_edge=step['edge'],ratio=step['ratio'],linear_before=before,after=list(v.co)))
    newface,_=bmesh.utils.face_split(face,new[0],new[1]);newface.material_index=2;face.material_index=2
    assert sorted([len(face.verts),len(newface.verts)])==[3,4]
bm.verts.index_update();bm.faces.index_update()
reform['actual_band_split_points']=splits
reform['untriangulated_shoulder_faces']=[dict(vertices=[list(v.co) for v in f.verts],area_m2=f.calc_area()) for f in bm.faces if len(f.verts)==4 and all(v.co.z>3 for v in f.verts)]
bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
assert all(e.is_manifold for e in bm.edges);assert all(f.calc_area()>1e-10 for f in bm.faces)
bm.to_mesh(terrain.data);bm.free();divisions=[]
native=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges);assert all(f.calc_area()>1e-10 for f in bm.faces)
    volume=bm.calc_volume(signed=True);assert volume>0;bm.free()
    if o.name!=tn:assert sig(o)==old[o.name]
    native.append(dict(name=o.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),volume_m3=volume))
assert len(native)==19
reform.update(actual_divisions=divisions,actual_moved_vertices=moved)
plan.update(scope=reform['scope'],retained_source='31h whole current shell with finite-width shared-edge shelf bands and staggered low roots',slope_reform=reform)
(OUT/'reform-plan.json').write_text(json.dumps(reform,indent=2));(OUT/'proportion-plan.json').write_text(json.dumps(plan,indent=2))
terrain['slope_reform_scope']=reform['scope'];bpy.context.scene['scope']=reform['scope']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_c.blend'))
(OUT/'geometry-evidence.json').write_text(json.dumps(dict(old=old,new={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'},sites=plan['sites'],additions=plan['additions'],historical_additions_only=True,slope_reform=reform)),encoding='utf-8')
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
(OUT/'model-report.json').write_text(json.dumps(dict(label='31i',source_basis=str(SRC.relative_to(R)),source_basis_sha256=sha(SRC),source_sha256=sha(OUT/'island_c.blend'),glb_sha256=sha(OUT/'island_c.glb'),native=native,scope=reform['scope'],moved_vertex_count=len(moved)),indent=2))
print('31i NATIVE SLOPE REFORM SAVED; moved',len(moved),flush=True)
