"""Independent ellipsoid zero-surfaces with compact, pair-local root blends.

Pure numpy, embedded-ready, no file I/O or actions on import. Coordinates are
local U/V/Y metres. Half-axes define each actual zero-surface, not G supports.
d_i=min(axes_i)*(norm(local_i/axes_i)-1) is a PSEUDO-distance, not Euclidean
signed distance. D=min(all d_i, all independently evaluated pair candidates).
The public scalar is -D: positive inside, zero on the surface. There is no
sequential/global smooth-min, additive density, common floor, or new control.
"""
from collections import Counter
import hashlib
import numpy as np

CORNERS = np.asarray(((0,0,0),(1,0,0),(1,1,0),(0,1,0),
                      (0,0,1),(1,0,1),(1,1,1),(0,1,1)), dtype=np.int64)
TETS = ((0,1,2,6),(0,2,3,6),(0,3,7,6),
        (0,7,4,6),(0,4,5,6),(0,5,1,6))
CONTROL_IDS = ('Main_Crown','Rear_Lower_Crown','Wide_Oblique_Core',
               'Front_Low_Shoulder','Right_Mid_Shoulder','Front_Left_Belly',
               'Rear_Right_Belly','Small_Turn_Shoulder')


def control_arrays(config, controls=None):
    """Return (id, center, zero-surface half-axes, principal-axis columns)."""
    rows = config['controls'] if controls is None else controls
    result = []
    for row in rows:
        assert 'strength' not in row and 'field_strength' not in row, 'H has no density strength'
        center=np.asarray(row['center_uvy_m'],float)
        axes=np.asarray(row['half_axes_m'],float)
        rotation=np.asarray(row['axes_local'],float)
        assert center.shape==(3,) and axes.shape==(3,) and rotation.shape==(3,3)
        assert np.all(np.isfinite(center)) and np.all(np.isfinite(axes)) and np.all(np.isfinite(rotation))
        assert np.all(axes>0) and np.max(np.abs(rotation.T@rotation-np.eye(3)))<2e-5
        assert np.linalg.det(rotation)>0, 'No reflected or sheared controls'
        result.append((row['id'],center,axes,rotation))
    assert tuple(r[0] for r in result)==CONTROL_IDS, 'Keep the same eight ordered controls'
    return result


def blend_arrays(config, controls=None, blends=None):
    """Explicit axis-aligned compact windows; no pair is synthesized implicitly."""
    ids={row[0]:i for i,row in enumerate(control_arrays(config,controls))}
    rows=config['blends'] if blends is None else blends
    result=[]; seen=set()
    for row in rows:
        assert row['id'] not in seen; seen.add(row['id'])
        a,b=row['pair']; assert a in ids and b in ids and a!=b
        width=float(row['width_m'])
        center=np.asarray(row['window_center_uvy_m'],float)
        axes=np.asarray(row['window_half_axes_m'],float)
        assert np.isfinite(width) and width>0
        assert center.shape==(3,) and axes.shape==(3,)
        assert np.all(np.isfinite(center)) and np.all(np.isfinite(axes)) and np.all(axes>0)
        result.append((row['id'],ids[a],ids[b],width,center,axes))
    return result


def piece_distances(points, config, controls=None, gradient=False):
    """Individual PSEUDO-distances, shape (N,8); gradients are branch derivatives."""
    points=np.asarray(points,float)
    assert points.ndim==2 and points.shape[1]==3 and np.all(np.isfinite(points))
    values=[]; gradients=[]
    for name,center,axes,rotation in control_arrays(config,controls):
        local=(points-center)@rotation
        radius=np.linalg.norm(local/axes,axis=1)
        scale=float(axes.min())
        values.append(scale*(radius-1.))
        if gradient:
            # The norm is nondifferentiable at its center; the declared branch
            # convention is zero there. Extraction never uses these gradients.
            divisor=np.where(radius>0,radius,1.)
            grad=(scale*local/(axes**2)/divisor[:,None])@rotation.T
            gradients.append(grad)
    values=np.stack(values,axis=1)
    return (values,np.stack(gradients,axis=1)) if gradient else values


