"""Fresh native B readback and bounded source context; never a world/visual pass."""
import argparse,hashlib,json,sys
from collections import Counter
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
P=Path(__file__).resolve().parent;A=P.parent;ROOT=A.parents[1]
sys.path[:0]=[str(P),str(A)]
from intake58 import native_intake,glb_reader
from build58 import world_coordinate
from geometry58 import signed_volume
from verify58 import bounds,distances_to_triangles,classify,bvh_for


def mesh_data(ob):
    ob.data.calc_loop_triangles();v=np.array([world_coordinate(ob.matrix_world@p.co) for p in ob.data.vertices]);ids=np.array([tuple(t.vertices) for t in ob.data.loop_triangles]);return v,ids,v[ids]


def geometry(ob):
    v,ids,tri=mesh_data(ob);bm=bmesh.new();bm.from_mesh(ob.data)
    boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);todo=set(bm.verts);components=[]
    while todo:
        stack=[todo.pop()];count=0
        while stack:
            p=stack.pop();count+=1
            for e in p.link_edges:
                q=e.other_vert(p)
                if q in todo:todo.remove(q);stack.append(q)
        components.append(count)
    bm.free();tree=BVHTree.FromPolygons([Vector(p) for p in v],[tuple(t) for t in ids],all_triangles=True,epsilon=0)
    overlaps=[(a,b) for a,b in tree.overlap(tree) if a<b and not(set(ids[a])&set(ids[b]))]
    area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)*.5
    duplicates=len(ids)-len({tuple(sorted(tuple(round(float(x),6) for x in p) for p in t)) for t in tri})
    row=dict(name=ob.name,vertices=len(v),triangles=len(ids),boundary_edges=boundary,nonmanifold_edges=nonmanifold,components=components,
             nonadjacent_self_overlap_count=len(overlaps),first_overlap_pairs=overlaps[:30],zero_area_triangles=int((area<1e-8).sum()),duplicate_triangles=duplicates,
             signed_volume_m3=signed_volume(v,ids),world_bounds=bounds(tri))
    row['closed_geometry_passed']=not(boundary or nonmanifold or overlaps or row['zero_area_triangles'] or duplicates) and len(components)==1 and row['signed_volume_m3']>0
    return row,v,ids,tri,tree


