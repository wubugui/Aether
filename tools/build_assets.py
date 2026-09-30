"""Deterministic, editable low-poly geometry. No reference-image textures are used.
Run with Python + numpy + scipy to regenerate the GLB source assets.
"""
from pathlib import Path
import math, json, struct
import numpy as np
from scipy.spatial import Delaunay, ConvexHull

ROOT = Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(27)

def rgb(s):
    return np.array([int(s[i:i+2],16)/255 for i in (0,2,4)])

SUN = np.array([-0.48, 0.82, 0.30])
SUN /= np.linalg.norm(SUN)

class Mesh:
    def __init__(self, name):
        self.name=name; self.p=[]; self.c=[]; self.n=[]
    def tri(self,a,b,c,color,shade=True):
        a,b,c = np.asarray(a),np.asarray(b),np.asarray(c)
        n=np.cross(b-a,c-a); n=n/max(np.linalg.norm(n),1e-8)
        col=np.asarray(color)[:3].copy()
        if shade:
            light=max(0,np.dot(n,SUN))
            if self.name=='Clouds':
                col=col*(.86+.14*light)+np.array([.0,.003,.020])*(1-light)
            else: col *= 0.73+0.27*light
        self.p.extend([a,b,c]); self.n.extend([n,n,n]); self.c.extend([np.r_[np.clip(col,0,1),1]]*3)
    def quad(self,a,b,c,d,col,shade=True):
        self.tri(a,b,c,col,shade); self.tri(a,c,d,col,shade)
    def box(self,center,size,col):
        p=np.array(center); x,y,z=np.array(size)*0.5
        v=[p+q for q in [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]]
        for a,b,c,d in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:self.quad(v[a],v[b],v[c],v[d],col)
    def rod(self,a,b,r,col,sides=6,r2=None):
        a,b=np.array(a,dtype=float),np.array(b,dtype=float)
        d=b-a; d/=max(np.linalg.norm(d),1e-8)
        u=np.cross(d,[0,1,0] if abs(d[1])<0.9 else [1,0,0]); u/=np.linalg.norm(u)
        v=np.cross(d,u); r2=r if r2 is None else r2
        ring=[u*math.cos(i*2*math.pi/sides)+v*math.sin(i*2*math.pi/sides) for i in range(sides)]
        for i in range(sides):
            j=(i+1)%sides
            self.quad(a+ring[i]*r,a+ring[j]*r,b+ring[j]*r2,b+ring[i]*r2,col)
            self.tri(b,b+ring[i]*r2,b+ring[j]*r2,col)
    def ellipsoid(self,center,radii,col,rings=6,segs=10,jitter=0.07):
        p=np.array(center); radii=np.array(radii)
        vertices=[p+np.array([0,-1,0])*radii]
        for j in range(1,rings):
            lat=-math.pi/2+math.pi*j/rings
            for i in range(segs):
                angle=2*math.pi*(i+(j%2)*0.36)/segs
                q=np.array([math.cos(lat)*math.cos(angle),math.sin(lat),math.cos(lat)*math.sin(angle)])
                vertices.append(p+q*radii*(1+RNG.uniform(-jitter,jitter)))
        vertices.append(p+np.array([0,1,0])*radii)
        vertices=np.array(vertices)
        hull=ConvexHull(vertices)
        for face in hull.simplices:
            a,b,c=vertices[face]
            if np.dot(np.cross(b-a,c-a),(a+b+c)/3-p)<0:b,c=c,b
            self.tri(a,b,c,np.asarray(col)*RNG.uniform(.965,1.03))

