"""Independent cliff assets with authored crest, wall, shoulder and foot sections.

Sparse reference measurements are converted into fixed metre-space modeling
controls. Godot places these complete assets as separate native prefabs.
"""
import math
import numpy as np
from cliff_terrace_topology import ground_at

# Study-only terrain cage edit underneath the southwest buttress.
# This alters native ground geometry in metre space, not camera/render data.
import copy
import world_definition as W
W.SCULPTS=copy.deepcopy(W.SCULPTS)
for cage in W.SCULPTS:
    if cage['name']!='Crown Escarpment foothills':continue
    for p in cage['points']:
        x,y,z=p
        influence=W.smooth(-5,20,x)*(1-W.smooth(90,130,x))*W.smooth(-80,-20,z)*(1-W.smooth(65,110,z))
        influence=max(influence,W.smooth(90,115,x)*(1-W.smooth(170,205,x))*W.smooth(-90,-40,z)*(1-W.smooth(60,110,z)))
        p[1]=float(y-13*influence)


F=941/(2*math.tan(math.radians(25)));P=math.radians(-3.5)
CAM=np.array([0.,145.,250.])

def ray(u,v):
    y=(470.5-v)/F
    return np.array([(u-836)/F,math.cos(P)*y+math.sin(P),math.sin(P)*y-math.cos(P)])

def survey(u,v,h):
    r=ray(u,v);return CAM+r*((h-145)/r[1])

def ground_survey(u,v):
    r=ray(u,v);lo=1.;hi=None
    for d in np.arange(10.,800.,2.):
        p=CAM+r*d
        if p[1]<=ground_at(p[0],p[2]):hi=d;break
        lo=d
    assert hi is not None,(u,v)
    for _ in range(25):
        d=(lo+hi)*.5;p=CAM+r*d
        if p[1]>ground_at(p[0],p[2]):lo=d
        else:hi=d
    return CAM+r*hi

def at_depth(u,v,z):
    r=ray(u,v);return CAM+r*((z-250)/r[2])

def make_crown(origin):
    ridge_data=[(1290,695,65),(1336,663,76),(1370,642,78),(1398,624,82),
                (1425,627,81),(1447,633,78),(1467,672,66),(1498,684,58)]
    ridge=np.array([survey(*p) for p in ridge_data])
    cap_uv=[(1287,714),(1322,699),(1352,702),(1387,699),
            (1412,687),(1437,684),(1470,707),(1504,708)]
    front=np.array([at_depth(*uv,p[2]+d) for uv,p,d in zip(cap_uv,ridge,[8,10,13,18,8,8,12,8])])
    foot=front.copy();foot[:,2]+=np.array([2,2,3,3,3,3,2,2])
    for p in foot:p[1]=ground_at(p[0],p[2])-1.2
    shoulder=ridge.copy();shoulder[:,2]-=np.array([32,37,42,45,45,44,43,38]);shoulder[:,1]-=np.array([12,15,15,9,9,11,12,8])
    # An eccentric rear shoulder gives the high outcrop breadth in both
    # horizontal axes; the crest does not extrude as a thin straight blade.
    shoulder[:,0]=origin[0]+(shoulder[:,0]-origin[0])*1.25+26
    for p in shoulder:p[1]=max(p[1],ground_at(p[0],p[2])+2)
    rear=shoulder.copy();rear[:,2]-=np.array([15,26,38,45,41,32,20,13])
    for p in rear:p[1]=ground_at(p[0],p[2])-1.2
    bench=shoulder*.48+rear*.52
    bench[:,1]+=np.array([0,2,-3,4,3,-3,2,0])
    for p in bench:p[1]=max(p[1],ground_at(p[0],p[2])+1)
    return section_volume([foot,front,ridge,shoulder,bench,rear],
        [['grass','grass','grass','grass','wall','wall','grass'],'wall','grass','slope','slope'],origin)

