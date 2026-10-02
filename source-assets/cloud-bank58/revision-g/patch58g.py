"""Deterministic finite-support field and shared-edge tetrahedral isosurface.

Pure numpy; import defines functions only. Geometry remains in local U/V/Y.
Controls are a new design hypothesis, never reference-derived 3D measurements.
No old cloud mesh, noise, common underside, camera or image processing is used.
"""
from collections import Counter
import hashlib
import math
import numpy as np

CORNERS = np.asarray(((0,0,0),(1,0,0),(1,1,0),(0,1,0),
                      (0,0,1),(1,0,1),(1,1,1),(0,1,1)), dtype=np.int64)
# The same body diagonal in every cube gives matching face diagonals.
TETS = ((0,1,2,6),(0,2,3,6),(0,3,7,6),
        (0,7,4,6),(0,4,5,6),(0,5,1,6))


def rotation_xyz(degrees):
    x,y,z = np.radians(degrees)
    cx,sx,cy,sy,cz,sz = math.cos(x),math.sin(x),math.cos(y),math.sin(y),math.cos(z),math.sin(z)
    return np.asarray(((cz,-sz,0),(sz,cz,0),(0,0,1))) @ np.asarray(((cy,0,sy),(0,1,0),(-sy,0,cy))) @ np.asarray(((1,0,0),(0,cx,-sx),(0,sx,cx)))


def control_arrays(config, controls=None):
    result=[]
    for row in controls if controls is not None else config['controls']:
        rotation = np.asarray(row['axes_local'],float) if 'axes_local' in row else rotation_xyz(row['rotation_xyz_degrees'])
        axes = np.asarray(row['half_axes_m'],float) * config['field']['support_radius_multiplier']
        center = np.asarray(row['center_uvy_m'],float)
        assert axes.shape==(3,) and center.shape==(3,) and np.all(axes>0)
        assert np.all(np.isfinite(axes)) and np.all(np.isfinite(center))
        assert np.max(np.abs(rotation.T@rotation-np.eye(3)))<2e-5 and np.linalg.det(rotation)>0
        assert 0 < row['strength'] <= 2
        result.append((row['id'],center,axes,rotation,float(row['strength'])))
    assert len(result)==8 and len({r[0] for r in result})==8
    return result


def field(points, config, controls=None, gradient=False, contributions=False):
    points=np.asarray(points,float)
    assert points.ndim==2 and points.shape[1]==3
    values=[]; gradients=[]
    for name,center,axes,rotation,strength in control_arrays(config,controls):
        local=(points-center)@rotation
        q2=np.sum((local/axes)**2,axis=1)
        term=np.maximum(0.,1.-q2)
        values.append(strength*term**3)
        if gradient:
            gradients.append((-6.*strength*term[:,None]**2*local/(axes**2))@rotation.T)
    values=np.asarray(values).T
    if contributions:return values
    if gradient:return values.sum(axis=1),np.sum(gradients,axis=0)
    return values.sum(axis=1)


def topology(vertices,faces):
    v=np.asarray(vertices,float); f=np.asarray(faces,np.int64)
    assert v.ndim==2 and v.shape[1]==3 and len(v)>3 and np.all(np.isfinite(v))
    assert f.ndim==2 and f.shape[1]==3 and len(f)>3 and f.min()>=0 and f.max()<len(v)
    directed=Counter((int(a),int(b)) for tri in f for a,b in zip(tri,np.roll(tri,-1)))
    edges=Counter(tuple(sorted(edge)) for edge in directed.elements())
    closed=all(n==2 for n in edges.values())
    oriented=all(n==1 and directed[(b,a)]==1 for (a,b),n in directed.items())
    neighbors=[set() for _ in v]
    for a,b in edges:neighbors[a].add(b);neighbors[b].add(a)
    unseen=set(range(len(v))); components=0
    while unseen:
        stack=[unseen.pop()];components+=1
        while stack:
            nxt=neighbors[stack.pop()] & unseen
            unseen.difference_update(nxt);stack.extend(nxt)
    tri=v[f]; cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    minimum_double_area=float(np.linalg.norm(cross,axis=1).min())
    duplicate_faces=len(f)-len({tuple(sorted(map(int,tri))) for tri in f})
    duplicate_vertices=len(v)-len(np.unique(v,axis=0))
    links=[{} for _ in v]
    for a,b,d in f:
        for center,x,y in ((a,b,d),(b,d,a),(d,a,b)):
            links[center].setdefault(int(x),set()).add(int(y))
            links[center].setdefault(int(y),set()).add(int(x))
    bad_links=0
    for link in links:
        if not link or any(len(n)!=2 for n in link.values()):bad_links+=1;continue
        visited=set();stack=[next(iter(link))]
        while stack:
            node=stack.pop()
            if node in visited:continue
            visited.add(node);stack.extend(link[node]-visited)
        if len(visited)!=len(link):bad_links+=1
    relative=tri-v.mean(axis=0)
    volume=float(np.einsum('ij,ij->i',relative[:,0],np.cross(relative[:,1],relative[:,2])).sum()/6.)
    euler=len(v)-len(edges)+len(f)
    max_edge=float(max(np.linalg.norm(v[a]-v[b]) for a,b in edges))
    result=dict(vertices=len(v),triangles=len(f),edges=len(edges),connected_components=components,
                closed_edge_incidence_two=closed,oriented_edges_consistent=oriented,euler_characteristic=euler,
                minimum_double_triangle_area_m2=minimum_double_area,signed_volume_m3=volume,maximum_edge_m=max_edge,
                duplicate_triangle_count=duplicate_faces,duplicate_coordinate_count=duplicate_vertices,
                nonsingle_cycle_vertex_links=bad_links,
                self_intersections_checked=False,continuous_valley_checked=False,visual_acceptance=False)
    result['passed']=bool(closed and oriented and components==1 and euler==2 and minimum_double_area>1e-8 and volume>0
                          and duplicate_faces==0 and duplicate_vertices==0 and bad_links==0)
    return result


