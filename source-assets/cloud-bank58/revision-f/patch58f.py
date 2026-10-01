"""One shared, editable double-crown skin; definitions only, no asset writes.

This is a new shape hypothesis. D/E geometry is not read or transformed. All
metres are design coordinates, not 3D dimensions measured from reference pixels.
The 7x9 topology is deformed into an irregular outline, with shared crown/shoulder
and saddle vertices, three short side turns and a separately folded belly net.
"""
from collections import Counter
import numpy as np

U=[
 [-95,-65,-30,5,45,80,115,140,155],
 [-200,-155,-95,-45,15,70,135,190,215],
 [-265,-215,-140,-65,15,85,150,210,250],
 [-280,-225,-145,-60,20,90,160,230,280],
 [-240,-195,-125,-45,40,110,175,235,265],
 [-155,-115,-55,10,70,130,190,235,250],
 [-65,-25,20,70,115,155,195,220,225]
]
V_BASE=[-195,-140,-75,-10,55,130,195]
V_DELTA=[
 [22,7,-4,-12,0,14,-4,10,27],
 [4,-8,12,3,-10,6,-12,8,2],
 [-6,9,-7,11,-4,12,3,-10,6],
 [4,-11,5,-7,8,-5,12,-4,-7],
 [-8,10,-5,8,-12,4,-8,12,-5],
 [6,-4,9,-11,5,-7,10,-5,-8],
 [-18,-5,12,6,-4,15,0,-9,-27]
]
TOP_Y=[
 [655,680,704,718,710,690,700,680,645],
 [685,735,770,805,780,750,775,725,690],
 [730,805,865,873,820,775,810,780,715],
 [755,840,888,880,800,770,832,852,775],
 [730,795,848,866,805,785,843,834,760],
 [705,750,790,775,765,785,817,806,740],
 [675,725,755,745,770,755,775,740,700]
]
# Every boundary station is authored explicitly. These are not concentric rings
# at common heights: each follows its own upper outline elevation and offsets.
SIDE_OFFSETS=[
 [24,38,31,42,27,36,45,30,22,34,42,28,36,25,18,29,43,32,23,37,28,20,30,42,24,36,29,22],
 [-10,-14,-8,-17,-12,-8,-18,-15,-6,-12,-18,-10,-14,-8,-5,-12,-16,-8,-15,-10,-17,-9,-12,-8,-16,-11,-15,-8],
 [16,24,12,30,18,8,25,22,14,20,28,12,23,16,8,22,14,27,18,10,26,16,23,12,29,18,10,20]
]
SIDE_DROPS=[
 [32,45,30,55,35,42,28,48,34,42,31,50,36,28,40,32,45,29,44,35,50,30,42,34,48,28,39,33],
 [95,110,90,108,98,88,112,102,94,108,96,115,102,89,98,105,92,110,97,106,90,112,100,92,108,96,104,90],
 [150,135,162,140,155,130,158,145,152,138,164,148,155,132,150,160,138,155,142,165,149,136,158,144,152,137,162,146]
]
# Independent interior of the underside, rows 1..5 / columns 1..7. These shared
# cells create three uneven short returns rather than a central fan or flat cap.
BELLY_Y=[
 [570,595,555,575,535,570,555],
 [590,555,525,560,575,535,580],
 [605,575,540,590,550,520,565],
 [620,585,565,555,600,575,590],
 [625,600,580,615,585,550,575]
]


