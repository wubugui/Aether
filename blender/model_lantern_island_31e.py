"""Direct native rear slope reform: sparse oblique divisions and bounded shears."""
from pathlib import Path
import bpy,bmesh,json,hashlib,shutil,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_island_study_31d/island_c.blend';OUT=R/'captures/lantern_island_study_31e'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
plan=json.loads((SRC.parent/'proportion-plan.json').read_text());reform=json.loads((R/'captures/island-31e-slope-reform-plan.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(SRC))
tn='island_c grass and exposed rock terrain'
def sig(o):return dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons])
old={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'};terrain=bpy.data.objects[tn]
shutil.copy2(SRC.parent/'shoulder_operands.blend',OUT/'shoulder_operands.blend')
bm=bmesh.new();bm.from_mesh(terrain.data);domain=reform['cut_face_domain'];divisions=[]
def inside(v):return all(domain[a][0]<v.co[i]<domain[a][1] for i,a in enumerate(['x','y','z']))
for section in reform['cross_sections']:
    faces=[f for f in bm.faces if any(inside(v) for v in f.verts)]
    geom=list(set(faces)|{e for f in faces for e in f.edges}|{v for f in faces for v in f.verts})
    before=(len(bm.verts),len(bm.faces))
    bmesh.ops.bisect_plane(bm,geom=geom,dist=1e-6,plane_co=Vector(section['point']),plane_no=Vector(section['normal']),clear_inner=False,clear_outer=False)
    divisions.append(dict(name=section['name'],before=before,after=[len(bm.verts),len(bm.faces)]))
def bell(value,center,radius):
    q=abs(value-center)/radius
    return .5*(1+math.cos(math.pi*q)) if q<1 else 0.
def vertical(z,s):
    if z<=s['z_low'] or z>=s['z_high']:return 0.
    t=(z-s['z_low'])/(s['z_peak']-s['z_low']) if z<s['z_peak'] else (s['z_high']-z)/(s['z_high']-s['z_peak'])
    return .5*(1-math.cos(math.pi*t))
bm.verts.index_update();moved=[]
for v in bm.verts:
    before=list(v.co)
    for spec in reform['reforms']:
        amount=spec['amount_m']*bell(v.co.x,spec['x_center'],spec['x_radius'])*bell(v.co.y,spec['y_center'],spec['y_radius'])*vertical(v.co.z,spec)
        v.co[spec['axis']]+=amount
    delta=(v.co-Vector(before)).length
    if delta>1e-7:moved.append(dict(vertex_before_final_triangulation=v.index,before=before,after=list(v.co),distance_m=delta))
assert len(moved)>10
bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
assert all(f.calc_area()>1e-10 for f in bm.faces)
bm.to_mesh(terrain.data);bm.free()
native=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges);assert all(f.calc_area()>1e-10 for f in bm.faces)
    volume=bm.calc_volume(signed=True);assert volume>0;bm.free()
    if o.name!=tn:assert sig(o)==old[o.name]
    native.append(dict(name=o.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),volume_m3=volume))
assert len(native)==19
reform.update(actual_divisions=divisions,actual_moved_vertices=moved)
plan.update(scope=reform['scope'],retained_source='31d original and union rear exterior reformed together',slope_reform=reform)
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
(OUT/'model-report.json').write_text(json.dumps(dict(label='31e',source_basis=str(SRC.relative_to(R)),source_basis_sha256=sha(SRC),source_sha256=sha(OUT/'island_c.blend'),glb_sha256=sha(OUT/'island_c.glb'),native=native,scope=reform['scope'],moved_vertex_count=len(moved)),indent=2))
print('31e NATIVE SLOPE REFORM SAVED; moved',len(moved),flush=True)
