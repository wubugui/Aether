"""Double-precision narrow-phase triangle intersection diagnostics, no Blender."""
import numpy as np
EPS=1e-6  # metres; points are actual native float coordinates promoted to double


def barycentric(p,t):
    u=t[1]-t[0];v=t[2]-t[0];w=p-t[0];uu=u@u;uv=u@v;vv=v@v;wu=w@u;wv=w@v
    det=uu*vv-uv*uv
    if abs(det)<1e-20:return None
    b=(vv*wu-uv*wv)/det;c=(uu*wv-uv*wu)/det;return np.array([1-b-c,b,c])


def within(p,t):
    b=barycentric(p,t);return b is not None and b.min()>=-1e-9 and b.max()<=1+1e-9


def unique(points):
    out=[]
    for p in points:
        if not any(np.linalg.norm(p-q)<=EPS for q in out):out.append(p)
    return out


def cross2(a,b):return a[0]*b[1]-a[1]*b[0]


def coplanar_clip(a,b,normal):
    axis=int(np.argmax(abs(normal)));keep=[k for k in range(3) if k!=axis]
    aa=a[:,keep];bb=b[:,keep];sign=1 if cross2(bb[1]-bb[0],bb[2]-bb[0])>=0 else -1
    polygon=[p.copy() for p in aa]
    for p,q in zip(bb,np.roll(bb,-1,axis=0)):
        if not polygon:break
        result=[];edge=q-p
        for x,y in zip(polygon,polygon[1:]+polygon[:1]):
            dx=sign*cross2(edge,x-p);dy=sign*cross2(edge,y-p);xi=dx>=-EPS;yi=dy>=-EPS
            if xi:result.append(x)
            if xi!=yi:
                den=dx-dy
                if abs(den)>1e-20:result.append(x+(y-x)*(dx/den))
        polygon=result
    area=0.
    if len(polygon)>=3:area=abs(sum(cross2(x,y) for x,y in zip(polygon,polygon[1:]+polygon[:1])))*.5
    out=[]
    for p in polygon:
        point=np.zeros(3);point[keep]=p
        point[axis]=a[0,axis]-sum(normal[k]*(point[k]-a[0,k]) for k in keep)/normal[axis]
        out.append(point)
    # Divide projection area by the largest normal component for true3D area.
    return unique(out),area/abs(normal[axis])


def narrow_phase(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    na=np.cross(a[1]-a[0],a[2]-a[0]);nb=np.cross(b[1]-b[0],b[2]-b[0]);la=np.linalg.norm(na);lb=np.linalg.norm(nb)
    if min(la,lb)<1e-12:return dict(classification='degenerate_input',penetrating=None,points=[])
    na/=la;nb/=lb;da=(a-b[0])@nb;db=(b-a[0])@na
    base=dict(a_plane_distances_to_b_m=da.tolist(),b_plane_distances_to_a_m=db.tolist(),epsilon_m=EPS)
    if da.min()>EPS or da.max()<-EPS or db.min()>EPS or db.max()<-EPS:
        return dict(base,classification='separated_by_triangle_plane',penetrating=False,points=[])
    if max(abs(da).max(),abs(db).max())<=EPS:
        points,area=coplanar_clip(a,b,na)
        cls='coplanar_area_overlap' if area>1e-7 else 'coplanar_zero_area_contact' if points else 'coplanar_disjoint'
        return dict(base,classification=cls,penetrating=area>1e-7,overlap_area_m2=float(area),points=[p.tolist() for p in points])
    hits=[]
    for t,other,dists in ((a,b,da),(b,a,db)):
        for i in range(3):
            j=(i+1)%3;x,y=t[i],t[j];dx,dy=dists[i],dists[j]
            if abs(dx)<=EPS and within(x,other):hits.append(x)
            if (dx>EPS and dy<-EPS) or (dx<-EPS and dy>EPS):
                point=x+(y-x)*(dx/(dx-dy))
                if within(point,other):hits.append(point)
    hits=unique(hits)
    if not hits:return dict(base,classification='noncoplanar_disjoint',penetrating=False,points=[])
    longest=0.;midpoint=None
    for p in hits:
        for q in hits:
            length=float(np.linalg.norm(p-q))
            if length>longest:longest=length;midpoint=(p+q)*.5
    if longest<=EPS:return dict(base,classification='zero_length_vertex_contact',penetrating=False,points=[p.tolist() for p in hits],intersection_length_m=longest)
    ba=barycentric(midpoint,a);bb=barycentric(midpoint,b)
    strict=bool(ba.min()>1e-8 and bb.min()>1e-8)
    cls='proper_nonadjacent_segment_crossing' if strict else 'boundary_only_segment_contact'
    return dict(base,classification=cls,penetrating=strict,points=[p.tolist() for p in hits],intersection_length_m=longest,
                midpoint_barycentric_a=ba.tolist(),midpoint_barycentric_b=bb.tolist())


def counterexamples():
    a=np.array([[0.,0,0],[2,0,0],[0,2,0]])
    cases=[('proper',np.array([[.5,.5,-1],[.5,.5,1],[1.5,.5,0]]),'proper_nonadjacent_segment_crossing'),
           ('separated',a+[0,0,1],'separated_by_triangle_plane'),
           ('coplanar overlap',a+[.25,.25,0],'coplanar_area_overlap'),
           ('shared edge',np.array([[0.,0,0],[2,0,0],[1,-1,0]]),'coplanar_zero_area_contact'),
           ('coplanar disjoint',a+[4,0,0],'coplanar_disjoint')]
    for name,b,expect in cases:
        actual=narrow_phase(a,b);assert actual['classification']==expect,(name,actual)
    return len(cases)


if __name__=='__main__':print('Narrow-phase counterexamples passed:',counterexamples())
