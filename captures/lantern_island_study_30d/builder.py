"""Three authored open-sided cutbacks expose existing low rock shoulders."""
from pathlib import Path
import bpy,bmesh,json,hashlib,shutil
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_island_study_30c/island_c.blend';OUT=R/'captures/lantern_island_study_30d'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
plan=json.loads((SRC.parent/'proportion-plan.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(SRC))
tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths'
def sig(o):return dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons])
old={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
terrain=bpy.data.objects[tn]
cutters=[
 dict(name='West short recessed shoulder',rock='West broken shoulder',polygon=[[-38,-14],[-26,-16],[-18,-14],[-14,-10],[-15,-7],[-22,-5],[-37,-4]],floor_plane=[.20,0.,7.0]),
 dict(name='Southwest staggered ledge',rock='Southwest leaning crag',polygon=[[-36,-34],[-22,-34],[-15,-27],[-14,-22],[-16,-18],[-20,-17],[-27,-20],[-38,-26]],floor_plane=[.12,.12,7.16]),
 dict(name='North low stepped root',rock='North broken ridge',polygon=[[-9,37],[5,36],[8,27],[5,21],[1,15],[-3,15],[-7,20]],floor_plane=[.05,-.16,5.13])]
for spec in cutters:
    poly=spec['polygon'];a,b,c=spec['floor_plane'];nv=len(poly)
    verts=[(x,y,a*x+b*y+c) for x,y in poly]+[(x,y,40.) for x,y in poly]
    faces=[list(reversed(range(nv))),list(range(nv,nv*2))]+[[i,(i+1)%nv,(i+1)%nv+nv,i+nv] for i in range(nv)]
    mesh=bpy.data.meshes.new(spec['name']);mesh.from_pydata(verts,[],faces);mesh.update()
    for mat in terrain.data.materials:mesh.materials.append(mat)
    for p in mesh.polygons:p.material_index=2
    cutter=bpy.data.objects.new(spec['name'],mesh);bpy.context.collection.objects.link(cutter)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free()
    bpy.ops.object.select_all(action='DESELECT');terrain.select_set(True);bpy.context.view_layer.objects.active=terrain
    mod=terrain.modifiers.new(spec['name'],'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    print('Applied native cutback: '+spec['name'],flush=True)
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
plan.update(scope='30d three true Blender Boolean cutbacks of30c main exterior expose existing West/Southwest/North short shoulders. Actual17rock positions/shape and complete path preserved; occupied support and actual collision require independent checks. No blanket outward rock move.',cutbacks=cutters,top_vertex_count=None,core_boundary_map=None,retained_source='30c welded exterior')
(OUT/'proportion-plan.json').write_text(json.dumps(plan,indent=2))
bpy.context.scene['scope']=plan['scope'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_c.blend'))
(OUT/'geometry-evidence.json').write_text(json.dumps(dict(old=old,new={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'},sites=plan['sites'],cutbacks=cutters)),encoding='utf-8')
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
(OUT/'model-report.json').write_text(json.dumps(dict(label='30d',source_basis=str(SRC.relative_to(R)),source_basis_sha256=sha(SRC),source_sha256=sha(OUT/'island_c.blend'),glb_sha256=sha(OUT/'island_c.glb'),native=native,scope=plan['scope']),indent=2))
print('30d NATIVE CUTBACKS SAVED',flush=True)
