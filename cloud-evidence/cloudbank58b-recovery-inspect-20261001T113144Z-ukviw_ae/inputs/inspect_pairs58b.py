"""Read saved failed union only; record actual triangle intersections, no save."""
import hashlib,json,sys,time
from collections import Counter
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;B=P.parent;A=B.parent
sys.path[:0]=[str(P),str(B),str(A)]
from verify58b import mesh_data
from verify58 import distances_to_triangles
from triangle_pairs58b import narrow_phase,counterexamples
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=P/'cloud_bank58b_union.blend';before=sha(source);start=time.monotonic()
bpy.ops.wm.open_mainfile(filepath=str(source));bank=bpy.data.objects['CloudBank58B_four_root_folded_volume'];v,ids,tri=mesh_data(bank)
tree=BVHTree.FromPolygons([Vector(p) for p in v],[tuple(t) for t in ids],all_triangles=True,epsilon=0)
all_pairs=[(a,b) for a,b in tree.overlap(tree) if a<b];shared=[(a,b) for a,b in all_pairs if set(ids[a])&set(ids[b])]
candidates=[(a,b) for a,b in all_pairs if not(set(ids[a])&set(ids[b]))];rows=[]
for a,b in candidates:
    row=narrow_phase(tri[a],tri[b]);row.update(triangle_indices=[a,b],native_vertex_indices=[ids[a].tolist(),ids[b].tolist()],actual_world_triangles=[tri[a].tolist(),tri[b].tolist()],shared_native_vertex_count=0)
    rows.append(row)
counts=Counter(r['classification'] for r in rows);assert before==sha(source)
neighbors=[set() for _ in v]
for a,b,c in ids:
    neighbors[a].update((int(b),int(c)));neighbors[b].update((int(a),int(c)));neighbors[c].update((int(a),int(b)))
todo=set(range(len(v)));groups=[]
while todo:
    stack=[todo.pop()];members=[]
    while stack:
        i=stack.pop();members.append(i)
        for j in neighbors[i]:
            if j in todo:todo.remove(j);stack.append(j)
    groups.append(sorted(members))
groups.sort(key=len,reverse=True);component_rows=[]
main_triangles=tri[np.all(np.isin(ids,groups[0]),axis=1)]
for members in groups:
    points=v[members];faces=ids[np.all(np.isin(ids,members),axis=1)];ct=v[faces]-points[0]
    volume=float(np.einsum('ij,ij->i',ct[:,0],np.cross(ct[:,1],ct[:,2])).sum()/6)
    component_rows.append(dict(vertex_count=len(members),triangle_count=len(faces),native_vertex_indices=members if len(members)<100 else None,
        world_bounds=[points.min(0).tolist(),points.max(0).tolist()],dimensions_m=(points.max(0)-points.min(0)).tolist(),signed_volume_m3=volume,
        actual_world_vertices=points.tolist() if len(members)<100 else None,
        sampled_nearest_main_surface_m=None if len(members)==len(groups[0]) else min(float(distances_to_triangles(p,main_triangles).min()) for p in points)))
report=dict(source_sha256=before,source_unchanged=True,counterexample_cases_passed=counterexamples(),candidate_count=len(candidates),
            shared_native_vertex_or_edge_pairs_excluded=len(shared),classification_counts=dict(counts),real_positive_area_or_interior_crossings=sum(r['penetrating'] is True for r in rows),
            ambiguous_or_degenerate=sum(r['penetrating'] is None for r in rows),candidate_rows=rows,connected_components=component_rows,wall_seconds=time.monotonic()-start,
            method='Actual saved native triangles. BVH broad-phase followed by double-precision signed-plane, polygon-clipping and segment/barycentric narrow phase. Adjacent shared native vertex/edge pairs excluded. Coplanar zero-area and boundary-only contacts classified separately from true interior crossing.',
            modifies_union_geometry=False,original_failure_preserved=True,visual_acceptance=False,world_loaded=False,rendered=False)
(P/'actual-intersections58b.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('source_unchanged','candidate_count','classification_counts','real_positive_area_or_interior_crossings','ambiguous_or_degenerate','wall_seconds')},indent=2),flush=True)