def make_shadow_buttress(origin):
    ridge_data=[(1008,896,31),(1040,825,42),(1110,798,48),(1162,846,35),(1190,902,26)]
    ridge=np.array([survey(*p) for p in ridge_data])
    front_uv=[(981,941),(1030,904),(1090,898),(1148,936),(1186,971)]
    front=np.array([at_depth(*uv,p[2]+d) for uv,p,d in zip(front_uv,ridge,[7,14,18,15,9])])
    foot=front.copy();foot[:,2]+=np.array([9,15,19,16,12])
    for i,p in enumerate(foot):
        p[1]=ground_at(p[0],p[2])-1.2
        front[i,1]=max(front[i,1],p[1]+3)
    shoulder=ridge.copy();shoulder[:,2]-=np.array([12,24,33,27,16]);shoulder[:,1]-=np.array([7,15,18,14,7])
    for p in shoulder:p[1]=max(p[1],ground_at(p[0],p[2])+2)
    rear=shoulder.copy();rear[:,2]-=np.array([14,26,35,29,17])
    for p in rear:p[1]=ground_at(p[0],p[2])-1.2
    return section_volume([foot,front,ridge,shoulder,rear],['wall',['grass','grass','wall','grass'],'grass','slope'],origin)

def make_central_wall(origin):
    front_data=[(1282,762,53),(1315,752,55),(1360,753,54),(1390,775,49),(1419,811,40)]
    ridge_data=[(1281,738,57),(1325,725,61),(1377,717,64),(1405,745,57),(1440,793,44)]
    front=np.array([survey(*p) for p in front_data])
    ridge=np.array([survey(*p) for p in ridge_data]);ridge[:,2]=np.minimum(ridge[:,2],front[:,2]-7)
    foot=front.copy();foot[:,2]+=np.array([5,8,13,14,7])
    for p in foot:p[1]=ground_at(p[0],p[2])-1.2
    mid=front*.43+foot*.57;mid[:,2]+=np.array([0,2,-1,2,0])
    shoulder=ridge.copy();shoulder[:,2]-=np.array([10,26,36,27,10]);shoulder[:,1]-=np.array([10,16,21,15,8])
    for p in shoulder:p[1]=max(p[1],ground_at(p[0],p[2])+2)
    rear=shoulder.copy();rear[:,2]-=np.array([12,28,37,29,12])
    for p in rear:p[1]=ground_at(p[0],p[2])-1.2
    return section_volume([foot,mid,front,ridge,shoulder,rear],['wall','wall','grass','grass','slope'],origin)

def make_front_columns(origin):
    # Three broad wall blocks retain full cap/back sections and a seated rim.
    crest=[(1168,785,44),(1229,752,52),(1278,753,52),(1320,786,43)]
    feet=[(1167,831),(1233,849),(1281,856),(1332,830)]
    front=np.array([survey(*p) for p in crest])
    foot=np.array([ground_survey(*p) for p in feet]);foot[:,1]-=1.2
    # A low sloping cap has a crest running across it, then two distinct rear
    # shoulder sections, so the complete asset stands up from every direction.
    back=front.copy();back[:,2]-=np.array([9,26,24,8])
    back[:,1]+=np.array([-1,3,1,-3])
    shoulder=back.copy();shoulder[:,2]-=np.array([8,25,26,9])
    shoulder[:,1]-=np.array([8,14,18,9])
    for p in shoulder:p[1]=max(p[1],ground_at(p[0],p[2])+2)
    rear=shoulder.copy();rear[:,2]-=np.array([12,34,30,14])
    for p in rear:p[1]=ground_at(p[0],p[2])-1.2
    mid=front*.42+foot*.58
    # Two concave channels survive as aligned edges through all wall sections.
    mid[:,2]+=np.array([0,1.2,2.2,0])
    return section_volume([foot,mid,front,back,shoulder,rear],['wall','wall','grass','grass','slope'],origin)

def make_western_slab(origin):
    crest=[(1168,785,44),(1207,758,50),(1243,759,50),(1278,753,52),(1320,786,43)]
    front=np.array([survey(*p) for p in crest]);front[:,2]-=1.0
    foot=front.copy();foot[:,2]+=2.5
    for p in foot:p[1]=ground_at(p[0],p[2])-1.2
    ridge=[(1160,752,53),(1192,735,56),(1235,695,65),(1285,727,58),(1330,769,48)]
    back=np.array([survey(*p) for p in ridge])
    # Paired sections must run rearward. The measurements describe a slope,
    # and this constraint prevents a folded crest at its narrow end.
    back[:,2]=np.minimum(back[:,2],front[:,2]-6)
    shoulder=back.copy();shoulder[:,2]-=np.array([9,24,30,25,8]);shoulder[:,1]-=np.array([8,16,14,15,7])
    for p in shoulder:p[1]=max(p[1],ground_at(p[0],p[2])+2)
    rear=shoulder.copy();rear[:,2]-=np.array([9,24,36,25,9])
    for p in rear:p[1]=ground_at(p[0],p[2])-1.2
    return section_volume([foot,front,back,shoulder,rear],['wall','grass','grass','slope'],origin)

