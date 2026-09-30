from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1]
p=R/'captures/island-30g-faceted-cut-plan.json';assert not p.exists();shutil.copy2(R/'captures/island-30f-faceted-cut-plan.json',p)
s=(R/'blender/model_lantern_island_30f.py').read_text().replace('30f','30g')
needle="bm=bmesh.new();bm.from_mesh(terrain.data);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(terrain.data);bm.free()"
replacement="""bm=bmesh.new();bm.from_mesh(terrain.data);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
def cleanup_state(mesh):return dict(vertices=len(mesh.verts),edges=len(mesh.edges),faces=len(mesh.faces),nonmanifold_edges=sum(not e.is_manifold for e in mesh.edges),small_faces=sum(f.calc_area()<=1e-10 for f in mesh.faces),short_edges=sum(e.calc_length()<=1e-5 for e in mesh.edges),minimum_area=min(f.calc_area() for f in mesh.faces))
cleanup_stats={'before':cleanup_state(bm),'merge_distance_m':.000005,'degenerate_distance_m':.00001}
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000005);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00001)
bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
cleanup_stats['after']=cleanup_state(bm);(OUT/'cleanup-evidence.json').write_text(json.dumps(cleanup_stats,indent=2));bm.to_mesh(terrain.data);bm.free()
print('30g numerical cleanup '+json.dumps(cleanup_stats),flush=True)"""
assert needle in s;s=s.replace(needle,replacement).replace("plan.update(boolean_solver=","plan.update(cleanup_statistics=cleanup_stats,boolean_solver=")
p=R/'blender/model_lantern_island_30g.py';assert not p.exists();p.write_text(s)
for a,b in [('captures/check_island_30f.py','captures/check_island_30g.py'),('tools/render_lantern_island_30f.py','tools/render_lantern_island_30g.py')]:
    p=R/b;assert not p.exists();p.write_text((R/a).read_text().replace('30f','30g'))
print('30g prepared with measured micron-scale degenerate cleanup; original gates retained')