def make_patch(frame):
    rows,cols=7,9
    ids=np.arange(rows*cols).reshape(rows,cols)
    uv=np.stack((np.asarray(U,float),np.asarray(V_BASE,float)[:,None]+np.asarray(V_DELTA,float)),axis=-1)*.8
    local=np.concatenate((uv,np.asarray(TOP_Y,float)[...,None]),axis=2).reshape(-1,3).tolist()
    boundary=[*ids[0,:],*ids[1:,-1],*ids[-1,-2::-1],*ids[-2:0:-1,0]]
    boundary=list(map(int,boundary));assert len(boundary)==28
    faces=[]
    def grid_faces(grid,reverse=False):
        for r in range(rows-1):
            for col in range(cols-1):
                a,b,d,e=map(int,[grid[r,col],grid[r,col+1],grid[r+1,col],grid[r+1,col+1]])
                tris=[[a,b,e],[a,e,d]] if (r+col)%2 else [[a,b,d],[b,e,d]]
                faces.extend([list(reversed(t)) for t in tris] if reverse else tris)
    grid_faces(ids)
    edge_uv=np.asarray([local[i][:2] for i in boundary]);normals=[]
    for i in range(len(boundary)):
        tangent=edge_uv[(i+1)%28]-edge_uv[(i-1)%28]
        normals.append(np.array([tangent[1],-tangent[0]])/np.linalg.norm(tangent))
    rings=[boundary]
    for layer in range(3):
        ring=[]
        for i,top_id in enumerate(boundary):
            upper=np.asarray(local[top_id],float)
            p=upper.copy();p[:2]+=normals[i]*SIDE_OFFSETS[layer][i];p[2]-=SIDE_DROPS[layer][i]
            ring.append(len(local));local.append(p.tolist())
        for i in range(28):
            j=(i+1)%28;a,b=rings[-1][i],rings[-1][j];d,e=ring[i],ring[j]
            faces.extend([[a,d,b],[b,d,e]])
        rings.append(ring)
    lower=np.full((rows,cols),-1,int)
    offset=np.zeros((rows,cols,2),float)
    for top_id,lower_id in zip(boundary,rings[-1]):
        r,col=divmod(top_id,cols);lower[r,col]=lower_id
        offset[r,col]=np.asarray(local[lower_id][:2])-uv[r,col]
    # Coons interpolation extends the already authored lower boundary inwards.
    # Belly heights remain explicit; no smoothing, noise or volume union.
    for r in range(1,rows-1):
        t=r/(rows-1)
        for col in range(1,cols-1):
            s=col/(cols-1)
            corners=(1-s)*(1-t)*offset[0,0]+s*(1-t)*offset[0,-1]+(1-s)*t*offset[-1,0]+s*t*offset[-1,-1]
            displacement=(1-s)*offset[r,0]+s*offset[r,-1]+(1-t)*offset[0,col]+t*offset[-1,col]-corners
            p=uv[r,col]+displacement;lower[r,col]=len(local);local.append([*p,BELLY_Y[r-1][col-1]])
    grid_faces(lower,reverse=True)
    local=np.asarray(local,float)
    world=np.asarray(frame['anchor_godot_world_xyz'])+local[:,0,None]*np.asarray(frame['local_u_world'])+local[:,1,None]*np.asarray(frame['local_v_world'])+np.c_[np.zeros(len(local)),local[:,2],np.zeros(len(local))]
    triangles=world[np.asarray(faces)]-world[0]
    if np.einsum('ij,ij->i',triangles[:,0],np.cross(triangles[:,1],triangles[:,2])).sum()<0:
        faces=[list(reversed(face)) for face in faces]
    groups={
        'CrownA_short_top_folds':ids[1:5,1:4].ravel().tolist(),
        'CrownB_short_top_folds':ids[2:6,6:8].ravel().tolist(),
        'Shared_wide_saddle':ids[1:6,4:6].ravel().tolist(),
        'Low_front_shoulder':ids[:2,2:7].ravel().tolist(),
        'Top_outer_shared_boundary':boundary,
        'Side_upper_bulge':rings[1],'Side_inset_waist':rings[2],'Side_lower_return':rings[3],
        'Belly_A_fold':lower[1:5,1:4].ravel().tolist(),
        'Belly_shared_saddle_fold':lower[1:6,4:6].ravel().tolist(),
        'Belly_B_fold':lower[2:6,6:8].ravel().tolist()
    }
    assert world.shape==(182,3) and len(faces)==360
    edges=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]))
    assert all(count==2 for count in edges.values()),'Shared skin has an open or duplicated edge'
    return dict(vertices=world.tolist(),faces=faces,groups=groups,local_uv_y=local.tolist(),
                ring_indices=rings,top_grid=ids.tolist(),bottom_grid=lower.tolist(),
                basic_edge_incidence_two=True,final_self_intersection_validation=False,
                final_continuous_valley_validation=False,visual_acceptance=False)
