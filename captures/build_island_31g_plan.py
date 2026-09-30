from pathlib import Path
import json, numpy as np, hashlib
from scipy.spatial import Delaunay
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'captures/island-31g-cut-patch-full-depth.json').read_text());d=json.loads((R/'captures/island-31g-disk-full-depth.json').read_text())
v=np.array(m['vertices']);boundary=d['boundary'];uv=d['uv'];interior=d['interior']
design=[('high cross shoulder',[-5,6,8],[-6.8,8.5,8.1]),('middle east return',[-3,11,5],[-1,12,6.1]),('low west blunt root',[-8,12,2],[-9,17,2.8]),('east sea nose',[0,15,3],[2,20,1.4]),('west broad flank',[-10,7,4],[-14,10,5.4]),('high east fold',[0,10,8],[1,9.5,8.2]),('submerged rear base',[-5,15,-5.85],[-6,20,-5.85]),('outer rear shoulder',[-5,24,1],[-4,24,.65])]
controls=[];taken=set()
for name,near,xyz in design:
 i=min((j for j in interior if j not in taken),key=lambda j:np.linalg.norm(v[j]-near));taken.add(i)
 controls.append(dict(name=name,old_vertex=i,before=v[i].tolist(),xyz=xyz,uv=uv[str(i)]))
xy=np.array([uv[str(i)] for i in boundary]+[a['uv'] for a in controls]);xyz=np.array([v[i] for i in boundary]+[a['xyz'] for a in controls]);tri=Delaunay(xy).simplices.tolist()
# Repair physical collinear boundary ears by a legal diagonal flip in the disk.
def area(f):return np.linalg.norm(np.cross(xyz[f[1]]-xyz[f[0]],xyz[f[2]]-xyz[f[0]]))/2
for _ in range(200):
 bad=next((i for i,f in enumerate(tri) if area(f)<1e-8),None)
 if bad is None:break
 f=tri[bad];fixed=False
 for j,g in enumerate(tri):
  if j==bad:continue
  common=set(f)&set(g)
  if len(common)!=2:continue
  a,b=common;c=next(x for x in f if x not in common);h=next(x for x in g if x not in common)
  cross=lambda a,b,c:np.cross(xy[b]-xy[a],xy[c]-xy[a]).item()
  if cross(c,h,a)*cross(c,h,b)>=-1e-14:continue
  nf=[c,h,a];ng=[h,c,b]
  if min(area(nf),area(ng))<1e-8:continue
  tri[bad]=nf;tri[j]=ng;fixed=True;break
 assert fixed,('unrepairable ear',bad,f,area(f))
assert min(area(f) for f in tri)>1e-8
for f in tri:
 if np.cross(xy[f[1]]-xy[f[0]],xy[f[2]]-xy[f[0]])<0:f.reverse()
plan=dict(scope='31g replace rear slope plus submerged cleft with an actual native disk retopology. Remove448 source split faces and every interior old edge. Retain70 boundary vertices exactly; reconnect with8 authored cross-slope/root controls and wide triangles. Disk UV is connectivity only; physical self-intersection and occupied support are separately tested.',source='captures/lantern_island_study_31f/island_c.blend',cut_mesh='captures/island-31g-cut-patch-full-depth.json',cut_mesh_sha256=hashlib.sha256((R/'captures/island-31g-cut-patch-full-depth.json').read_bytes()).hexdigest(),selected_faces=d['selected_faces'],boundary=boundary,interior=interior,controls=controls,replacement_local_vertices=xyz.tolist(),replacement_local_triangles=tri,parameterization=d['parameterization'],actual_moved_vertices=[],actual_divisions=m['planes'])
(R/'captures/island-31g-slope-reform-plan.json').write_text(json.dumps(plan,indent=2))
print(json.dumps(dict(old_faces=len(d['selected_faces']),new_faces=len(tri),controls=controls,min_triangle_area_m2=min(area(f) for f in tri)),indent=2))
for a,b in [('blender/model_lantern_island_31f.py','blender/model_lantern_island_31g.py'),('captures/check_island_31f.py','captures/check_island_31g.py'),('captures/make_island_31f_authoring_workspace.py','captures/make_island_31g_authoring_workspace.py'),('tools/render_lantern_island_31f.py','tools/render_lantern_island_31g.py'),('captures/audit_island_31f_runtime.py','captures/audit_island_31g_runtime.py')]:
 p=R/b;assert not p.exists();s=(R/a).read_text().replace('31f','31g')
 if b.startswith('blender/'):
  s=s.replace("SRC=R/'captures/lantern_island_study_31e/island_c.blend'","SRC=R/'captures/lantern_island_study_31f/island_c.blend'")
  start=s.index('bm=bmesh.new();bm.from_mesh(terrain.data);divisions=[]');end=s.index('native=[]',start)
  s=s[:start]+'''cutpath=R/reform['cut_mesh'];assert hashlib.sha256(cutpath.read_bytes()).hexdigest()==reform['cut_mesh_sha256']
cut=json.loads(cutpath.read_text());deleted=set(reform['selected_faces']);verts=cut['vertices'];boundary=reform['boundary'];n=len(boundary)
mapping=boundary+list(range(len(verts),len(verts)+len(reform['controls'])))
verts=verts+[a['xyz'] for a in reform['controls']]
faces=[f for i,f in enumerate(cut['polygons']) if i not in deleted]+[[mapping[j] for j in f] for f in reform['replacement_local_triangles']]
materials=[x for i,x in enumerate(cut['materials']) if i not in deleted]+[0]*len(reform['replacement_local_triangles'])
used=sorted({i for f in faces for i in f});compact={a:i for i,a in enumerate(used)}
mesh=bpy.data.meshes.new('31g continuous broad rear shell');mesh.from_pydata([verts[i] for i in used],[],[[compact[i] for i in f] for f in faces]);mesh.update()
for mat in terrain.data.materials:mesh.materials.append(mat)
for f,mat in zip(mesh.polygons,materials):f.material_index=mat;f.use_smooth=False
terrain.data=mesh
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
assert all(e.is_manifold for e in bm.edges);assert all(f.calc_area()>1e-10 for f in bm.faces)
bm.to_mesh(mesh);bm.free();moved=[];divisions=cut['planes']
'''+s[end:]
  s=s.replace("retained_source='31e original and union rear exterior sculpted together including local sea mouth'","retained_source='31f occupied upper support retained; rear and submerged mouth replaced by actual cross-seam retopology'")
  s=s.replace('Direct native sculpt of high/mid/sea-root using three bounded authored local displacements.','Native cross-seam rear shell retopology with editable authored controls.')
 if b.startswith('tools/'):
  s=s.replace('C/D31g locally sculpt31e original high flank, middle junction and seaward mouth with three authored bounded displacements; no new filler or repeated bisection.','C/D31g replace448 cut rear faces with82 cross-seam triangles using8 controls; retain true upper support and rebuild submerged cleft. New topology, not another sculpt or filler.')
 p.write_text(s)
