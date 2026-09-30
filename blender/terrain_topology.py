"""Native Blender constrained terrain topology and exact mesh-height sampling.

The mesh follows metre-space shore, channel and ridge geometry. Its triangles
are also used to place every tree/house/road; no screenshot pixels are sampled.
"""
import math
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
import world_definition as W

def normals(points):
    p=np.asarray(points,float)
    tangent=np.empty_like(p)
    tangent[0]=p[1]-p[0];tangent[-1]=p[-1]-p[-2]
    tangent[1:-1]=p[2:]-p[:-2]
    tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-9)
    return np.c_[-tangent[:,1],tangent[:,0]]

def world_constraints():
    lines=[]
    coast=np.array([[p[1],p[0]] for p in W.COAST],float)
    n=-normals(coast)  # Mainland lies east of the western coastline.
    for offset,h in [(0,0),(3,.65),(9,2.7),(22,6.5),(-5,-4)]:
        lines.append((coast+n*offset,h))
    for channel_index,channel in enumerate(W.RIVERS):
        if channel_index==0 and W.WATER_REGIONS:continue
        p=np.asarray(channel['banks'][0]+channel['banks'][1][::-1],float)
        area=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])
        tangent=np.roll(p,-1,axis=0)-np.roll(p,1,axis=0)
        tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-9)
        outward=np.c_[tangent[:,1],-tangent[:,0]]*np.sign(area)
        for offset,h in [(0,0),(2.0,1.3),(5.5,6),(-5,-5)]:
            bank=p+outward*offset;lines.append((np.r_[bank,bank[:1]],h))
    for region in W.WATER_REGIONS:
        for ring_index,ring in enumerate([region['outer']]+region['holes']):
            p=np.asarray(ring,float)
            area=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])
            tangent=np.roll(p,-1,axis=0)-np.roll(p,1,axis=0)
            tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-9)
            land=np.c_[tangent[:,1],-tangent[:,0]]*np.sign(area)*(1 if ring_index==0 else -1)
            for offset,h in [(0,0),(1.2,.35),(8,2.8),(20,7),(-3,-4)]:
                points=p+land*offset;lines.append((np.r_[points,points[:1]],h))
    # Explicit broad ridge fans and plateau perimeter rings.
    # This near-shore island is smaller than the regular terrain spacing.
    # Add its low plateau and shoreline as geometric constraints so it does
    # not collapse to a single triangle with a needle-like highest vertex.
    px,pz,top,*_=W.PEAKS[22]
    for radius in [.30,.705,.93]:
        ring=[]
        for i in range(11):
            a=math.tau*i/10
            r=radius/(1+.10*math.sin(a*5))
            ring.append([px+37*r*math.cos(a),pz+29*r*math.sin(a)])
        lines.append((np.asarray(ring),None))
    for peak_index,(px,pz,top,r,flat,jag) in enumerate(W.PEAKS[:26]):
        if 16<=peak_index<=21 and W.SCULPTS:continue
        center=np.array([px,pz])
        ring=[]
        for i in range(9):
            angle=math.tau*i/8
            radius=r*(flat if flat>.2 else .48)*(1+.07*math.sin(i*13+px))
            ring.append(center+np.array([math.cos(angle),math.sin(angle)])*radius)
        lines.append((np.asarray(ring),None))
        for p in ring[::2]:lines.append((np.asarray([center,p]),None))
    for sculpt in W.SCULPTS:
        points=np.asarray(sculpt['points'])[:,[0,2]];edges=set()
        for tri in sculpt['triangles']:
            for a,b in zip(tri,tri[1:]+tri[:1]):edges.add(tuple(sorted((a,b))))
        for a,b in edges:lines.append((points[[a,b]],None))
    segments=[]
    for points,y in lines:
        for a,b in zip(points[:-1],points[1:]):
            segments.append((a,b,y))
    return segments

SEGMENTS=world_constraints()

def clip_segment(a,b,x0,z0,x1,z1):
    d=b-a;lo=0.;hi=1.
    for p,q in [(-d[0],a[0]-x0),(d[0],x1-a[0]),(-d[1],a[1]-z0),(d[1],z1-a[1])]:
        if abs(p)<1e-10:
            if q<0:return None
        elif p<0:lo=max(lo,q/p)
        else:hi=min(hi,q/p)
        if lo>hi:return None
    return a+d*lo,a+d*hi

