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
for vertex_index,((x,z),constraints) in enumerate(zip(design['vertices_xz_local'],design['grading_constraints'])):
    old_height,_=hit(top,x,-z,True);bottom_height,_=hit(bottom,x,-z,False)
    height=old_height
    for ceiling,weight in constraints:
        target=ceiling if design.get('earth_fill_enabled',False) else min(old_height,ceiling)
        proposed=old_height+weight*(target-old_height)
        height=proposed if len(constraints)==1 else min(height,proposed)
    if 'resolved_heights' in design:
        assert abs(old_height-design['original_actual_heights'][vertex_index])<.002,('Original GLB/native mismatch',vertex_index,old_height,design['original_actual_heights'][vertex_index])
        height=design['resolved_heights'][vertex_index]
    assert height>bottom_height+.5
    vertices.append((x,-z,height));bottom_vertices.append((x,-z,bottom_height))
    if abs(height-old_height)>1e-5:changes.append({'local_xz':[x,z],'before_y':old_height,'after_y':height,'cut_m':max(0.,old_height-height),'fill_m':max(0.,height-old_height)})
n=len(vertices)
# The road subdivision belongs to the upper surface only. Keep the original
# closed underside and all original side-wall faces instead of tessellating
# thousands of tiny road contour intersections into a flat buried bottom.
counts={}
for p in top_faces:
    ids=list(p.vertices)
    for a,b in zip(ids,ids[1:]+ids[:1]):
        edge=tuple(sorted((a,b)));counts[edge]=counts.get(edge,0)+1
old_border={i for edge,count in counts.items() if count==1 for i in edge}
new_border={i for edge in design['border_edges'] for i in edge}
mesh_vertices=[tuple(v) for v in old_vertices];mapping={};border_errors=[]
for i,co in enumerate(vertices):
    if i in new_border:
        nearest=min(old_border,key=lambda j:(old_vertices[j].x-co[0])**2+(old_vertices[j].y-co[1])**2)
        error=math.hypot(old_vertices[nearest].x-co[0],old_vertices[nearest].y-co[1])
        assert error<.0001,('New coastline vertex',i,error)
        mapping[i]=nearest;border_errors.append(error)
    else:mapping[i]=len(mesh_vertices);mesh_vertices.append(co)
assert {mapping[i] for i in new_border}==old_border
faces=[tuple(p.vertices) for p in core.data.polygons if p.normal.z<=1e-6]
material_ids=[p.material_index for p in core.data.polygons if p.normal.z<=1e-6]
for tri in design['triangles']:
    center=sum((Vector(vertices[i]) for i in tri),Vector())/3
    _,top_index=hit(top,center.x,center.y,True)
    faces.append(tuple(mapping[i] for i in reversed(tri)));material_ids.append(top_faces[top_index].material_index)
materials=list(core.data.materials)
mesh=bpy.data.meshes.new('Locally graded original headland with conforming street boundaries')
mesh.from_pydata(mesh_vertices,[],faces);mesh.update()
for material in materials:mesh.materials.append(material)
for face,material in zip(mesh.polygons,material_ids):face.material_index=material
core.data=mesh
core['village_grading_label']=label
core['source_23g_sha256']=design['source_headland_glb_sha256']
parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(parts)==12
checks=[]
for obj in parts:
    bm=bmesh.new();bm.from_mesh(obj.data)
    unused=[v for v in bm.verts if not v.link_faces]
    if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    # Source-edge/road-boundary intersections can leave sub-0.1mm slivers.
    # Collapse those geometrically before retaining the unchanged area gate.
    bmesh.ops.dissolve_degenerate(bm,dist=.0001,edges=list(bm.edges))
    collapsed_slivers=[]
    for iteration in range(3):
        tiny=[f for f in bm.faces if f.calc_area()<1e-9]
        if not tiny:break
        for face in tiny:
            if not face.is_valid:continue
            edge=min(face.edges,key=lambda e:e.calc_length())
            assert edge.calc_length()<.002,('Unexpected large degenerate face',obj.name,edge.calc_length())
            collapsed_slivers.append({'edge_length_m':edge.calc_length(),'vertices':[list(v.co) for v in edge.verts]})
            bmesh.ops.collapse(bm,edges=[edge],uvs=False)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
    issues=[]
    if any(not e.is_manifold for e in bm.edges):issues.append('nonmanifold edge')
    if any(f.calc_area()<1e-9 for f in bm.faces):issues.append('zero area')
    volume=bm.calc_volume(signed=True)
    if volume<=0:issues.append('nonpositive volume')
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    checks.append({'name':obj.name,'volume_m3':volume,'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),'issues':issues,'collapsed_sub2mm_slivers':collapsed_slivers,'small_faces':[{'area':p.area,'vertices':[list(obj.data.vertices[i].co) for i in p.vertices]} for p in obj.data.polygons if p.area<1e-9]})
report={'label':label,'source_blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_glb_sha256':design['source_headland_glb_sha256'],'paving_design_sha256':design['paving_design_sha256'],'parts':checks,'changed_vertices':changes,'edge_rounding_fallbacks':fallbacks,'original_border_vertices_reused':len(old_border),'maximum_border_mapping_error_before_reuse_m':max(border_errors),'passed':not any(p['issues'] for p in checks),'earth_fill_enabled':design.get('earth_fill_enabled',False),'scope':'Editable local cut-and-fill terrain around authored road bands. Original triangles constrained in planar subdivision; original underside, side walls and exact border vertices retained. Native and actual GPU envelope checks still required. Production unchanged.'}
(OUT/'build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
shutil.copy2(design_path,OUT/'grading-design.json');shutil.copy2(__file__,OUT/'builder.py')
if not report['passed']:bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'rejected-headland.blend'))
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
