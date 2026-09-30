from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'blender/model_lantern_island_30e.py').read_text().replace("OUT=R/'captures/lantern_island_study_30e'","OUT=R/'captures/lantern_island_study_30e_diagnostic'")
start=s.index('# Explicit editable final triangles');s=s[:start]+'''
bm=bmesh.new();bm.from_mesh(terrain.data);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
bad=[dict(index=e.index,vertices=[v.index for v in e.verts],coords=[list(v.co) for v in e.verts],faces=[f.index for f in e.link_faces],length=e.calc_length()) for e in bm.edges if not e.is_manifold]
before=dict(vertices=len(bm.verts),edges=len(bm.edges),faces=len(bm.faces),bad_edges=bad)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'failed-shell.blend'))
bm2=bm.copy();bmesh.ops.remove_doubles(bm2,verts=list(bm2.verts),dist=.00001);bmesh.ops.dissolve_degenerate(bm2,edges=list(bm2.edges),dist=.000001);bmesh.ops.recalc_face_normals(bm2,faces=list(bm2.faces));bm2.verts.ensure_lookup_table();bm2.edges.ensure_lookup_table();bm2.faces.ensure_lookup_table()
after=dict(vertices=len(bm2.verts),edges=len(bm2.edges),faces=len(bm2.faces),bad_edges=[dict(coords=[list(v.co) for v in e.verts],faces=len(e.link_faces),length=e.calc_length()) for e in bm2.edges if not e.is_manifold],min_face_area=min(f.calc_area() for f in bm2.faces),volume=bm2.calc_volume(signed=True))
(OUT/'diagnostic.json').write_text(json.dumps(dict(before=before,after_10micrometer_weld=after,cutters=cutters),indent=2));bm.free();bm2.free();print('30e DIAGNOSTIC',len(bad),len(after['bad_edges']),flush=True)
'''
p=R/'blender/diagnose_lantern_island_30e.py';assert not p.exists();p.write_text(s)
print(p)
