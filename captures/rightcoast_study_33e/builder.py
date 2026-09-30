"""Reform four actually visible old grading transitions with bounded native geometry changes."""
from pathlib import Path
import bpy,bmesh,json,hashlib,shutil,numpy as np
R=Path(__file__).resolve().parents[1];OUT=R/'captures/rightcoast_study_33e';assert not OUT.exists();OUT.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=R/'captures/rightcoast_study_33b/mainland_headland.blend';domain_path=R/'reviews/round-33d-visible-transition-domain.json';domain=json.loads(domain_path.read_text(encoding='utf-8'));assert sha(source)==domain['bindings']['actual_source_sha256']
shutil.copy2(__file__,OUT/'builder.py');shutil.copy2(domain_path,OUT/'transition-domain.json');bpy.ops.wm.open_mainfile(filepath=str(source));obj=bpy.data.objects['Mainland headland continuous bedrock and grass terraces'];old=np.array([list(v.co) for v in obj.data.vertices]);free=[]
for v in domain['one_ring_vertices']:
 i=v['vertex_index'];assert np.max(abs(old[i]-np.array(v['xyz'])))<1e-7
 if v['can_move_without_splitting_any_occupied_incident_face']:free.append(i)
assert len(free)==86
fi={i:j for j,i in enumerate(free)};adj=[set() for _ in old]
for p in obj.data.polygons:
 ids=list(p.vertices)
 if min(old[ids,2])<=0:continue
 for a,b in zip(ids,ids[1:]+ids[:1]):adj[a].add(b);adj[b].add(a)
A=np.zeros((len(free),len(free)));rhs=np.zeros(len(free))
for i in free:
 j=fi[i];assert adj[i]
 for k in adj[i]:
  w=1/max(.025,float(np.linalg.norm(old[i,:2]-old[k,:2])));A[j,j]+=w
  if k in fi:A[j,fi[k]]-=w
  else:rhs[j]+=w*old[k,2]
result=np.linalg.solve(A,rhs);changed=[]
for i,h in zip(free,result):
 obj.data.vertices[i].co.z=float(h);changed.append(dict(source_vertex=i,old_xyz=old[i].tolist(),new_xyz=list(obj.data.vertices[i].co)))
obj.data.update();bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();bm.verts.index_update();selected=set(free)
eligible=[f for f in bm.faces if len(f.verts)==3 and all(v.index in selected for v in f.verts)]
eligible_set=set(eligible);edges=[e for e in bm.edges if len(e.link_faces)==2 and all(f in eligible_set for f in e.link_faces)]
beauty=bmesh.ops.beautify_fill(bm,faces=eligible,edges=edges,method='AREA')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update()
for p in obj.data.polygons:
 if not any(i in selected for i in p.vertices):continue
 if p.normal.z>.89:p.material_index=3
 elif p.normal.z>.80:p.material_index=4
 else:p.material_index=1 if p.normal.x<-.2 else 0
checks=[]
for o in [x for x in bpy.context.scene.objects if x.type=='MESH']:
 bm=bmesh.new();bm.from_mesh(o.data);issues=[]
 if any(not e.is_manifold for e in bm.edges):issues.append('nonmanifold')
 if any(f.calc_area()<1e-9 for f in bm.faces):issues.append('degenerate')
 volume=bm.calc_volume(signed=True)
 if volume<=0:issues.append('nonpositive')
 bm.free();checks.append(dict(name=o.name,vertices=len(o.data.vertices),polygons=len(o.data.polygons),volume_m3=volume,issues=issues))
scope='Reform only four visible old26b grading transition groups on33b with86 independently free vertices, retaining3 support-boundary vertices. Solve continuous elevations from surrounding actual upper neighbors and improve inner triangle diagonals. Keep11rock pieces and all bay33b geometry. No all-reference/art acceptance; production unchanged.'
report=dict(label='33e',scope=scope,immediate_source_blend_sha256=sha(source),immediate_source_glb_sha256=sha(source.with_suffix('.glb')),parts=checks,passed=not any(p['issues'] for p in checks),production_modified=False,domain_sha256=sha(domain_path),changed_vertices=changed,max_height_change_m=float(np.max(abs(result-old[free,2]))),kept_support_boundary_vertices=[3772,7152,7289],eligible_beautify_faces=len(eligible),eligible_beautify_edges=len(edges))
(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(OUT/'design-plan.json').write_text(json.dumps(dict(scope=scope,source=str(source.relative_to(R)),source_sha256=sha(source),domain_sha256=sha(domain_path),source_domain='reviews/round-33d-visible-transition-domain.json',free_vertices=free,kept_support_boundary_vertices=[3772,7152,7289]),indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'mainland_headland.blend'));assert report['passed'],checks
bpy.ops.object.select_all(action='DESELECT');parts=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=obj;bpy.ops.object.join();bpy.ops.export_scene.gltf(filepath=str(OUT/'mainland_headland.glb'),export_format='GLB',use_selection=True,export_apply=True)
report.update(source_sha256=sha(OUT/'mainland_headland.blend'),glb_sha256=sha(OUT/'mainland_headland.glb'));(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('33e native ready',report['max_height_change_m'],flush=True)