def field(points, config, controls=None, gradient=False, contributions=False, blends=None):
    """Positive-inside union scalar, optional branch gradient or ownership.

    contributions=True returns normalized nonnegative nearest-piece ownership
    weights (N,8), splitting exact/tiny roundoff ties. These are NOT additive
    density contributions and do not describe blending energy. They select
    editable groups/landmarks by the minimum original piece PSEUDO-distance.
    This option takes precedence over gradient, as in the previous interface.

    A pair candidate is min(a,b)-w*max(k-|a-b|,0)^2/(4*k), with the compact
    window w=max(1-sum(((p-c)/r)^2),0)^2. Each pair uses original a,b, never a
    previous pair candidate. Scalar correction <= k/4; spatial displacement
    is NOT claimed to equal k/4 because d_i is not an exact distance field.
    """
    points=np.asarray(points,float)
    if gradient and not contributions:
        distances,grads=piece_distances(points,config,controls,gradient=True)
    else:
        distances=piece_distances(points,config,controls)
    if contributions:
        closest=distances.min(axis=1,keepdims=True)
        weights=(np.abs(distances-closest)<=1e-12).astype(float)
        return weights/weights.sum(axis=1,keepdims=True)
    # Choose equal-valued branches by their stable table order. At hard union
    # seams this is a branch derivative, not a claim of differentiability.
    nearest=np.argmin(distances,axis=1); index=np.arange(len(points))
    union=distances[index,nearest].copy()
    if gradient:union_grad=grads[index,nearest].copy()
    for name,ia,ib,width,center,axes in blend_arrays(config,controls,blends):
        a,b=distances[:,ia],distances[:,ib]
        delta=a-b; remaining=np.maximum(width-np.abs(delta),0.)
        window_local=(points-center)/axes
        term=np.maximum(1.-np.sum(window_local**2,axis=1),0.)
        weight=term**2
        correction=weight*remaining**2/(4.*width)
        candidate=np.minimum(a,b)-correction
        choose=candidate<union
        if gradient:
            ga,gb=grads[:,ia],grads[:,ib]
            window_grad=-4.*term[:,None]*(points-center)/(axes**2)
            correction_grad=(remaining**2/(4.*width))[:,None]*window_grad
            correction_grad-=(weight*remaining*np.sign(delta)/(2.*width))[:,None]*(ga-gb)
            pair_grad=np.where((a<=b)[:,None],ga,gb)-correction_grad
            union_grad[choose]=pair_grad[choose]
        union[choose]=candidate[choose]
    return (-union,-union_grad) if gradient else -union