def chunk_mesh(cx,cz):
    ox,oz=cx*W.CHUNK,cz*W.CHUNK
    coords=[];forced=[];lookup={};edges=[]
    def point(p,h=None):
        p=np.clip(np.asarray(p)-[ox,oz],0,W.CHUNK)
        key=tuple(np.round(p,5))
        if key in lookup:
            index=lookup[key]
            if h is not None:forced[index]=h if forced[index] is None else min(h,forced[index])
            return index
        index=len(coords);lookup[key]=index;coords.append(Vector(key));forced.append(h)
        return index
    # Shared straight tile boundaries, with finer irregular interior near shore.
    spacing=12 if -1<=cx<=1 and -2<=cz<=0 else 24
    for z in np.arange(0,W.CHUNK+1,spacing):
        for x in np.arange(0,W.CHUNK+1,spacing):
            if (x==0 or x==W.CHUNK) and z%24:continue
            if (z==0 or z==W.CHUNK) and x%24:continue
            if x in (0,W.CHUNK) or z in (0,W.CHUNK):px,pz=ox+x,oz+z
            else:
                px=ox+x+(math.sin((ox+x)*1.317+(oz+z)*2.37)*.5)*spacing
                pz=oz+z+(math.sin((ox+x)*2.171-(oz+z)*1.913)*.5)*spacing
                if any(s['name']=='Frostpeak alpine range' and s['bounds'][0]<px<s['bounds'][2] and s['bounds'][1]<pz<s['bounds'][3] for s in W.SCULPTS) and (x%48 or z%48):continue
            point([px,pz])
    for a,b,y in SEGMENTS:
        clipped=clip_segment(a,b,ox,oz,ox+W.CHUNK,oz+W.CHUNK)
        if clipped is None:continue
        aa,bb=clipped;distance=np.linalg.norm(bb-aa)
        if distance<.001:continue
        count=max(1,math.ceil(distance/(8 if y is not None else 32)))
        prior=None
        for t in np.linspace(0,1,count+1):
            index=point(aa*(1-t)+bb*t,y)
            if prior is not None and prior!=index:edges.append((prior,index))
            prior=index
    for px,pz,top,*rest in W.PEAKS:
        if ox<=px<=ox+W.CHUNK and oz<=pz<=oz+W.CHUNK:point([px,pz])
    verts,_,faces,orig,_,_=delaunay_2d_cdt(coords,edges,[],0,.0001,True)
    xy=np.asarray(verts,float)
    heights=W.height(xy[:,0]+ox,xy[:,1]+oz)
    for i,indices in enumerate(orig):
        values=[forced[k] for k in indices if forced[k] is not None]
        if values:heights[i]=min(min(values),heights[i]) if heights[i]<0 else min(values)
    # The outer authored boundary meets the coarser streaming mesh exactly.
    for axis,other,cell,minimum,maximum in [(0,1,cx,W.BOUNDS[0],W.BOUNDS[1]),(1,0,cz,W.BOUNDS[2],W.BOUNDS[3])]:
        for boundary,active in [(0,cell==minimum),(W.CHUNK,cell==maximum)]:
            if not active:continue
            mask=np.abs(xy[:,axis]-boundary)<.001
            for i in np.flatnonzero(mask):
                coord=xy[i]+[ox,oz];q=math.floor(coord[other]/24)*24
                a=coord.copy();b=coord.copy();a[other]=q;b[other]=q+24
                blend=(coord[other]-q)/24
                heights[i]=float(W.height(*a))*(1-blend)+float(W.height(*b))*blend
    vertices=np.c_[xy[:,0],heights,xy[:,1]]
    faces=np.asarray(faces,dtype=np.int32)
    tri=vertices[faces]
    upward=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])[:,1]
    faces[upward<0]=faces[upward<0][:,[0,2,1]]
    area=np.abs(upward)
    faces=faces[area>1e-7]
    return vertices,faces

class SurfaceSampler:
    def __init__(self):self.tiles={};self.misses=0
    def add(self,cx,cz,vertices,faces):
        tri=vertices[faces].copy();buckets={}
        lower=np.floor(np.min(tri[:,:,[0,2]],axis=1)/24).astype(int)
        upper=np.floor(np.max(tri[:,:,[0,2]],axis=1)/24).astype(int)
        for i,(a,b) in enumerate(zip(lower,upper)):
            for z in range(max(0,a[1]),min(31,b[1])+1):
                for x in range(max(0,a[0]),min(31,b[0])+1):buckets.setdefault((x,z),[]).append(i)
        self.tiles[(cx,cz)]=(tri,buckets)
    def height(self,x,z):
        x,z=np.broadcast_arrays(np.asarray(x,float),np.asarray(z,float))
        shape=x.shape;x=x.ravel();z=z.ravel();result=np.empty_like(x)
        cells=np.c_[np.floor(x/W.CHUNK),np.floor(z/W.CHUNK)].astype(int)
        for cell in np.unique(cells,axis=0):
            selected=np.flatnonzero(np.all(cells==cell,axis=1));key=tuple(cell)
            if key not in self.tiles:
                result[selected]=W.surface_height(x[selected],z[selected]);continue
            tri,buckets=self.tiles[key]
            local=np.c_[x[selected]-cell[0]*W.CHUNK,z[selected]-cell[1]*W.CHUNK]
            bins=np.clip(np.floor(local/24).astype(int),0,31)
            for bucket in np.unique(bins,axis=0):
                take=np.flatnonzero(np.all(bins==bucket,axis=1))
                indices=buckets.get(tuple(bucket),[])
                if not indices:raise ValueError(f'Empty terrain bucket {key} {bucket}')
                t=tri[indices];a=t[:,0];b=t[:,1];c=t[:,2]
                p=local[take]
                den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2])
                wa=((b[:,2]-c[:,2])*(p[:,0,None]-c[:,0])+(c[:,0]-b[:,0])*(p[:,1,None]-c[:,2]))/den
                wb=((c[:,2]-a[:,2])*(p[:,0,None]-c[:,0])+(a[:,0]-c[:,0])*(p[:,1,None]-c[:,2]))/den
                wc=1-wa-wb;inside=(wa>=-1e-5)&(wb>=-1e-5)&(wc>=-1e-5)
                valid=inside.any(axis=1);pick=inside.argmax(axis=1);row=np.arange(len(take))
                values=wa[row,pick]*a[pick,1]+wb[row,pick]*b[pick,1]+wc[row,pick]*c[pick,1]
                if not np.all(valid):
                    self.misses+=int((~valid).sum())
                    values[~valid]=W.height(x[selected[take[~valid]]],z[selected[take[~valid]]])
                result[selected[take]]=values
        return result.reshape(shape)
