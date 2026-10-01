"""Reopen58 native source; check actual geometry, root-local exports, and context.

This is SOURCE validation only. No Godot process, render, saved-world mutation,
physical collision conclusion, ship clearance conclusion, or visual acceptance.
Parent schedules the Blender invocation after build58.py has completed.
"""
import argparse, hashlib, json, math, sys
from collections import Counter
from pathlib import Path
import bpy, bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
import geometry58 as G
from intake58 import native_intake,glb_reader
from build58 import world_coordinate,read_controls


def bounds(tri):
    p=tri.reshape(-1,3);return [p.min(0).tolist(),p.max(0).tolist()]


def distances_to_triangles(point,triangles):
    p=np.asarray(point);a,b,c=triangles[:,0],triangles[:,1],triangles[:,2]
    ab=b-a;ac=c-a;n=np.cross(ab,ac);norm2=(n*n).sum(1)
    dp=p-a;signed=(dp*n).sum(1)
    projection=p-n*(signed/np.maximum(norm2,1e-24))[:,None]
    v=projection-a;d00=(ab*ab).sum(1);d01=(ab*ac).sum(1);d11=(ac*ac).sum(1)
    d20=(v*ab).sum(1);d21=(v*ac).sum(1);den=d00*d11-d01*d01
    u=(d11*d20-d01*d21)/np.maximum(den,1e-24);w=(d00*d21-d01*d20)/np.maximum(den,1e-24)
    inside=(u>=0)&(w>=0)&(u+w<=1)&(norm2>1e-18)
    result=np.where(inside,signed*signed/np.maximum(norm2,1e-24),np.inf)
    for x,y in ((a,b),(b,c),(c,a)):
        e=y-x;t=np.clip(((p-x)*e).sum(1)/np.maximum((e*e).sum(1),1e-24),0,1)
        near=x+e*t[:,None];result=np.minimum(result,((near-p)**2).sum(1))
    return np.sqrt(np.maximum(result,0))


def classify(point,tri):
    point=np.asarray(point);a,b,c=tri[:,0],tri[:,1],tri[:,2];e1=b-a;e2=c-a
    near=distances_to_triangles(point,tri);nearest=int(near.argmin());votes=[]
    for d in ((.941784799,.233194321,.241129873),(.1723371,.9238873,.341567),(.384115,.271938,.882771)):
        d=np.asarray(d);d/=np.linalg.norm(d);h=np.cross(np.broadcast_to(d,e2.shape),e2);det=(e1*h).sum(1)
        valid=abs(det)>1e-10;inv=np.where(valid,1/np.where(valid,det,1),0)
        s=point-a;u=(s*h).sum(1)*inv;q=np.cross(s,e1);v=(q*d).sum(1)*inv;t=(e2*q).sum(1)*inv
        hits=np.sort(t[valid&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-5)])
        count=0;last=-np.inf
        for value in hits:
            if value-last>.001:count+=1;last=value
        votes.append(dict(direction=d.tolist(),unique_forward_hits=count,odd=count%2==1))
    minimum=float(near[nearest]);odd=[v['odd'] for v in votes]
    label='boundary' if minimum<=.025 else 'inside' if all(odd) else 'outside' if not any(odd) else 'ambiguous'
    return dict(classification=label,nearest_surface_m=minimum,nearest_triangle=nearest,rays=votes)


def bvh_for(tri):
    return BVHTree.FromPolygons([Vector(v) for v in tri.reshape(-1,3)],[(3*i,3*i+1,3*i+2) for i in range(len(tri))],all_triangles=True,epsilon=0)


def canonical_triangle(tri,scale=1000):
    row=[tuple(int(round(float(x)*scale)) for x in p) for p in tri]
    return min(tuple(row),tuple(row[1:]+row[:1]),tuple(row[2:]+row[:2]))


