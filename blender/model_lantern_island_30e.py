"""Three authored open-sided cutbacks expose existing low rock shoulders."""
from pathlib import Path
import bpy,bmesh,json,hashlib,shutil,collections
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_island_study_30d/island_c.blend';OUT=R/'captures/lantern_island_study_30e'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
plan=json.loads((SRC.parent/'proportion-plan.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(SRC))
tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths'
def sig(o):return dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons])
old={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
terrain=bpy.data.objects[tn]

input_plan=json.loads((R/'captures/island-30e-faceted-cut-plan.json').read_text())
cutters=input_plan['components'];source=input_plan['terrain_up_triangles']
def edge_distance(p,a,b):
    p,a,b=Vector(p),Vector(a),Vector(b);d=b-a;t=max(0.,min(1.,(p-a).dot(d)/max(d.length_squared,1e-20)));return (p-a-d*t).length
def inside(p,poly):
    x,y=p;yes=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if edge_distance(p,a,b)<1e-5:return True
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
    return yes
def surface(x,y):
    hits=[]
    for a,b,c in source:
        if x<min(a[0],b[0],c[0])-1e-5 or x>max(a[0],b[0],c[0])+1e-5 or y<min(a[1],b[1],c[1])-1e-5 or y>max(a[1],b[1],c[1])+1e-5:continue
        det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(det)<1e-12:continue
        u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/det;v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/det;w=1-u-v
        if min(u,v,w)>=-1e-5:hits.append(u*a[2]+v*b[2]+w*c[2])
    return max(hits) if hits else None
for spec in cutters:
    points,_,faces,_,_,_=delaunay_2d_cdt([Vector(p) for p in spec['cdt_points']],spec['cdt_edges'],[spec['cdt_outline']],1,.00001)
    faces=[list(f) for f in faces if inside(tuple(sum(points[i][k] for i in f)/len(f) for k in range(2)),spec['polygon']) and not any(inside(tuple(sum(points[i][k] for i in f)/len(f) for k in range(2)),hole) for hole in spec['holes'])]
    assert all(len(f)==3 for f in faces)
    used=sorted({i for f in faces for i in f});lookup={v:i for i,v in enumerate(used)};faces=[[lookup[i] for i in f] for f in faces]
    bottom=[];boundary_rings=[spec['polygon'],*spec['holes']];a,b,c=spec['floor_plane']
    for i in used:
        p=points[i];old_height=surface(p.x,p.y)
        distance=min(edge_distance(p,u,v) for ring in boundary_rings for u,v in zip(ring,ring[1:]+ring[:1]))
        if old_height is None:height=-1.
        else:
            weight=min(1.,distance/spec['blend_width'])
            height=(old_height+.12)*(1-weight)+min(old_height,a*p.x+b*p.y+c)*weight
        bottom.append((p.x,p.y,height))
    count=len(bottom);verts=bottom+[(x,y,40.) for x,y,_ in bottom]
    ec=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3))
    polys=[list(reversed(f)) for f in faces]+[[i+count for i in f] for f in faces]+[[a,b,b+count,a+count] for (a,b),n in ec.items() if n==1]
    mesh=bpy.data.meshes.new(spec['name']+' faceted transition cutter');mesh.from_pydata(verts,[],polys);mesh.update()
    for mat in terrain.data.materials:mesh.materials.append(mat)
    for p in mesh.polygons:p.material_index=2
    cutter=bpy.data.objects.new(spec['name'],mesh);bpy.context.collection.objects.link(cutter)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free()
    spec['actual_lower_vertices']=bottom;spec['actual_lower_triangles']=faces;spec['actual_cutter_geometry']=sig(cutter)
    bpy.ops.object.select_all(action='DESELECT');terrain.select_set(True);bpy.context.view_layer.objects.active=terrain
    mod=terrain.modifiers.new(spec['name'],'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True);print('Applied native faceted cutback '+spec['name'],flush=True)
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
plan.update(scope='30e southern/eastern visible main-slope faceted cutbacks. Real transition-bottom meshes taper from original surface to authored lower facets. Actual road/pad/tree masks subtracted with0.4m nominal margin. Complete path and17rocks retained; actual support, visible shape and runtime require checks.',cutbacks=cutters,top_vertex_count=None,core_boundary_map=None,retained_source='30d local-cut welded exterior',faceted_input_plan=input_plan)
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
(OUT/'model-report.json').write_text(json.dumps(dict(label='30e',source_basis=str(SRC.relative_to(R)),source_basis_sha256=sha(SRC),source_sha256=sha(OUT/'island_c.blend'),glb_sha256=sha(OUT/'island_c.glb'),native=native,scope=plan['scope']),indent=2))
print('30e NATIVE CUTBACKS SAVED',flush=True)
