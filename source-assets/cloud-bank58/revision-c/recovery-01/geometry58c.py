"""Explicit compact, asymmetric native control shells. Pure Python; no Blender.

Angular ring contours are editing controls for short, unequal 3D masses. No
heightfield, world plate, long axial loft, or sphere primitive is used. Every
saved ring vertex is editable. A common construction topology is not a claim
that the source silhouette is accepted.
"""
import math
import numpy as np

ORIGIN=np.array([3775.,700.,3575.])

def source_coordinate(p):
    p=np.asarray(p)-ORIGIN
    return (float(p[0]),float(-p[2]),float(p[1]))

def world_coordinate(p):
    return (float(p[0]+ORIGIN[0]),float(p[2]+ORIGIN[1]),float(-p[1]+ORIGIN[2]))

def volume(vertices,faces):
    v=np.asarray(vertices,float);f=np.asarray(faces,int);t=v[f]
    return float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)

def control_mesh(row):
    """Six angular rings + unequal broad top/belly hubs, in exact worldXYZ."""
    role=row['role'];number=int(row['id'][1:]);role_index={'lower_density':0,'primary_crown':1,'medium_fold':2,'small_edge_fold':3}[role]
    n=10 if role=='lower_density' else 9 if role=='primary_crown' else 8 if role=='medium_fold' else 7
    seed=number*1.731+role_index*.873
    # Ring height, half-size radius, independently offset XZ centre.
    if role=='lower_density':levels=[(-.46,.29),(-.29,.78),(-.05,.99),(.18,.96),(.36,.73),(.465,.32)]
    elif role=='primary_crown':levels=[(-.46,.32),(-.29,.77),(-.06,.98),(.18,.91),(.36,.69),(.47,.27)]
    elif role=='medium_fold':levels=[(-.46,.28),(-.27,.83),(-.02,.99),(.22,.91),(.39,.59),(.475,.24)]
    else:levels=[(-.46,.25),(-.24,.83),(.02,.96),(.23,.88),(.40,.55),(.48,.18)]
    vertices=[]
    for r,(y,rad) in enumerate(levels):
        dx=.048*math.sin(seed+r*.87);dz=.042*math.cos(seed*.83+r*.93)
        for j in range(n):
            angle=2*math.pi*j/n+.08*math.sin(seed+j*.73)
            # Broad uneven shoulders; deterministic individual outlines, not noise.
            fold=1+.105*math.cos(3*angle+seed)+.06*math.sin(2*angle-seed*.72)
            radial=rad*fold
            xx=.5*radial*math.cos(angle)+dx
            zz=.5*radial*math.sin(angle)+dz
            yy=y+.018*math.sin(2*angle+seed+r*.5)
            vertices.append([xx,yy,zz])
    vertices.append([-.07*math.sin(seed),-.5,.06*math.cos(seed*.7)]);bottom=len(vertices)-1
    vertices.append([.07*math.cos(seed),.5,-.055*math.sin(seed*.8)]);top=len(vertices)-1
    faces=[]
    for r in range(len(levels)-1):
        for j in range(n):
            k=(j+1)%n;a=r*n+j;b=r*n+k;c=(r+1)*n+k;d=(r+1)*n+j
            faces.extend([(a,b,c),(a,c,d)] if (r+j+number)%2 else [(a,b,d),(b,c,d)])
    for j in range(n):
        k=(j+1)%n;faces.append((bottom,k,j));faces.append((top,(len(levels)-1)*n+j,(len(levels)-1)*n+k))
    v=np.asarray(vertices,float)
    # Exact design extents before yaw, without square caps or a trim domain.
    v=(v-(v.min(0)+v.max(0))/2)/(v.max(0)-v.min(0))*np.asarray(row['design_extent_xyz_m'])
    angle=math.radians(row['yaw_degrees']);co,si=math.cos(angle),math.sin(angle)
    rot=np.array([[co,0,-si],[0,1,0],[si,0,co]])
    v=v@rot.T+np.asarray(row['center_godot_world_xyz_m'])
    if volume(v,faces)<0:faces=[tuple(reversed(f)) for f in faces]
    return dict(id=row['id'],role=role,parent_form=row['parent_form'],vertices=v.tolist(),faces=faces,
                ring_vertices=n,ring_count=len(levels),source_method='six independently offset angular ring contours with unequal broad top and belly hubs',
                design=row)

def all_controls(plan):
    controls=[control_mesh(row) for row in plan['controls']]
    for spec in controls:
        v=spec['vertices'];n=spec['ring_vertices'];rings=spec['ring_count']
        for hub,ring in [(-2,v[:n]),(-1,v[(rings-1)*n:rings*n])]:
            # Endhub stays above/below its terminalring and within its contour.
            # No othervertex, face, declaredbounds or controltransformchanges.
            v[hub][0]=sum(q[0] for q in ring)/n
            v[hub][2]=sum(q[2] for q in ring)/n
    return controls
