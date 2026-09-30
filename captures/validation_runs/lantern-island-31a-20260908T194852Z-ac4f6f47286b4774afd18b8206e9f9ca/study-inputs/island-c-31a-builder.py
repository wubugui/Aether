"""Three authored open-sided cutbacks expose existing low rock shoulders."""
from pathlib import Path
import bpy,bmesh,json,hashlib,shutil,collections
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_island_study_30k/island_c.blend';OUT=R/'captures/lantern_island_study_31a'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
plan=json.loads((SRC.parent/'proportion-plan.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(SRC))
tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths'
def sig(o):return dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons])
old={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
terrain=bpy.data.objects[tn]

input_plan=json.loads((R/'captures/island-31a-convex-shoulder-plan.json').read_text())
authoring_scene=bpy.data.scenes.new('31a editable short rock shoulders')
specs=input_plan['components'];operands=[]
for spec in specs:
    mesh=bpy.data.meshes.new(spec['name']+' authored beveled hull')
    bm=bmesh.new()
    for v in spec['vertices']:bm.verts.new(v)
    result=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    unused=[v for v in bm.verts if not v.link_faces]
    if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
    assert bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free()
    for mat in terrain.data.materials:mesh.materials.append(mat)
    for p in mesh.polygons:p.material_index=2
    obj=bpy.data.objects.new(spec['name'],mesh);bpy.context.collection.objects.link(obj)
    copy=obj.copy();copy.data=obj.data.copy();authoring_scene.collection.objects.link(copy)
    spec['actual_operand_geometry']=sig(obj);operands.append(obj)
bpy.data.libraries.write(str(OUT/'shoulder_operands.blend'),{authoring_scene},fake_user=True)
for obj in list(authoring_scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.scenes.remove(authoring_scene)
for obj in operands:
    bpy.ops.object.select_all(action='DESELECT');terrain.select_set(True);bpy.context.view_layer.objects.active=terrain
    mod=terrain.modifiers.new(obj.name+' connected shoulder union','BOOLEAN');mod.operation='UNION';mod.solver='MANIFOLD';mod.object=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
    print('United native short convex shoulder '+obj.name,flush=True);bpy.data.objects.remove(obj,do_unlink=True)
# Explicit editable final triangles match the actual export and collision input.
bm=bmesh.new();bm.from_mesh(terrain.data);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(terrain.data);bm.free()
native=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data)
    assert all(e.is_manifold for e in bm.edges),(o.name,'open shell')
    assert all(f.calc_area()>1e-10 for f in bm.faces),(o.name,'zero face')
    volume=bm.calc_volume(signed=True);assert volume>0,(o.name,volume);bm.free()
    native.append(dict(name=o.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),volume_m3=volume))
    if o.name!=tn:assert sig(o)==old[o.name],o.name
assert len(native)==19
plan.update(boolean_solver='MANIFOLD',scope=input_plan['scope'],additions=specs,addition_input_plan=input_plan,retained_source='30k broad-cut exterior with current lower eastern tree group')
(OUT/'proportion-plan.json').write_text(json.dumps(plan,indent=2))
bpy.context.scene['scope']=plan['scope'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_c.blend'))
(OUT/'geometry-evidence.json').write_text(json.dumps(dict(old=old,new={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'},sites=plan['sites'],additions=specs)),encoding='utf-8')
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
(OUT/'model-report.json').write_text(json.dumps(dict(label='31a',source_basis=str(SRC.relative_to(R)),source_basis_sha256=sha(SRC),source_sha256=sha(OUT/'island_c.blend'),glb_sha256=sha(OUT/'island_c.glb'),native=native,scope=plan['scope']),indent=2))
print('31a NATIVE CUTBACKS SAVED',flush=True)
