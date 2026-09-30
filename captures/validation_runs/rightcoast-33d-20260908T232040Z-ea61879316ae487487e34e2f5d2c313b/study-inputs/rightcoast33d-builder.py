"""Constrained local terrain retopology with a real low bay and broad landward slope."""
from pathlib import Path
import bpy,bmesh,json,hashlib,shutil,numpy as np,math
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
R=Path(__file__).resolve().parents[1];OUT=R/'captures/rightcoast_study_33d';assert not OUT.exists();OUT.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
path=R/'captures/rightcoast33d-design-plan.json';plan=json.loads(path.read_text(encoding='utf-8'));source=R/plan['source'];assert sha(source)==plan['source_sha256'];shutil.copy2(path,OUT/'design-plan.json');shutil.copy2(__file__,OUT/'builder.py')
bpy.ops.wm.open_mainfile(filepath=str(source));obj=bpy.data.objects[plan['object']];oldv=[tuple(v.co) for v in obj.data.vertices];oldp=[tuple(p.vertices) for p in obj.data.polygons];oldmat=[p.material_index for p in obj.data.polygons]
def inside_loop(p,loop):
 x,y=p;inside=False
 for a,b in zip(loop,loop[1:]+loop[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
def contains(p,geom):
 rings=geom['coordinates'];return inside_loop(p,list(rings[0])) and not any(inside_loop(p,list(h)) for h in rings[1:])
pv,pe,pt,_,_,_=delaunay_2d_cdt([Vector(p) for p in plan['points']],plan['edges'],[],0,1e-6)
tris=[tuple(f) for f in pt if contains(tuple(sum((pv[i] for i in f),Vector((0,0)))/3),plan['patch'])];assert tris and all(len(f)==3 for f in tris)
used=sorted({i for f in tris for i in f});lut={i:j for j,i in enumerate(used)};v=np.array([tuple(pv[i]) for i in used]);ts=[tuple(lut[i] for i in f) for f in tris];constraints={};mapping={};source_changes=[]
for c in plan['boundary_constraints']:
 point=np.array(plan['points'][c['point']]);distance=np.linalg.norm(v-point,axis=1);i=int(np.argmin(distance));assert distance[i]<2e-5
 constraints[i]=c['height'];mapping[i]=c['source_vertex']
 if abs(c['height']-oldv[c['source_vertex']][2])>1e-7:source_changes.append(c['source_vertex'])
for i,p in enumerate(v):
 if i not in constraints and contains(tuple(p),plan['floor']):constraints[i]=plan['floor_height_m']
adj=[set() for _ in v]
for f in ts:
 for a,b in zip(f,f[1:]+f[:1]):adj[a].add(b);adj[b].add(a)
free=[i for i in range(len(v)) if i not in constraints];fi={i:j for j,i in enumerate(free)};A=np.zeros((len(free),len(free)));rhs=np.zeros(len(free))
for i in free:
 j=fi[i]
 for k in adj[i]:
  w=1/max(.02,float(np.linalg.norm(v[i]-v[k])));A[j,j]+=w
  if k in fi:A[j,fi[k]]-=w
  else:rhs[j]+=w*constraints[k]
solution=np.linalg.solve(A,rhs);z=[constraints[i] if i in constraints else float(solution[fi[i]]) for i in range(len(v))]
vertices=list(oldv)
for i in range(len(v)):
 co=(float(v[i,0]),float(v[i,1]),z[i])
 if i in mapping:vertices[mapping[i]]=(oldv[mapping[i]][0],oldv[mapping[i]][1],z[i])
 else:mapping[i]=len(vertices);vertices.append(co)
selected=set(plan['selected_polygons']);faces=[p for i,p in enumerate(oldp) if i not in selected];mats=[m for i,m in enumerate(oldmat) if i not in selected]
for f in ts:
 ids=tuple(mapping[i] for i in f);a,b,c=[Vector(vertices[i]) for i in ids]
 if (b-a).cross(c-a).z<0:ids=tuple(reversed(ids))
 faces.append(ids);center=sum((Vector(vertices[i]) for i in ids),Vector())/3;mats.append(1 if contains((center.x,center.y),plan['floor']) else 4)
mesh=bpy.data.meshes.new('33d broad bay terrain with constrained low shore and landward slope');mesh.from_pydata(vertices,[],faces);mesh.update()
for m in obj.data.materials:mesh.materials.append(m)
for p,mi in zip(mesh.polygons,mats):p.material_index=mi
obj.data=mesh
# Lower just the low rock shoulder where it intersects the explicit working shore.
for rock in bpy.context.scene.objects:
 if rock.type!='MESH' or rock==obj:continue
 for p in rock.data.vertices:
  if p.co.z>0 and contains((p.co.x,p.co.y),plan['floor']):p.co.z=min(p.co.z,1.6)
checks=[]
for o in [x for x in bpy.context.scene.objects if x.type=='MESH']:
 bm=bmesh.new();bm.from_mesh(o.data);unused=[v for v in bm.verts if not v.link_faces]
 if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update();issues=[]
 if any(not e.is_manifold for e in bm.edges):issues.append('nonmanifold')
 if any(f.calc_area()<1e-9 for f in bm.faces):issues.append('degenerate')
 volume=bm.calc_volume(signed=True)
 if volume<=0:issues.append('nonpositive')
 bm.to_mesh(o.data);bm.free();o.data.update();checks.append(dict(name=o.name,vertices=len(o.data.vertices),polygons=len(o.data.polygons),volume_m3=volume,issues=issues))
report=dict(label='33d',scope=plan['scope'],immediate_source_blend_sha256=sha(source),immediate_source_glb_sha256=sha(source.with_suffix('.glb')),parts=checks,passed=not any(p['issues'] for p in checks),production_modified=False,design_plan_sha256=sha(path),retopology=dict(old_polygons_removed=len(selected),new_triangles=len(ts),harmonic_free_points=len(free),source_boundary_height_changes=source_changes,minimum_patch_height=min(z),maximum_patch_height=max(z)))
(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'mainland_headland.blend'));assert report['passed'],checks
bpy.ops.object.select_all(action='DESELECT');parts=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=obj;bpy.ops.object.join();bpy.ops.export_scene.gltf(filepath=str(OUT/'mainland_headland.glb'),export_format='GLB',use_selection=True,export_apply=True)
report.update(source_sha256=sha(OUT/'mainland_headland.blend'),glb_sha256=sha(OUT/'mainland_headland.glb'));(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');assert sha(source)==plan['source_sha256'];print('33d native ready',json.dumps(report),flush=True)