def save_glb(meshes,filename):
    blob=bytearray(); accessors=[]; views=[]; glmeshes=[]; nodes=[]
    def arr(data,type_):
        nonlocal blob
        data=np.asarray(data,dtype='<f4')
        while len(blob)%4:blob.append(0)
        offset=len(blob); raw=data.tobytes(); blob.extend(raw)
        views.append(dict(buffer=0,byteOffset=offset,byteLength=len(raw),target=34962))
        accessor=dict(bufferView=len(views)-1,componentType=5126,count=len(data),type=type_)
        if type_=='VEC3':accessor.update(min=data.min(axis=0).tolist(),max=data.max(axis=0).tolist())
        accessors.append(accessor); return len(accessors)-1
    for m in meshes:
        if not m.p:continue
        att={'POSITION':arr(m.p,'VEC3'),'NORMAL':arr(m.n,'VEC3'),'COLOR_0':arr(m.c,'VEC4')}
        glmeshes.append(dict(name=m.name,primitives=[dict(attributes=att,material=0,mode=4)]))
        nodes.append(dict(name=m.name,mesh=len(glmeshes)-1))
    doc=dict(asset=dict(version='2.0',generator='Airship Vista procedural authoring'),scene=0,scenes=[dict(nodes=list(range(len(nodes))))],nodes=nodes,meshes=glmeshes,buffers=[dict(byteLength=len(blob))],bufferViews=views,accessors=accessors,materials=[dict(name='Baked pastel palette',doubleSided=True,pbrMetallicRoughness=dict(baseColorFactor=[1,1,1,1],metallicFactor=0,roughnessFactor=1))])
    js=json.dumps(doc,separators=(',',':')).encode(); js+=b' '*((-len(js))%4)
    blob+=b'\0'*((-len(blob))%4)
    out=struct.pack('<III',0x46546c67,2,12+8+len(js)+8+len(blob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob
    (ROOT/'assets'/filename).write_bytes(out)
    print(filename, len(out)//1024,'KB',sum(len(m.p)//3 for m in meshes),'triangles')

RIVER=np.array([[-1900,-1000],[-1200,-840],[-850,-720],[-580,-560],[-380,-470],[-230,-520],[-120,-710],[90,-760],[280,-660],[450,-700],[650,-850],[950,-920],[1350,-1150],[1900,-1550],[2800,-1850]])

def river_distance(x,z):
    x,z=np.broadcast_arrays(np.asarray(x),np.asarray(z)); result=np.full(x.shape,1e9)
    for a,b in zip(RIVER[:-1],RIVER[1:]):
        d=b-a; t=np.clip(((x-a[0])*d[0]+(z-a[1])*d[1])/np.dot(d,d),0,1)
        result=np.minimum(result,np.sqrt((x-a[0]-t*d[0])**2+(z-a[1]-t*d[1])**2))
    return result

def noise(x,z):
    return (np.sin(x*.018+z*.009)*np.cos(z*.024-x*.008)*.5+np.sin(x*.049+z*.039)*.23+np.cos(x*.089-z*.072)*.14+np.sin(z*.19+x*.15)*.06)

PEAKS=[(960,-2370,450,440),(760,-2490,378,390),(1100,-2600,398,365),(670,-2220,285,315),(1320,-2630,305,380),(1150,-2130,258,270),(450,-2310,190,300),(1510,-2530,230,300),(1720,-2960,250,450),
       (240,0,105,125),(155,-55,92,80),(320,-160,93,135),(390,-270,56,155),(145,-170,42,80),(-530,-700,96,145),(-305,-820,39,110),(-180,-420,42,68),(-690,-1100,102,160),(-1390,-1800,150,280),(850,-690,70,190),(-55,-40,18,44)]

def height(x,z):
    x,z=np.broadcast_arrays(np.asarray(x),np.asarray(z))
    n=noise(x,z)
    y=10+n*3.5+np.sin(x*.006-z*.011)*5+np.sin(x*.013+z*.009)*2.5
    mountain=np.zeros_like(y)
    for px,pz,h,r in PEAKS:
        dx=(x-px)/r; dz=(z-pz)/r
        d=np.sqrt(dx*dx+dz*dz)
        angle=np.arctan2(dz,dx)
        shape=np.maximum(0,1-d*(1+np.sin(angle*5+px)*.10+np.sin(angle*9)*.06))
        peak=h*shape**1.35
        mountain=np.maximum(mountain,peak)
    y+=mountain*(.94+n*.14)
    # An open western sea meeting the foreground peninsula.
    coast=np.interp(z,[-1800,-800,-540,-430,-320,-220,-100,0,100,220],[-1500,-1100,-640,-270,-230,-185,-95,-55,35,50])
    coast+=np.sin(z*.035)*11+np.sin(z*.087)*4
    ocean=np.clip((x-coast)/28,-1,1)
    y=np.where((z>-900)&(x<coast+28),np.minimum(y, ocean*13),y)
    river=river_distance(x,z)
    rw=43+10*(np.sin(x*.004)+1)
    river_height=(river-rw)*.28
    y=np.where(river<rw+46,np.minimum(y,river_height),y)
    return y

def terrain():
    pts=[]
    for step,xlim,zmin,zmax in [(17,1050,-950,180),(26,3000,-2900,-900),(110,11000,-12000,-2800)]:
        xs=np.arange(-xlim,xlim+1,step); zs=np.arange(zmin,zmax+1,step)
        xx,zz=np.meshgrid(xs,zs); p=np.c_[xx.ravel(),zz.ravel()].astype(float)
        p+=RNG.uniform(-step*.39,step*.39,p.shape); pts.append(p)
    pts=np.concatenate(pts); y=height(pts[:,0],pts[:,1]); verts=np.c_[pts[:,0],y,pts[:,1]]
    faces=Delaunay(pts).simplices
    m=Mesh('Terrain'); shores=Mesh('Shoreline')
    greens=[rgb(c) for c in ['a2b17b','aebb84','b2bc89','b5bf8a','a6b37d','9eac7b','bfc596','96a881','aeb982']]
    for f in faces:
        p=verts[f]; a,b,c=p; avg=p.mean(axis=0)
        if np.cross(b-a,c-a)[1]<0:b,c=c,b
        nn=np.cross(b-a,c-a); nn/=max(np.linalg.norm(nn),1e-8)
        h=avg[1]; col=greens[RNG.integers(len(greens))].copy()
        if h<2.3:col=rgb('d5ceaa')*RNG.uniform(.97,1.025)
        elif h<5.0:col=rgb('b9bd86')*RNG.uniform(.97,1.025)
        if nn[1]<.83 and h>24: col=rgb('999e98')*RNG.uniform(.91,1.07)
        if h>140 and avg[2]<-1800:
            col=rgb('b0bccc')*RNG.uniform(.91,1.04)
            if h>190+22*math.sin(avg[0]*.025)+25*(1-nn[1]):col=rgb('eef0ed')*RNG.uniform(.965,1.03)
        m.tri(a,b,c,col)
        # Real contour strips follow every zero crossing of the terrain mesh.
        crossings=[]
        for u,v in [(a,b),(b,c),(c,a)]:
            if (u[1]>.35)!=(v[1]>.35):
                t=(.35-u[1])/(v[1]-u[1]); crossings.append(u+(v-u)*t)
        if len(crossings)==2:
            u,v=crossings; d=v-u; side=np.cross(d,[0,1,0]); side/=max(np.linalg.norm(side),1e-8)
            w=.65 if avg[2]>-800 else 1.2
            shores.quad(u+side*w,v+side*w,v-side*w,u-side*w,rgb('cadcce'),False)
    return m,shores

def details():
    trees=Mesh('Groves'); houses=Mesh('Hamlets'); roads=Mesh('Paths'); fields=Mesh('Fields')
    for i in range(4200):
        z=RNG.uniform(-2700,60); x=RNG.uniform(-2300,2300); h=float(height(x,z))
        if h<5 or h>75:continue
        if noise(x*.45+900,z*.45)<-.10:continue
        scale=RNG.uniform(1.4,3.5)
        p=np.array([x,h,z]); trees.rod(p,p+[0,scale*1.2,0],scale*.10,rgb('767d5b'),5)
        trees.ellipsoid(p+[0,scale*1.45,0],[scale*.78,scale*1.45,scale*.73],rgb('788d60')*RNG.uniform(.85,1.1),4,5,.16)
        # Ground contact shadow.
        r=scale*1.0; trees.quad(p+[-r,.07,-r*.5],p+[-r,.07,r*.5],p+[r,.07,r*.5],p+[r,.07,-r*.5],rgb('879b68'),False)
    centers=[(-100,-280),(38,-480),(80,-620),(-390,-680),(-580,-750),(520,-950),(-820,-1150),(740,-1450),(320,-520),(200,-1200),(-240,-1380),(1050,-1550)]
    def house(x,z,s):
        y=float(height(x,z)); p=np.array([x,y+s*.6,z]); houses.box(p,[s*1.3,s*1.2,s],rgb('cbc4a1'))
        roof=rgb('95977c')*RNG.uniform(.85,1.1); x0=x-s*.78;x1=x+s*.78;z0=z-s*.65;z1=z+s*.65;y0=y+s*1.2;y1=y+s*1.9
        houses.quad([x0,y0,z0],[x1,y0,z0],[x1,y1,z],[x0,y1,z],roof)
        houses.quad([x0,y1,z],[x1,y1,z],[x1,y0,z1],[x0,y0,z1],roof)
        houses.tri([x0,y0,z0],[x0,y1,z],[x0,y0,z1],rgb('b8b899'))
        houses.box([x,y+s*.32,z+s*.502],[s*.23,s*.62,.08],rgb('72745e'))
    for cx,cz in centers:
        for k in range(RNG.integers(5,16)):
            x=cx+RNG.normal(0,14);z=cz+RNG.normal(0,14)
            if float(height(x,z))>5:house(x,z,RNG.uniform(1.7,3.8))
    # Winding pale tracks draped onto the mesh.
    for i,(cx,cz) in enumerate(centers):
        target=centers[(i+1)%len(centers)]
        if np.linalg.norm(np.array(target)-[cx,cz])>650:continue
        prev=None
        for t in np.linspace(0,1,110):
            x=cx*(1-t)+target[0]*t+math.sin(t*17+i)*6
            z=cz*(1-t)+target[1]*t+math.sin(t*22)*4
            p=np.array([x,float(height(x,z))+.22,z])
            if prev is not None and p[1]>3 and prev[1]>3:
                d=p-prev; n=np.cross(d,[0,1,0]);n/=max(np.linalg.norm(n),1e-8);n*=1.0
                roads.quad(prev-n,prev+n,p+n,p-n,rgb('d0caa0'),False)
            prev=p
    # The little cream-stone citadel on the central peninsula.
    cx,cz=52,-530; base=float(height(cx,cz)); stone=rgb('d4c79a')
    for x,z,w,h,d in [(-14,0,4,18,4),(13,0,5,16,5),(14,-17,4,14,4),(-14,-17,4,15,4),(0,-10,10,13,8),(0,-10,4,23,4)]:
        houses.box([cx+x,base+h*.5,cz+z],[w,h,d],stone)
        houses.rod([cx+x,base+h,cz+z],[cx+x,base+h+4,cz+z],w*.65,rgb('b6aa7f'),4,0)
    for a,b in [((-14,0),(13,0)),((-14,-17),(14,-17)),((-14,0),(-14,-17)),((14,0),(14,-17))]:
        mid=(np.array(a)+b)*.5; d=np.abs(np.array(b)-a)
        houses.box([cx+mid[0],base+3,cz+mid[1]],[max(1.8,d[0]),6,max(1.8,d[1])],stone)
        for t in np.linspace(0,1,10):
            q=np.array(a)*(1-t)+np.array(b)*t
            houses.box([cx+q[0],base+6.6,cz+q[1]],[1.8,1.3,1.8],stone)
    return trees,houses,roads,fields

def clouds():
    m=Mesh('Clouds')
    # Projected placement matches the reference's characteristic cloud banks.
    # x/y here are reference-image design coordinates, d is camera distance.
    for sx,sy,width,d in [(1107,180,235,1600),(791,283,230,1800),(400,345,168,2100),(45,310,260,1600),(1245,204,92,2200),(650,323,60,2600),(1700,320,160,1900),(1370,353,55,2600),(265,395,120,3300),(-10,398,120,3000)]:
        f=941/(2*math.tan(math.radians(25))); x=(sx-836)/f*d; y=145+(470.5-sy)/f*d-d*.06116;z=250-d
        w=width/f*d
        for ox,oy,s in [(-.45,-.014,.17),(-.21,.01,.22),(.06,.095,.27),(.27,-.014,.22),(.46,-.036,.18)]:
            before=len(m.p)
            m.ellipsoid([x+w*ox,y+w*oy,z+RNG.uniform(-w*.04,w*.04)],[w*s,w*s*(.77 if ox==.06 else .33),w*s*.30],rgb('fcfaf8'),5,8,.12)
            # Flat underside, tall rounded lobes, slim wisps at the edges.
            for i in range(before,len(m.p)):
                m.p[i][1]=max(m.p[i][1],y-w*.055+RNG.uniform(-.4,.4))
    return m

def ship():
    envelope=Mesh('Envelope'); rig=Mesh('Rigging'); boat=Mesh('Gondola'); prop=Mesh('Propeller');flag=Mesh('Flag')
    cream=rgb('efe3c9'); rope=rgb('776a4b'); wood=rgb('70563e'); dark=rgb('4e4638'); brass=rgb('b6a27a')
    # A triangulated longitudinal hull; seams follow its elliptical sections.
    ns=16; nl=10; vs=[]
    for j in range(nl+1):
        a=math.pi*j/nl; x=-6.15*math.cos(a); r=max(.025,math.sin(a))
        ring=[]
        for k in range(ns):
            theta=k*math.tau/ns; taper=1+RNG.uniform(-.035,.035) if 0<j<nl else 1
            ring.append(np.array([x,4.7+3.90*r*math.cos(theta)*taper,3.15*r*math.sin(theta)*taper]))
        vs.append(ring)
    for j in range(nl):
        for k in range(ns):
            a,b,c,d=vs[j][k],vs[j][(k+1)%ns],vs[j+1][(k+1)%ns],vs[j+1][k]
            envelope.tri(a,b,c,cream*RNG.uniform(.96,1.035)); envelope.tri(a,c,d,cream*RNG.uniform(.96,1.035))
    # Full circumference leather bands, lighter inset stitching and brass clasps.
    for x in [-5.70,-.1,4.5]:
        r=math.sqrt(1-(x/6.15)**2)
        for k in range(48):
            t=k*math.tau/48; u=(k+1)*math.tau/48
            a=[x,4.7+3.95*r*math.cos(t),3.2*r*math.sin(t)]
            b=[x,4.7+3.95*r*math.cos(u),3.2*r*math.sin(u)]
            rig.rod(a,b,.066,rope,5)
            rig.rod(np.array(a)+[-.06,0,0],np.array(b)+[-.06,0,0],.016,rgb('c4b895'),4)
            if k%8==0:rig.box(a,[.22,.13,.18],brass)
    # Nose spindle and rear propeller mount.
    rig.rod([-6.75,4.3,0],[-5.9,4.3,0],.11,dark,8,.30)
    rig.ellipsoid([-6.15,4.3,0],[.28,.32,.33],rgb('817d69'),4,8,0)
    rig.rod([5.3,3.6,0],[6.8,3.6,0],.12,wood,8)
    # Suspension cables.
    for x in [-4.6,3.7]:
        for z in [-1.7,1.7]:
            rig.rod([x,2.6,z],[x*.59,-1.55,z*.65],.040,rope,5)
            rig.rod([x*.76,1.05,z*1.18],[x*.59,-1.55,z*.65],.027,rgb('a59672'),5)
    # Curved wooden boat with planks constructed as separate hull strips.
    sections=[(-3.6,.16,-1.68,-2.1),(-2.8,1.02,-1.70,-3.55),(-1.45,1.24,-1.78,-3.9),(1.1,1.15,-1.80,-3.80),(2.7,.73,-1.52,-3.20),(3.45,.12,-1.17,-2.0)]
    for j in range(len(sections)-1):
        x,w,top,bot=sections[j];xx,ww,tt,bb=sections[j+1]
        for side in [-1,1]:
            for row in range(5):
                t=row/5;u=(row+1)/5
                def pos(ax,aw,at,ab,f):return [ax,at*(1-f)+ab*f,side*aw*(1-.55*f*f)]
                a,b,c,d=pos(x,w,top,bot,t),pos(x,w,top,bot,u),pos(xx,ww,tt,bb,u),pos(xx,ww,tt,bb,t)
                boat.quad(a,b,c,d,wood*RNG.uniform(.90,1.1))
                rig.rod(a,d,.032,rgb('a18b61'),5)
            rig.rod([x,top,side*w],[xx,tt,side*ww],.085,brass,6)
        boat.quad([x,top,-w],[xx,tt,-ww],[xx,tt,ww],[x,top,w],rgb('8c7554'))
    for x,w,top,bot in sections[1:-1]:
        for side in [-1,1]:
            rig.rod([x,top,side*(w+.01)],[x,(top+bot)*.5,side*w*.88],.055,dark,5)
            rig.rod([x,(top+bot)*.5,side*w*.88],[x,bot,side*w*.45],.055,dark,5)
    # Cabin, window panes, mullions, roof, exhaust, rails, sacks and hanging lantern.
    boat.box([.65,-.97,0],[2.15,1.45,1.85],rgb('655139'))
    boat.box([.55,-.16,0],[2.5,.20,2.12],dark)
    for x in [-.08,.56,1.20]:
        boat.box([x,-.78,.947],[.42,.75,.06],rgb('9c9b84'))
        boat.box([x,-.78,.984],[.044,.82,.04],brass)
    for x in [-.65,1.78]:boat.box([x,-.93,.97],[.10,1.35,.10],brass)
    boat.box([-.72,-.73,0],[.57,1.58,1.17],rgb('594c37'))
    rig.rod([-.64,.04,-.13],[-.64,.64,-.13],.15,dark,6)
    for x in np.linspace(-2.7,2.65,10):
        rig.rod([x,-1.74,1.10],[x,-1.23,1.10],.04,brass,5)
    rig.rod([-2.9,-1.23,1.10],[2.7,-1.23,1.1],.055,brass,5)
    for x in [1.1,1.75,2.4]:
        boat.ellipsoid([x,-2.04,1.15],[.30,.52,.26],rgb('d6c9a0'),5,7,.04)
        rig.rod([x,-1.5,1.14],[x,-2.3,1.37],.025,rope,4)
    rig.rod([4.15,1.2,.8],[4.15,-.33,.8],.024,rope,4)
    boat.box([4.15,-.65,.8],[.47,.61,.39],dark)
    boat.box([4.15,-.65,1.0],[.28,.36,.025],rgb('d3a86d'))
    # Mast and a forked red pennant.
    rig.rod([.55,8.6,0],[.65,11.0,0],.045,wood,5)
    rig.ellipsoid([.55,8.65,0],[.35,.10,.23],brass,3,7,0)
    flag.quad([.67,9.9,0],[1.50,9.69,.02],[1.50,9.13,.05],[.65,9.12,0],rgb('a74d3e'),False)
    flag.tri([1.5,9.69,.02],[2.7,9.75,.14],[2.18,9.42,.05],rgb('ae5140'),False)
    flag.tri([1.5,9.69,.02],[2.18,9.42,.05],[1.5,9.13,.05],rgb('ae5140'),False)
    flag.tri([1.5,9.13,.05],[2.18,9.42,.05],[2.83,9.13,-.01],rgb('a6503d'),False)
    # Propeller geometry is local to a separate animated pivot.
    for k in range(4):
        angle=k*math.pi/2+.15; u=np.array([0,math.cos(angle),math.sin(angle)]);v=np.array([0,-math.sin(angle),math.cos(angle)])
        center=np.array([0.,0.,0.])
        poly=[center+u*.22-v*.09,center+u*1.78-v*.30,center+u*1.95+v*.10,center+u*1.71+v*.33,center+u*.23+v*.13]
        for i in range(1,len(poly)-1):prop.tri(poly[0],poly[i],poly[i+1],rgb('997354')*RNG.uniform(.92,1.07))
    prop.rod([-.14,0,0],[.20,0,0],.21,brass,8)
    for p in flag.p:p[1]+=1
    save_glb([envelope,rig,boat,flag],'airship.glb');save_glb([prop],'propeller.glb')

if __name__=='__main__':
    save_glb([*terrain(),*details(),clouds()],'world.glb')
    ship()