def fingerprint(vertices,faces):
    v=np.asarray(vertices,dtype='<f4'); f=np.asarray(faces,dtype='<i4')
    return dict(vertices_sha256=hashlib.sha256(v.tobytes(order='C')).hexdigest(),
                oriented_triangles_sha256=hashlib.sha256(f.tobytes(order='C')).hexdigest(),
                vertices=len(v),triangles=len(f))


def extract(config, controls=None):
    step=float(config['meshing']['spacing_m']); origin=np.asarray(config['meshing']['grid_origin_uvy_m'],float)
    assert step>0 and config['field']['iso_value']>0
    intervals=[]
    for name,center,axes,rotation,strength in control_arrays(config,controls):
        extent=np.sqrt((rotation**2)@(axes**2))
        intervals.append((center-extent,center+extent))
    low=origin+(np.floor((np.min([r[0] for r in intervals],axis=0)-origin)/step)-1)*step
    high=origin+(np.ceil((np.max([r[1] for r in intervals],axis=0)-origin)/step)+1)*step
    shape=np.rint((high-low)/step).astype(int)+1
    assert int(np.prod(shape))<=config['meshing']['max_grid_nodes'],'Refuse oversized density workspace'
    indices=np.indices(tuple(shape)).reshape(3,-1).T
    points=low+indices*step
    values=field(points,config,controls)
    iso=float(config['field']['iso_value'])
    assert not np.any(values==iso),'Exact grid isovalue needs explicit design review, never silent jitter'
    volume=values.reshape(tuple(shape))
    boundary=np.concatenate((volume[0].ravel(),volume[-1].ravel(),volume[:,0].ravel(),volume[:,-1].ravel(),volume[:,:,0].ravel(),volume[:,:,-1].ravel()))
    assert np.max(boundary)<iso,'Isosurface touches workspace boundary; do not cap it'
    cube_shape=shape-1
    cube_values=np.stack([volume[x:x+cube_shape[0],y:y+cube_shape[1],z:z+cube_shape[2]] for x,y,z in CORNERS],axis=-1)
    active=np.argwhere((cube_values.min(axis=-1)<iso)&(cube_values.max(axis=-1)>iso))
    stride=np.asarray((shape[1]*shape[2],shape[2],1),np.int64)
    offsets=CORNERS@stride
    cache={}; vertices=[];faces=[]
    def crossing(a,b):
        a,b=(int(a),int(b)) if a<b else (int(b),int(a))
        key=(a,b)
        if key not in cache:
            t=(iso-values[a])/(values[b]-values[a])
            assert 0<t<1
            cache[key]=len(vertices);vertices.append(points[a]+t*(points[b]-points[a]))
        return cache[key]
    for xyz in active:
        ids=int(xyz@stride)+offsets
        for tetra in TETS:
            tt=ids[list(tetra)]
            inside=[int(i) for i in tt if values[i]>iso]
            outside=[int(i) for i in tt if values[i]<iso]
            if len(inside) in (0,4):continue
            if len(inside)==1:
                faces.append([crossing(inside[0],i) for i in outside])
            elif len(inside)==3:
                faces.append([crossing(outside[0],i) for i in inside])
            else:
                a,b,c,d=(crossing(inside[0],outside[0]),crossing(inside[0],outside[1]),
                         crossing(inside[1],outside[0]),crossing(inside[1],outside[1]))
                # A deterministic diagonal of the planar section quadrilateral.
                faces.extend(((a,b,d),(a,d,c)))
    vertices=np.asarray(vertices,float);faces=np.asarray(faces,np.int64)
    assert len(faces)<=config['meshing']['max_raw_triangles'] and len(faces)>0
    tris=vertices[faces]
    _,gradient=field(tris.mean(axis=1),config,controls,gradient=True)
    dot=np.einsum('ij,ij->i',np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]),-gradient)
    assert np.all(np.abs(dot)>1e-12),'Ambiguous face orientation'
    faces[dot<0]=faces[dot<0][:,[0,2,1]]
    proof=topology(vertices,faces)
    assert proof['passed'],'Raw field shell failed basic manifold/connected/orientation checks'
    return dict(vertices=vertices,faces=faces,proof=proof,
                grid=dict(shape=shape.tolist(),nodes=len(points),active_cubes=len(active),spacing_m=step,
                          lower_uvy_m=low.tolist(),upper_uvy_m=high.tolist(),boundary_max_density=float(boundary.max()),
                          shared_grid_edge_intersections=len(cache)),
                field_controls=len(control_arrays(config,controls)),single_shared_surface=True)


def source_basis(frame):
    u=np.asarray(frame['local_u_world'],float); v=np.asarray(frame['local_v_world'],float)
    basis=np.asarray(((u[0],v[0],0),(-u[2],-v[2],0),(0,0,1)),float)
    assert np.all(np.isfinite(basis)) and np.max(np.abs(basis.T@basis-np.eye(3)))<2e-6 and np.linalg.det(basis)>0
    return basis


def source_coordinates(local,frame):
    return np.asarray(local,float)@source_basis(frame).T