def section_volume(profiles,strip_roles,origin):
    vertices=[];faces=[];roles=[]
    def row(values):
        ids=[]
        for p in values:ids.append(len(vertices));vertices.append((p-origin).tolist())
        return ids
    def tri(a,b,c,role):faces.append((a,b,c));roles.append(role)
    def quad(a,b,c,d,role,flip=False):
        if flip:tri(a,b,d,role);tri(b,c,d,role)
        else:tri(a,b,c,role);tri(a,c,d,role)
    rows=[row(p) for p in profiles]
    for j,(a,b) in enumerate(zip(rows,rows[1:])):
        role=strip_roles[j]
        for k in range(len(a)-1):quad(a[k],a[k+1],b[k+1],b[k],role[k] if isinstance(role,list) else role,k%2==0)
    # Close left and right flanks with actual ground-foot strips. The flanks
    # have their own width, rather than a fan ending in one cap vertex.
    sides=[]
    for side in [0,-1]:
        sign=-1 if side==0 else 1
        edge=[r[side] for r in rows]
        foot_side=[]
        for j,index in enumerate(edge):
            if j in (0,len(edge)-1):foot_side.append(index);continue
            p=np.array(vertices[index])+origin
            p[0]+=sign*(4+2*math.sin(j*1.4));p[1]=ground_at(p[0],p[2])-1.2
            foot_side+=row([p])
        for j in range(len(edge)-1):
            if j==0:tri(edge[j],edge[j+1],foot_side[j+1],'slope')
            elif j==len(edge)-2:tri(edge[j],edge[j+1],foot_side[j],'slope')
            else:quad(edge[j],edge[j+1],foot_side[j+1],foot_side[j],'slope',j%2==0)
        sides.append(foot_side)
    boundary=rows[0]+sides[1][1:-1]+rows[-1][::-1]+sides[0][-2:0:-1]
    # The foot's actual terrain contact is independent of the broad wall
    # sections. Sample the lower rim every four metres before closing it.
    # Only the boundary triangle is split, leaving the upper wall intact.
    seated=[]
    for j,a in enumerate(boundary):
        b=boundary[(j+1)%len(boundary)];aa=np.array(vertices[a]);bb=np.array(vertices[b])
        count=max(1,math.ceil(np.linalg.norm((bb-aa)[[0,2]])/4))
        curve=[a]
        for k in range(1,count):
            p=aa*(1-k/count)+bb*(k/count)
            p[1]=min(p[1],ground_at(p[0]+origin[0],p[2]+origin[2])-1.5)
            curve.append(len(vertices));vertices.append(p.tolist())
        curve.append(b);seated.extend(curve[:-1])
        if count==1:continue
        matching=[i for i,f in enumerate(faces) if a in f and b in f]
        assert len(matching)==1,(a,b,matching)
        index=matching[0];face=faces[index];role=roles[index];c=next(k for k in face if k not in (a,b))
        if face[(face.index(a)+1)%3]!=b:curve.reverse()
        replacements=[(c,x,y) for x,y in zip(curve,curve[1:])]
        faces[index]=replacements[0]
        for f in replacements[1:]:faces.append(f);roles.append(role)
    boundary=seated
    # Flatten a copy of the actual surface topology for the closed bottom.
    # A center fan can overlap itself when the footprint is concave or the
    # asset origin lies outside its kernel, even though all edges are paired.
    roof=list(faces);floor_map={};flat_lookup={}
    for k in range(len(vertices)):
        x,_,z=vertices[k];key=(round(x,7),round(z,7))
        if key not in flat_lookup:
            flat_lookup[key]=len(vertices);vertices.append([x,-15.,z])
        floor_map[k]=flat_lookup[key]
    lower=[floor_map[k] for k in boundary]
    for j,k in enumerate(boundary):
        n=(j+1)%len(boundary);quad(k,boundary[n],lower[n],lower[j],'buried')
    for a,b,c in roof:
        fa,fb,fc=floor_map[a],floor_map[b],floor_map[c]
        p,q,r=np.array([vertices[k] for k in (fa,fb,fc)])[:,[0,2]]
        if abs(float(np.cross(q-p,r-p)))>1e-8:tri(fc,fb,fa,'buried')
    return vertices,faces,roles
