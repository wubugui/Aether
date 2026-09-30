from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
intake=json.loads((R/'captures/island-31i-control-intake.json').read_text())
old=json.loads((R/'captures/lantern_island_study_31h/reform-plan.json').read_text())
positions={1108:[-14,10,6.2],1105:[.6,13.2,6.4],1106:[-10.5,18,3.5],1107:[3.2,20,1.7],1111:[-4.5,23,2.0]}
changes=[dict(index=a['actual31h_vertex'],name=a['name'],before=a['xyz'],after=positions[a['actual31h_vertex']]) for a in intake['controls'] if a['actual31h_vertex'] in positions]
bands=[dict(name='west short tilted shelf',face_vertices=[1108,1104,1106],edge_splits=[dict(edge=[1108,1106],ratio=.45,xyz=[-13,13.5,6.1]),dict(edge=[1104,1106],ratio=.40,xyz=[-7.5,12.5,7.6])]),dict(name='east lower turned shelf',face_vertices=[1109,1107,1105],edge_splits=[dict(edge=[1109,1107],ratio=.35,xyz=[2.8,13.8,7.6]),dict(edge=[1105,1107],ratio=.55,xyz=[2.4,17,6.0])])]
plan=dict(scope='31i actual short shelf bands on31h rear: split shared mesh edges and connect front lip into each whole face, making finite-width shoulder tops and separate front drops. West and east bands have different height/direction; low root controls become blunt staggered ends. No filler, no single lifted spike. Rear patch uses existing exposed-rock material; grass remains on preserved upper terrain instead of isolated triangle threshold patches.',source='captures/lantern_island_study_31h/island_c.blend',source_sha256=hashlib.sha256((R/'captures/lantern_island_study_31h/island_c.blend').read_bytes()).hexdigest(),vertex_changes=changes,bands=bands,historical_retology_plan='captures/lantern_island_study_31g/reform-plan.json',cut_mesh=old['cut_mesh'],cut_mesh_sha256=old['cut_mesh_sha256'],cut_mesh_role='Historical31g construction input only;31i edits actual31h source.',actual_moved_vertices=[],actual_divisions=[])
p=R/'captures/island-31i-slope-reform-plan.json';assert not p.exists();p.write_text(json.dumps(plan,indent=2))
for a,b in [('blender/model_lantern_island_31g.py','blender/model_lantern_island_31i.py'),('captures/check_island_31h.py','captures/check_island_31i.py'),('captures/make_island_31h_authoring_workspace.py','captures/make_island_31i_authoring_workspace.py'),('tools/render_lantern_island_31h.py','tools/render_lantern_island_31i.py'),('captures/audit_island_31h_runtime.py','captures/audit_island_31i_runtime.py')]:
 p=R/b;assert not p.exists();s=(R/a).read_text(encoding='utf-8').replace('31g','31i') if b.startswith('blender/') else (R/a).read_text(encoding='utf-8').replace('31h','31i')
 if b.startswith('blender/'):
  s=s.replace("SRC=R/'captures/lantern_island_study_31f/island_c.blend'","SRC=R/'captures/lantern_island_study_31h/island_c.blend'")
  start=s.index('cutpath=R/reform');end=s.index('native=[]',start)
  s=s[:start]+'''assert hashlib.sha256(SRC.read_bytes()).hexdigest()==reform['source_sha256']
prior=json.loads((SRC.parent/'reform-plan.json').read_text());lv=prior['replacement_local_vertices'];rear_keys={tuple(sorted(tuple(Vector(lv[i])) for i in f)) for f in prior['replacement_local_triangles']}
bm=bmesh.new();bm.from_mesh(terrain.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
verts=list(bm.verts);selected=[]
for f in bm.faces:
    if tuple(sorted(tuple(v.co) for v in f.verts)) in rear_keys:f.material_index=2;selected.append(f)
assert len(selected)==84
moved=[]
for change in reform['vertex_changes']:
    v=verts[change['index']];assert (v.co-Vector(change['before'])).length<1e-5
    moved.append(dict(before=list(v.co),after=change['after'],index=change['index']))
    v.co=change['after']
splits=[]
for band in reform['bands']:
    wanted={verts[i] for i in band['face_vertices']};face=next(f for f in bm.faces if set(f.verts)==wanted)
    new=[]
    for step in band['edge_splits']:
        a,b=[verts[i] for i in step['edge']];edge=next(e for e in a.link_edges if b in e.verts)
        _,v=bmesh.utils.edge_split(edge,a,step['ratio']);before=list(v.co);v.co=step['xyz'];new.append(v)
        splits.append(dict(name=band['name'],source_edge=step['edge'],ratio=step['ratio'],linear_before=before,after=list(v.co)))
    newface,_=bmesh.utils.face_split(face,new[0],new[1]);newface.material_index=2;face.material_index=2
    assert sorted([len(face.verts),len(newface.verts)])==[3,4]
bm.verts.index_update();bm.faces.index_update()
reform['actual_band_split_points']=splits
reform['untriangulated_shoulder_faces']=[dict(vertices=[list(v.co) for v in f.verts],area_m2=f.calc_area()) for f in bm.faces if len(f.verts)==4 and all(v.co.z>3 for v in f.verts)]
bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
assert all(e.is_manifold for e in bm.edges);assert all(f.calc_area()>1e-10 for f in bm.faces)
bm.to_mesh(terrain.data);bm.free();divisions=[]
'''+s[end:]
  s=s.replace("retained_source='31f occupied upper support retained; rear and submerged mouth replaced by actual cross-seam retopology'","retained_source='31h whole current shell with finite-width shared-edge shelf bands and staggered low roots'")
 if b.startswith('tools/'):
  start=s.index("run.manifest.update(scope=");end=s.index(",basis_run=prior.name",start)
  s=s[:start]+"run.manifest.update(scope='C/D31i genuine shared-edge shelf bands plus staggered low roots over actual31h. Five controls moved and four common-edge split points create finite shoulder tops and front drops. Real occupied support and actual geometry checks required. Unaffected native parts and full world retained.'"+s[end:]
 p.write_text(s,encoding='utf-8')
print('31i native shoulder-band plan and scoped pipeline prepared')