def verify(source):
    source=source.resolve();construction=json.loads((source/'construction58.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(source/'cloud_bank58.blend'))
    intake,old_world=native_intake();reader=glb_reader();all_new=[];geometry=[];passed=True
    # Native control readback is independent of the source JSON's final meshes.
    rebuilt=read_controls();original=construction['recipe']
    def near_recursive(a,b):
        if isinstance(a,dict):return set(a)==set(b) and all(near_recursive(a[k],b[k]) for k in a)
        if isinstance(a,(list,tuple)):return len(a)==len(b) and all(near_recursive(x,y) for x,y in zip(a,b))
        if isinstance(a,(float,int)):return abs(float(a)-float(b))<.002
        return a==b
    controls_match=near_recursive(rebuilt,original);passed&=controls_match
    for row in construction['meshes']:
        ob=bpy.data.objects[row['name']];me=ob.data;me.calc_loop_triangles()
        vertices=np.array([world_coordinate(ob.matrix_world@v.co) for v in me.vertices]);indices=np.array([tuple(t.vertices) for t in me.loop_triangles]);tri=vertices[indices]
        bm=bmesh.new();bm.from_mesh(me);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges)
        todo=set(bm.verts);components=[]
        while todo:
            pending=[todo.pop()];count=0
            while pending:
                v=pending.pop();count+=1
                for e in v.link_edges:
                    other=e.other_vert(v)
                    if other in todo:todo.remove(other);pending.append(other)
            components.append(count)
        bm.free();tree=BVHTree.FromPolygons([Vector(v) for v in vertices],[tuple(i) for i in indices],all_triangles=True,epsilon=0)
        self_pairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not(set(indices[a])&set(indices[b]))]
        area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)*.5
        duplicates=len(indices)-len({tuple(sorted(tuple(round(float(x),6) for x in v) for v in face)) for face in tri})
        native_volume=G.signed_volume(vertices,indices)
        export=reader(source/row['file']);assert len(export)==1
        etri=export[0]['triangles']@np.array(row['native_root_basis_rows']).T+np.array(row['native_root_position'])
        # Bind each exported point to the actual reopened native vertex and
        # compare oriented index triples; do not trust rounded decimal equality.
        kd=KDTree(len(vertices))
        for i,v in enumerate(vertices):kd.insert(Vector(v),i)
        kd.balance();mapped=[];errors=[]
        for v in etri.reshape(-1,3):
            _,index,error=kd.find(Vector(v));mapped.append(index);errors.append(error)
        def canonical_index(face):
            face=tuple(face);return min(face,face[1:]+face[:1],face[2:]+face[:2])
        orientation_match=Counter(canonical_index(t) for t in indices)==Counter(canonical_index(t) for t in np.array(mapped).reshape(-1,3))
        vertex_error=max(errors)
        own=not(boundary or nonmanifold or self_pairs or duplicates or (area<1e-8).sum()) and len(components)==1 and native_volume>0 and orientation_match and vertex_error<.002
        passed &= own
        geometry.append(dict(name=ob.name,passed=bool(own),vertices=len(vertices),triangles=len(indices),boundary_edges=boundary,nonmanifold_edges=nonmanifold,components=components,
                             nonadjacent_triangle_overlap_count=len(self_pairs),overlap_pairs=self_pairs[:40],duplicate_triangles=duplicates,zero_area_triangles=int((area<1e-8).sum()),
                             signed_volume_m3=native_volume,world_bounds=bounds(tri),glb_oriented_triangle_correspondence=orientation_match,glb_vertex_error_m=vertex_error,
                             internal_caps=int(ob['internal_caps']),source_shader_or_material_changed=False))
        all_new.append(dict(name=ob.name,triangles=tri,vertices=vertices,indices=indices,tree=tree,object=ob,kind=row['kind']))
    bank=next(m for m in all_new if m['kind']=='continuous_lower_volume')
    # External roots are actual old52e/52f GLB triangles at preserved native
    # transforms. These source-context checks are NOT a loaded-world proof.
    contact=[];bank_bounds=np.asarray(bounds(bank['triangles']))
    for old in old_world:
        if old['selected']:continue
        bb=np.asarray(bounds(old['triangles']));overlap=bool(np.all(bank_bounds[0]<=bb[1]) and np.all(bb[0]<=bank_bounds[1]))
        pairs=bank['tree'].overlap(bvh_for(old['triangles'])) if overlap else []
        if overlap:contact.append(dict(root=old['root'],mesh=old['name'],world_bounds=bb.tolist(),bvh_surface_overlap_pair_count=len(pairs),first_pairs=pairs[:12],
                                      interpretation='Actual triangle BVH overlaps; contacts/intersections require visual review and are not an accepted boundary blend'))
    # Sample the real exterior side vertices against real old mesh triangles.
    # Report sampled point distance, NOT an exact maximum or gap-free proof.
    side_group=bank['object'].vertex_groups['SURFACE_folded_side'].index
    side=[i for i,v in enumerate(bank['object'].data.vertices) if any(g.group==side_group for g in v.groups)]
    external=np.concatenate([o['triangles'] for o in old_world if not o['selected']])
    boundary_samples=[]
    for index in side[::8]:
        point=bank['vertices'][index];dist=distances_to_triangles(point,external)
        boundary_samples.append(dict(source_vertex=index,world=point.tolist(),nearest_external_triangle_distance_m=float(dist.min())))
    camera=np.array(intake['camera_transform'][9:]);camera_rows=[]
    for m in all_new:camera_rows.append(dict(name=m['name'],**classify(camera,m['triangles'])))
    # Deliberately bounded diagnostic corridor within the four-root authored
    # patch, above the lower relief and below upper ribbons. No input flight ran.
    route_points=[(3000,1150,4300),(3350,1150,3990),(3750,1150,3740),(4200,1150,3250),(4550,1150,3010)]
    route=[]
    all_context=np.concatenate([m['triangles'] for m in all_new]+[o['triangles'] for o in old_world if not o['selected']])
    for point in route_points:
        route.append(dict(point=list(point),sampled_center_to_cloud_surface_m=float(distances_to_triangles(point,all_context).min()),
                          new_volume_classifications=[dict(name=m['name'],**classify(point,m['triangles'])) for m in all_new]))
    y=bank['vertices'][:,1];bottom=[i for i,v in enumerate(bank['object'].data.vertices) if any(g.group==bank['object'].vertex_groups['SURFACE_bottom'].index for g in v.groups)]
    report=dict(native_source_geometry_passed=bool(passed),native_controls_match_recipe=bool(controls_match),geometry=geometry,
                native_ocean_y=intake['ocean']['saved_world_y'],bank_bottom_altitude_above_saved_ocean_m=[float(y[bottom].min()),float(y[bottom].max())],
                external_root_count=21,external_mesh_count=105,external_root_contacts=contact,exterior_boundary_samples=boundary_samples,
                camera_world=camera.tolist(),camera_new_optical_geometry=camera_rows,camera_outside_all_new_volumes=all(r['classification']=='outside' for r in camera_rows),
                source_route_samples=route,route_sampled_only=True,route_swept_volume_checked=False,ship_envelope_checked=False,physical_collision_checked=False,
                whole_world_loaded=False,rendered=False,visual_acceptance=False,source_sha256={f:hashlib.sha256((source/f).read_bytes()).hexdigest() for f in ['cloud_bank58.blend']+[r['file'] for r in construction['meshes']]})
    (source/'geometry-context58.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'native_source_geometry_passed':report['native_source_geometry_passed'],'native_controls_match_recipe':controls_match,'camera_outside_new_volumes':report['camera_outside_all_new_volumes'],
                     'contacts_requiring_review':len(contact),'source_readback_only':True,'visual_acceptance':False},indent=2))
    assert passed,'Retain failed report and source; do not promote or silently repair a completed source'


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=P)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    verify(args.source)
