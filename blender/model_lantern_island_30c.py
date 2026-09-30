"""Weld the actual terrain and rock exterior; remove the artificial soil collar."""
from pathlib import Path
import bpy,bmesh,json,hashlib,shutil
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_island_study_30b/island_c.blend';OUT=R/'captures/lantern_island_study_30c'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
plan=json.loads((SRC.parent/'proportion-plan.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(SRC))
tn='island_c grass and exposed rock terrain';cn='island_c faulted bedrock';pn='island_c terrain fitted keeper paths'
def sig(o):return dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons])
old={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
terrain=bpy.data.objects[tn];core=bpy.data.objects[cn];n=plan['top_vertex_count']
topfaces=[p for p in terrain.data.polygons if all(i<n for i in p.vertices)]
verts=[list(v.co) for v in terrain.data.vertices[:n]]+[list(v.co) for v in core.data.vertices[:54]]
faces=[list(p.vertices) for p in topfaces];materials=[p.material_index for p in topfaces]
tm=list(terrain.data.materials);cm=list(core.data.materials)
# No internal upper/lower duplicated cap and no constant-height perimeter skirt.
# The retained coast panels end at the actual top surface boundary vertices.
for p in core.data.polygons:
    if all(i>=54 for i in p.vertices):continue
    faces.append([n+i if i<54 else i-54 for i in p.vertices]);materials.append(len(tm)+p.material_index)
mesh=bpy.data.meshes.new('30c welded terrain and native rock exterior');mesh.from_pydata(verts,[],faces);mesh.update()
for m in tm+cm:mesh.materials.append(m)
for p,m in zip(mesh.polygons,materials):p.material_index=m
terrain.data=mesh;bpy.data.objects.remove(core,do_unlink=True)
native=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data)
    assert all(e.is_manifold for e in bm.edges),(o.name,'open shell')
    assert all(f.calc_area()>1e-10 for f in bm.faces),(o.name,'zero area')
    volume=bm.calc_volume(signed=True);assert volume>0,(o.name,volume)
    bm.free();native.append(dict(name=o.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),volume_m3=volume))
assert len(native)==19
actual=sig(terrain);assert actual['vertices'][:n]==old[tn]['vertices'][:n]
assert actual['polygons'][:len(topfaces)]==[f for f in old[tn]['polygons'] if all(i<n for i in f)]
assert sig(bpy.data.objects[pn])==old[pn]
plan.update(scope='30c actual terrain/main-bedrock welded exterior: remove internal duplicated cap and 0.65m perimeter collar. All745 terrain top vertices, original top triangles/materials, path, occupied pads and17 independent30b rocks retained exactly. Native whole island is19 editable mesh objects.',core_cap_offset=None,core_side_topology='54 lower-coast vertices appended after745 actual top vertices; no internal cap or collar')
(OUT/'proportion-plan.json').write_text(json.dumps(plan,indent=2))
bpy.context.scene['scope']=plan['scope'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_c.blend'))
(OUT/'geometry-evidence.json').write_text(json.dumps(dict(old=old,new={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'},sites=plan['sites'],retained_surface_vertex_count=n,retained_surface_face_count=len(topfaces))),encoding='utf-8')
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
(OUT/'model-report.json').write_text(json.dumps(dict(label='30c',source_basis=str(SRC.relative_to(R)),source_basis_sha256=sha(SRC),source_sha256=sha(OUT/'island_c.blend'),glb_sha256=sha(OUT/'island_c.glb'),native=native,scope=plan['scope']),indent=2))
print('30c WELDED NATIVE EXTERIOR SAVED',flush=True)