def verify(source):
    build=json.loads((source/'construction58b.json').read_text());input_controls=json.loads((source/'native-control-input58b.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(source/'cloud_bank58b.blend'))
    intake,old=native_intake();reader=glb_reader();rows=[];final=[];passed=True
    for row in build['meshes']:
        ob=bpy.data.objects[row['name']];data,v,ids,tri,tree=geometry(ob);export=reader(source/row['file']);assert len(export)==1
        etri=export[0]['triangles']@np.array(row['native_root_basis_rows']).T+np.array(row['native_root_position'])
        kd=KDTree(len(v))
        for i,p in enumerate(v):kd.insert(Vector(p),i)
        kd.balance();mapped=[];errors=[]
        for p in etri.reshape(-1,3):
            _,i,e=kd.find(Vector(p));mapped.append(i);errors.append(e)
        def canon(t):
            t=tuple(t);return min(t,t[1:]+t[:1],t[2:]+t[:2])
        correspondence=Counter(canon(t) for t in ids)==Counter(canon(t) for t in np.array(mapped).reshape(-1,3))
        data.update(glb_oriented_triangle_correspondence=correspondence,glb_world_vertex_error_m=max(errors))
        data['passed']=data['closed_geometry_passed'] and correspondence and max(errors)<.002
        passed&=data['passed'];rows.append(data);final.append(dict(name=ob.name,vertices=v,indices=ids,triangles=tri,tree=tree))
    control_rows=[]
    for spec in input_controls['loft_specs']:
        ob=bpy.data.objects['EDIT58B_'+spec['name']];data,v,ids,tri,tree=geometry(ob)
        delta=float(np.linalg.norm(v-np.array(spec['vertices']),axis=1).max())
        data['native_authored_vertex_error_m']=delta;data['native_control_preserved']=delta<.0002 and len(v)==len(spec['vertices'])
        passed &= data['closed_geometry_passed'] and data['native_control_preserved'];control_rows.append(data)
    union=bpy.data.objects['EDIT58B_continuous_union_before_facets'];union_row,*_=geometry(union);passed &= union_row['closed_geometry_passed']
    bank=final[0];bb=np.asarray(bounds(bank['triangles']));contacts=[]
    for part in old:
        if part['selected']:continue
        bounds_old=np.asarray(bounds(part['triangles']))
        overlap=bool(np.all(bb[0]<=bounds_old[1]) and np.all(bounds_old[0]<=bb[1]))
        if overlap:
            pairs=bank['tree'].overlap(bvh_for(part['triangles']))
            contacts.append(dict(root=part['root'],mesh=part['name'],bvh_surface_overlap_pair_count=len(pairs),first_pairs=pairs[:12],
                                 limitation='Source triangles only; not an accepted boundary blend or loaded-world check'))
    camera=intake['camera_transform'][9:];camera_rows=[dict(name=m['name'],**classify(camera,m['triangles'])) for m in final]
    # Exterior samples are selected from actual new surface vertices. No common
    # skirt or rectangle is assumed; convex hull is NOT used as geometry.
    ext=np.concatenate([m['triangles'] for m in old if not m['selected']]);boundary=[]
    center=np.mean(bank['vertices'][:,[0,2]],axis=0);r=np.linalg.norm(bank['vertices'][:,[0,2]]-center,axis=1)
    outer=np.flatnonzero(r>np.percentile(r,80))[::12]
    for i in outer:
        p=bank['vertices'][i];boundary.append(dict(vertex=int(i),world=p.tolist(),nearest_external_triangle_distance_m=float(distances_to_triangles(p,ext).min())))
    # Upper source-A native meshes are reused without claiming accepted shape.
    # Verify exact vertex, topology, color values and object matrices from the
    # original saved A by loading independent names in this ephemeral process.
    preserved=[]
    current={ob.name:ob for ob in bpy.data.objects if ob.name.startswith('CloudBank58_upper_')}
    with bpy.data.libraries.load(str(A/'cloud_bank58.blend'),link=False) as (src,dst):dst.objects=list(current)
    for original in dst.objects:
        key=original.name.rsplit('.',1)[0] if original.name.rsplit('.',1)[-1].isdigit() else original.name
        copied=current[key]
        exact=len(copied.data.vertices)==len(original.data.vertices) and [tuple(v.co) for v in copied.data.vertices]==[tuple(v.co) for v in original.data.vertices]
        exact &= [tuple(p.vertices) for p in copied.data.polygons]==[tuple(p.vertices) for p in original.data.polygons] and copied.matrix_world==original.matrix_world
        exact &= [tuple(x.color) for x in copied.data.color_attributes['Col'].data]==[tuple(x.color) for x in original.data.color_attributes['Col'].data]
        preserved.append(dict(name=key,A_vertices_topology_colors_transform_exact=bool(exact)));passed&=exact
    output=dict(native_source_geometry_passed=bool(passed),source_status='B new3D fold construction; visual review pending',geometry=rows,native_controls=control_rows,
                continuous_union_before_facets=union_row,old_A_upper_preservation=preserved,external_root_count=21,external_mesh_count=105,external_source_contacts=contacts,
                outer20percent_radial_vertex_samples=boundary,boundary_sample_limit='Sampled distances, not complete boundary connectivity or exact largest gap',
                camera_world=camera,camera_new_optical_geometry=camera_rows,camera_outside_all_new_volumes=all(r['classification']=='outside' for r in camera_rows),
                saved_native_ocean_y=0.,new_bank_world_bounds=rows[0]['world_bounds'],ship_envelope_checked=False,route_swept_volume_checked=False,world_loaded=False,rendered=False,visual_acceptance=False,
                source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [source/'cloud_bank58b.blend',*source.glob('*.glb')]})
    (source/'geometry-context58b.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(dict(native_source_geometry_passed=bool(passed),bank_triangles=rows[0]['triangles'],camera_outside=output['camera_outside_all_new_volumes'],actual_external_contact_meshes=sum(r['bvh_surface_overlap_pair_count']>0 for r in contacts),visual_acceptance=False),indent=2))
    assert passed,'Preserve native failed source and report; no visual/world promotion'


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=P)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    verify(args.source)