def extract(config, controls=None, blends=None):
    """Shared-grid-edge marching tetrahedra at the specified positive-inside iso0.

    Faces use each tetrahedron's constant linear-interpolant gradient, not the
    nondifferentiable min field's analytic branch gradient. The grid encloses
    every ellipsoid and entire blend window with one extra step of padding.
    This is a spatial support bound, not a k/4 displacement assumption.
    """
    assert config['field']['iso_value']==0
    step=float(config['meshing']['spacing_m'])
    origin=np.asarray(config['meshing']['grid_origin_uvy_m'],float)
    assert step>0 and np.isfinite(step) and origin.shape==(3,) and np.all(np.isfinite(origin))
    intervals=[]
    for name,center,axes,rotation in control_arrays(config,controls):
        extent=np.sqrt((rotation**2)@(axes**2))
        intervals.append((center-extent,center+extent))
    for name,ia,ib,width,center,axes in blend_arrays(config,controls,blends):
        intervals.append((center-axes,center+axes))
    low=origin+(np.floor((np.min([r[0] for r in intervals],axis=0)-origin)/step)-1)*step
    high=origin+(np.ceil((np.max([r[1] for r in intervals],axis=0)-origin)/step)+1)*step
    shape=np.rint((high-low)/step).astype(int)+1
    assert int(np.prod(shape))<=config['meshing']['max_grid_nodes'], 'Refuse oversized union workspace'
    indices=np.indices(tuple(shape)).reshape(3,-1).T
    points=low+indices*step
    values=field(points,config,controls,blends=blends)
    assert not np.any(values==0), 'Exact grid isovalue needs explicit review, never silent jitter'
    volume=values.reshape(tuple(shape))
    boundary=np.concatenate((volume[0].ravel(),volume[-1].ravel(),volume[:,0].ravel(),
                             volume[:,-1].ravel(),volume[:,:,0].ravel(),volume[:,:,-1].ravel()))
    assert np.max(boundary)<0, 'Isosurface touches workspace boundary; do not cap it'
    cube_shape=shape-1
    cube_values=np.stack([volume[x:x+cube_shape[0],y:y+cube_shape[1],z:z+cube_shape[2]]
                          for x,y,z in CORNERS],axis=-1)
    active=np.argwhere((cube_values.min(axis=-1)<0)&(cube_values.max(axis=-1)>0))
    stride=np.asarray((shape[1]*shape[2],shape[2],1),np.int64)
    offsets=CORNERS@stride
    inverse_edges=[np.linalg.inv((CORNERS[list(tetra)[1:]]-CORNERS[tetra[0]])*step) for tetra in TETS]
    cache={}; vertices=[]; faces=[]; outward=[]
    def crossing(a,b):
        a,b=(int(a),int(b)) if a<b else (int(b),int(a))
        key=(a,b)
        if key not in cache:
            t=-values[a]/(values[b]-values[a]); assert 0<t<1
            cache[key]=len(vertices); vertices.append(points[a]+t*(points[b]-points[a]))
        return cache[key]
    for xyz in active:
        ids=int(xyz@stride)+offsets
        for tetra,inverse in zip(TETS,inverse_edges):
            tt=ids[list(tetra)]
            inside=[int(i) for i in tt if values[i]>0]
            outside=[int(i) for i in tt if values[i]<0]
            if len(inside) in (0,4):continue
            direction=-(inverse@(values[tt[1:]]-values[tt[0]]))
            if len(inside)==1:
                faces.append([crossing(inside[0],i) for i in outside]); outward.append(direction)
            elif len(inside)==3:
                faces.append([crossing(outside[0],i) for i in inside]); outward.append(direction)
            else:
                a,b,c,d=(crossing(inside[0],outside[0]),crossing(inside[0],outside[1]),
                         crossing(inside[1],outside[0]),crossing(inside[1],outside[1]))
                faces.extend(((a,b,d),(a,d,c))); outward.extend((direction,direction))
    vertices=np.asarray(vertices,float); faces=np.asarray(faces,np.int64)
    assert 0<len(faces)<=config['meshing']['max_raw_triangles']
    tris=vertices[faces]
    dot=np.einsum('ij,ij->i',np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]),np.asarray(outward))
    assert np.all(np.abs(dot)>1e-12), 'Ambiguous tetrahedral face orientation'
    faces[dot<0]=faces[dot<0][:,[0,2,1]]
    proof=topology(vertices,faces)
    assert proof['passed'], 'Raw union shell failed basic manifold/connected/orientation checks'
    return dict(vertices=vertices,faces=faces,proof=proof,
                grid=dict(shape=shape.tolist(),nodes=len(points),active_cubes=len(active),spacing_m=step,
                          lower_uvy_m=low.tolist(),upper_uvy_m=high.tolist(),
                          boundary_max_positive_inside_scalar=float(boundary.max()),
                          shared_grid_edge_intersections=len(cache),
                          winding_basis='Each tetrahedron linear scalar interpolant gradient'),
                bounds_uvy_m=[vertices.min(axis=0).tolist(),vertices.max(axis=0).tolist()],
                field_controls=len(control_arrays(config,controls)),
                designated_pair_blends=len(blend_arrays(config,controls,blends)),
                single_shared_surface=True,scalar_semantics='Positive-inside PSEUDO-distance union; iso0')


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




def source_basis(frame):
    u=np.asarray(frame['local_u_world'],float); v=np.asarray(frame['local_v_world'],float)
    basis=np.asarray(((u[0],v[0],0),(-u[2],-v[2],0),(0,0,1)),float)
    assert np.all(np.isfinite(basis)) and np.max(np.abs(basis.T@basis-np.eye(3)))<2e-6 and np.linalg.det(basis)>0
    return basis


def source_coordinates(local,frame):
    return np.asarray(local,float)@source_basis(frame).T
