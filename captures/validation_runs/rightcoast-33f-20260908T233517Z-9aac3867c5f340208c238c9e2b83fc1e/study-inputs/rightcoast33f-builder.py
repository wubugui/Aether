"""Combine33d bay and only the two improved33e front groups, repairing unsafe diagonal."""
from pathlib import Path
import bpy,bmesh,json,hashlib,shutil,numpy as np
R=Path(__file__).resolve().parents[1];OUT=R/'captures/rightcoast_study_33f';assert not OUT.exists();OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
source=R/'captures/rightcoast_study_33d/mainland_headland.blend';base=R/'captures/rightcoast_study_33b/mainland_headland.blend'
domain_path=R/'reviews/round-33d-visible-transition-domain.json';domain=read(domain_path);echeck=read(R/'captures/rightcoast_study_33e/native-check.json')
assert sha(base)==domain['bindings']['actual_source_sha256'];assert sha(source)==read(source.parent/'native-check.json')['source_sha256']
shutil.copy2(__file__,OUT/'builder.py');shutil.copy2(domain_path,OUT/'transition-domain.json')
name='Mainland headland continuous bedrock and grass terraces'
bpy.ops.wm.open_mainfile(filepath=str(base));oldbase=[tuple(v.co) for v in bpy.data.objects[name].data.vertices]
# Vertex-connected components of the actual one-ring faces, not a bounding rectangle.
adj={v['vertex_index']:set() for v in domain['one_ring_vertices']}
for f in domain['one_ring_faces']:
 for i in f['vertex_indices']:adj[i].update(f['vertex_indices'])
remaining=set(adj);components=[]
while remaining:
 todo=[min(remaining)];group=set()
 while todo:
  i=todo.pop()
  if i in group:continue
  group.add(i);todo.extend(adj[i]-group)
 remaining-=group;components.append(group)
chosen=set().union(*(c for c in components if c & {3756,3831}))
assert not chosen & {7148,4022},'Main-view groups must stay unchanged'
free={v['vertex_index'] for v in domain['one_ring_vertices'] if v['can_move_without_splitting_any_occupied_incident_face']} & chosen
bpy.ops.wm.open_mainfile(filepath=str(source));obj=bpy.data.objects[name];before=[tuple(v.co) for v in obj.data.vertices]
lookup={}
for v in obj.data.vertices:lookup.setdefault(tuple(v.co),[]).append(v.index)
needed=chosen|{2466,4346,4348,4350};mapping={}
for i in needed:
 matches=lookup.get(oldbase[i],[]);assert len(matches)==1,(i,matches);mapping[i]=matches[0]
changed=[]
for item in echeck['changed_vertices']:
 i=item['source_vertex']
 if i not in free:continue
 j=mapping[i];assert tuple(item['old_xyz'])==oldbase[i];obj.data.vertices[j].co=item['new_xyz']
 changed.append(dict(source_vertex=i,current_vertex=j,old_xyz=list(before[j]),new_xyz=list(obj.data.vertices[j].co)))
assert len(changed)==len(free)
selected={mapping[i] for i in free};obj.data.update();bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table();bm.verts.index_update()
original_triangles={tuple(sorted(v.index for v in f.verts)) for f in bm.faces if len(f.verts)==3}
eligible=[f for f in bm.faces if len(f.verts)==3 and all(v.index in selected for v in f.verts)];eligible_set=set(eligible)
edges=[e for e in bm.edges if len(e.link_faces)==2 and all(f in eligible_set for f in e.link_faces)]
bmesh.ops.beautify_fill(bm,faces=eligible,edges=edges,method='AREA')
bad_edge=bm.edges.get((bm.verts[mapping[4346]],bm.verts[mapping[4350]]));restored=False
if bad_edge:
 faces=list(bad_edge.link_faces);assert len(faces)==2
 assert {v.index for f in faces for v in f.verts}=={mapping[i] for i in [2466,4346,4348,4350]}
 bmesh.ops.delete(bm,geom=faces,context='FACES_ONLY');assert not bad_edge.link_faces;bm.edges.remove(bad_edge)
 for ids in [[4348,2466,4346],[4350,2466,4348]]:bm.faces.new([bm.verts[mapping[i]] for i in ids])
 restored=True
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));new_faces=[]
for f in bm.faces:
 if len(f.verts)!=3 or tuple(sorted(v.index for v in f.verts)) in original_triangles:continue
 a,b,c=[v.co for v in f.verts];area2=(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
 assert area2>1e-10,('new XY fold', [v.index for v in f.verts],area2)
 new_faces.append(dict(vertices=[v.index for v in f.verts],xy_area_m2=area2*.5))
bm.to_mesh(obj.data);bm.free();obj.data.update()
for p in obj.data.polygons:
 if not any(i in selected for i in p.vertices):continue
 p.material_index=3 if p.normal.z>.89 else 4 if p.normal.z>.80 else 1 if p.normal.x<-.2 else 0
checks=[]
for o in [o for o in bpy.context.scene.objects if o.type=='MESH']:
 bm=bmesh.new();bm.from_mesh(o.data);issues=[]
 if any(not e.is_manifold for e in bm.edges):issues.append('nonmanifold')
 if any(f.calc_area()<1e-9 for f in bm.faces):issues.append('degenerate')
 volume=bm.calc_volume(signed=True)
 if volume<=0:issues.append('nonpositive')
 bm.free();checks.append(dict(name=o.name,vertices=len(o.data.vertices),polygons=len(o.data.polygons),volume_m3=volume,issues=issues))
scope='33d actual bay retained; only two33e front connected groups transferred by exact33b XYZ mapping. Main-view groups rejected. Unsafe beautify diagonal restored. No full art/all-reference acceptance.'
plan=dict(scope=scope,source=str(source.relative_to(R)),source_sha256=sha(source),base_sha256=sha(base),domain_sha256=sha(domain_path),donor_native_check_sha256=sha(R/'captures/rightcoast_study_33e/native-check.json'),components=[sorted(c) for c in components],selected_source_vertices=sorted(free),source_to_current_vertex_mapping=mapping,restored_old_diagonal=restored)
(OUT/'design-plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
report=dict(label='33f',scope=scope,immediate_source_blend_sha256=sha(source),immediate_source_glb_sha256=sha(source.with_suffix('.glb')),parts=checks,passed=not any(p['issues'] for p in checks),production_modified=False,changed_vertices=changed,restored_old_diagonal=restored,new_topology_triangles=new_faces,max_height_change_m=max(abs(c['old_xyz'][2]-c['new_xyz'][2]) for c in changed))
(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'mainland_headland.blend'));assert report['passed'],checks
bpy.ops.object.select_all(action='DESELECT')
for o in [o for o in bpy.context.scene.objects if o.type=='MESH']:o.select_set(True)
bpy.context.view_layer.objects.active=obj;bpy.ops.object.join();bpy.ops.export_scene.gltf(filepath=str(OUT/'mainland_headland.glb'),export_format='GLB',use_selection=True,export_apply=True)
report.update(source_sha256=sha(OUT/'mainland_headland.blend'),glb_sha256=sha(OUT/'mainland_headland.glb'));(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('33f native ready',len(changed),restored,flush=True)
