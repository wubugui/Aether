"""Locally grade the editable 23g headland, retaining its eleven separate rock shoulders."""
from pathlib import Path
import bpy,bmesh,json,sys,hashlib,shutil,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
label=sys.argv[sys.argv.index('--')+1]
OUT=ROOT/'captures'/('village_grading_study_'+label);assert not OUT.exists();OUT.mkdir()
source=ROOT/'captures/headland_study_23g/mainland_headland.blend'
design_path=ROOT/'captures'/('village_grading_design_'+label)/'grading.json'
design=json.loads(design_path.read_text(encoding='utf-8'))
assert hashlib.sha256((ROOT/'captures/headland_study_23g/mainland_headland.glb').read_bytes()).hexdigest()==design['source_headland_glb_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source))
core=bpy.data.objects['Mainland headland continuous bedrock and grass terraces']
assert all(abs(core.matrix_world[i][j]-(1 if i==j else 0))<1e-8 for i in range(4) for j in range(4))
old_vertices=[v.co.copy() for v in core.data.vertices]
top_faces=[p for p in core.data.polygons if p.normal.z>1e-6]
bottom_faces=[p for p in core.data.polygons if p.normal.z< -1e-6]
top=BVHTree.FromPolygons(old_vertices,[list(p.vertices) for p in top_faces],all_triangles=False)
bottom=BVHTree.FromPolygons(old_vertices,[list(p.vertices) for p in bottom_faces],all_triangles=False)
flat_vertices=[Vector((v.x,v.y,0)) for v in old_vertices]
flat_top=BVHTree.FromPolygons(flat_vertices,[list(p.vertices) for p in top_faces],all_triangles=False)
flat_bottom=BVHTree.FromPolygons(flat_vertices,[list(p.vertices) for p in bottom_faces],all_triangles=False)
whole=BVHTree.FromPolygons(old_vertices,[list(p.vertices) for p in core.data.polygons],all_triangles=False)
fallbacks=[]
def hit(surface,x,y,upper):
    co,normal,index,distance=surface.ray_cast(Vector((x,y,100 if upper else -100)),Vector((0,0,-1 if upper else 1)),300)
    if co is None:
        # Planar noding rounds at 10 micrometres. At an outer edge only, permit
        # that bounded horizontal rounding, recording the actual displacement.
        flat=flat_top if upper else flat_bottom
        co,normal,index,distance=flat.find_nearest(Vector((x,y,0)))
        error=math.hypot(co.x-x,co.y-y) if co is not None else 1e9
        assert error<.0001,('Source terrain ray missed',x,y,upper,error)
        fallbacks.append({'xz_local':[x,-y],'upper':upper,'horizontal_error_m':error})
        face=(top_faces if upper else bottom_faces)[index];assert len(face.vertices)==3
        a,b,c=[old_vertices[i] for i in face.vertices]
        denominator=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
        u=((b.y-c.y)*(co.x-c.x)+(c.x-b.x)*(co.y-c.y))/denominator
        v=((c.y-a.y)*(co.x-c.x)+(a.x-c.x)*(co.y-c.y))/denominator
        co.z=u*a.z+v*b.z+(1-u-v)*c.z
    return co.z,index
vertices=[];bottom_vertices=[];changes=[]
for (x,z),constraints in zip(design['vertices_xz_local'],design['grading_constraints']):
    old_height,_=hit(top,x,-z,True);bottom_height,_=hit(bottom,x,-z,False)
    height=old_height
    for ceiling,weight in constraints:height=min(height,old_height+weight*(min(old_height,ceiling)-old_height))
    assert height>bottom_height+.5
    vertices.append((x,-z,height));bottom_vertices.append((x,-z,bottom_height))
    if abs(height-old_height)>1e-5:changes.append({'local_xz':[x,z],'before_y':old_height,'after_y':height,'cut_m':old_height-height})
n=len(vertices);faces=[];material_ids=[]
for tri in design['triangles']:
    center=sum((Vector(vertices[i]) for i in tri),Vector())/3
    _,top_index=hit(top,center.x,center.y,True)
    faces.append(tuple(reversed(tri)));material_ids.append(top_faces[top_index].material_index)
    faces.append(tuple(i+n for i in tri));material_ids.append(bottom_faces[0].material_index)
for a,b in design['border_edges']:
    faces.append((a,b,b+n,a+n))
    center=(Vector(vertices[a])+Vector(vertices[b])+Vector(bottom_vertices[a])+Vector(bottom_vertices[b]))/4
    _,_,index,_=whole.find_nearest(center);material_ids.append(core.data.polygons[index].material_index)
materials=list(core.data.materials)
mesh=bpy.data.meshes.new('Locally graded original headland with conforming street boundaries')
mesh.from_pydata(vertices+bottom_vertices,[],faces);mesh.update()
for material in materials:mesh.materials.append(material)
for face,material in zip(mesh.polygons,material_ids):face.material_index=material
core.data=mesh
core['village_grading_label']=label
core['source_23g_sha256']=design['source_headland_glb_sha256']
parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(parts)==12
checks=[]
for obj in parts:
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    bmesh.ops.dissolve_degenerate(bm,dist=.00001,edges=list(bm.edges))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
    issues=[]
    if any(not e.is_manifold for e in bm.edges):issues.append('nonmanifold edge')
    if any(f.calc_area()<1e-9 for f in bm.faces):issues.append('zero area')
    volume=bm.calc_volume(signed=True)
    if volume<=0:issues.append('nonpositive volume')
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    checks.append({'name':obj.name,'volume_m3':volume,'issues':issues})
report={'label':label,'source_blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_glb_sha256':design['source_headland_glb_sha256'],'paving_design_sha256':design['paving_design_sha256'],'parts':checks,'changed_vertices':changes,'edge_rounding_fallbacks':fallbacks,'passed':not any(p['issues'] for p in checks),'scope':'Editable local ground cuts under authored road bands. Original triangles constrained in planar subdivision; native and actual GPU envelope checks still required. Production unchanged.'}
(OUT/'build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
shutil.copy2(design_path,OUT/'grading-design.json');shutil.copy2(__file__,OUT/'builder.py')
assert report['passed'],checks
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'mainland_headland.blend'))
# Join an export copy only; the saved native scene retains all twelve components.
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:obj.select_set(True)
bpy.context.view_layer.objects.active=core;bpy.ops.object.join()
bpy.ops.export_scene.gltf(filepath=str(OUT/'mainland_headland.glb'),export_format='GLB',use_selection=True,export_apply=True)
report['source_sha256']=hashlib.sha256((OUT/'mainland_headland.blend').read_bytes()).hexdigest()
report['glb_sha256']=hashlib.sha256((OUT/'mainland_headland.glb').read_bytes()).hexdigest()
(OUT/'build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('LOCAL GRADING BUILT',len(changes),'changed vertices; original11 rock components retained',flush=True)
