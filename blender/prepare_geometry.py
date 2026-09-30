"""Reference measurements and control meshes for Blender authoring.

Produces vertex positions and corner palette colors, never a world texture or
billboard. The Blender script constructs, welds, groups and exports the meshes.
"""
from pathlib import Path
import sys, json, math
import cv2
import numpy as np
from scipy.spatial import Delaunay
from scipy.ndimage import gaussian_filter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_assets as lib
from build_assets import Mesh, rgb

rng=np.random.default_rng(104)
W,H=1672,941
F=H/(2*math.tan(math.radians(25)))
CAM=np.array([0.,145.,250.])
PITCH=math.radians(-3.5)
ROT=np.array([[1,0,0],[0,math.cos(PITCH),-math.sin(PITCH)],[0,math.sin(PITCH),math.cos(PITCH)]])
source=cv2.imread(str(ROOT/'reference/source.jpg'))[:,:,::-1].astype(float)/255
occluded=cv2.imread(str(ROOT/'reference/occluded_color_reference.png'))[:,:,::-1].astype(float)/255

def sample(x,y,r=2):
    x=int(np.clip(x,0,W-1));y=int(np.clip(y,0,H-1))
    # Occluded colors are used only as color measurements, not runtime imagery.
    blocked=(650<x<905 and 350<y<610) or (x<344 and y<240) or (x>1450 and y<230) or (x<215 and y>680) or (x>1460 and y>726)
    a=occluded if blocked else source
    xx=int(x*a.shape[1]/W); yy=int(y*a.shape[0]/H)
    return np.median(a[max(0,yy-r):yy+r+1,max(0,xx-r):xx+r+1].reshape(-1,3),axis=0)

# Image analysis estimates shoreline positions; no edited bitmap is exported.
analysis=cv2.resize(occluded,(W,H))
rr,gg,bb=analysis.transpose(2,0,1)
yy,xx=np.mgrid[:H,:W]
water=((bb>gg-5/255)&(gg>rr+15/255)&(bb>rr+20/255)&(yy>507)).astype(np.uint8)
water=cv2.morphologyEx(water,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
inland=cv2.distanceTransform(1-water,cv2.DIST_L2,5)

RIDGE=np.array([[-260,438],[0,434],[140,430],[227,441],[277,444],[307,429],[329,439],[410,441],[500,444],[600,442],[705,444],[812,448],[873,443],[915,427],[955,410],[981,401],[1004,389],[1031,391],[1060,375],[1088,391],[1110,367],[1128,337],[1154,319],[1171,331],[1185,353],[1200,344],[1214,319],[1235,308],[1254,327],[1275,350],[1297,356],[1318,379],[1337,386],[1356,380],[1383,410],[1405,399],[1428,430],[1459,413],[1480,428],[1507,436],[1532,449],[1572,460],[1672,470],[1910,473]],float)
FOREGROUND=np.array([[928,1020],[951,891],[1009,866],[1031,811],[1071,780],[1091,724],[1179,756],[1209,705],[1252,688],[1299,667],[1388,659],[1420,636],[1463,629],[1490,660],[1505,693],[1550,680],[1599,699],[1639,694],[1710,723],[1900,820],[1900,1070]],np.float32)
MESA=np.array([[55,626],[78,589],[99,568],[128,540],[157,534],[187,536],[204,556],[211,580],[228,615],[199,639],[91,641]],np.float32)
MINI=np.array([[413,735],[443,698],[475,687],[493,661],[516,646],[538,652],[554,679],[592,687],[609,705],[589,739],[525,759]],np.float32)

def ray(x,y):
    return np.array([(x-W/2)/F,(H/2-y)/F,-1.])@ROT.T

def inside(poly,x,y):return cv2.pointPolygonTest(poly,(float(x),float(y)),False)>=0

def world_point(x,y,coast=False):
    ix=int(np.clip(x,0,W-1));iy=int(np.clip(y,0,H-1));v=ray(x,y)
    h=min(15.,float(inland[iy,ix])*.27)+math.sin(x*.027+y*.019)*1.2
    h=max(.1,h)
    if water[iy,ix] or coast:h=.08 if coast else -.15
    if v[1]>=-.004:
        d=9000.
    else:d=(h-CAM[1])/v[1]
    if 850<x<1750 and y<505:
        ridge=np.interp(x,RIDGE[:,0],RIDGE[:,1])
        if y>=ridge:
            factor=np.clip((505-y)/80,0,1)
            md=2350.+(x-1200)*.27
            if y>425:md=2350-(y-425)*10.7+(x-1200)*.12
            d=d*(1-factor)+md*factor
    if inside(FOREGROUND,x,y):
        d=430-(y-630)*.78+(x-1430)*.10
    if inside(MESA,x,y): d=660+(600-y)*.8
    if inside(MINI,x,y): d=412+(700-y)*.16
    result=CAM+v*max(d,95.)
    outside=max(-x,x-W,y-H,0.)
    if outside>0:
        # Extend the modeled coast outside the photographed frustum, then roll
        # it below the continuous ocean instead of leaving a rectangular edge.
        width=145.+30.*math.sin(y*.027)+22.*math.sin(x*.041+y*.013)
        t=np.clip(outside/width,0,1);t=t*t*(3-2*t)
        result[1]=result[1]*(1-t)-5*t
    return result

def prepare_ground():
    points=[];coast_points=[]
    for y0,y1,step in [(306,426,14),(426,530,6.5),(530,660,11),(660,800,22),(800,1100,42)]:
        for y in np.arange(y0,y1,step):
            for x in np.arange(-240,W+240,step):
                q=np.array([x,y])+rng.uniform(-step*.28,step*.28,2)
                if q[1]>np.interp(q[0],RIDGE[:,0],RIDGE[:,1])+1:
                    if 860<q[0]<1750 and q[1]<505 and step<14 and rng.random()<.75:continue
                    if inside(FOREGROUND,*q) and rng.random()<.68:continue
                    points.append(q)
    # Mountain silhouettes and internal ridges constrain the triangulation.
    for a,b in zip(RIDGE[:-1],RIDGE[1:]):
        for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/6))):points.append(a*(1-t)+b*t)
    for p in [FOREGROUND,MESA,MINI]:
        for a,b in zip(p,np.roll(p,-1,axis=0)):
            for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/26))):points.append(a*(1-t)+b*t)
    contours,_=cv2.findContours(water,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour)<12:continue
        contour=cv2.approxPolyDP(contour,1.0,True)[:,0,:]
        for a,b in zip(contour,np.roll(contour,-1,axis=0)):
            for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/5))):coast_points.append(a*(1-t)+b*t)
    points=np.array(points+coast_points)
    points=np.unique(np.round(points,3),axis=0)
    mesh2=Delaunay(points)
    vertices=np.array([world_point(*p) for p in points])
    names=['Terrain','Shoreline','Groves','Hamlets','Paths','Clouds','SnowRange','ForegroundCliffs','Water']
    meshes={n:Mesh(n) for n in names}
    for face in mesh2.simplices:
        px=points[face]; center=px.mean(axis=0);x,y=center
        if y<np.interp(x,RIDGE[:,0],RIDGE[:,1])+.05:continue
        edge1=px[1]-px[0];edge2=px[2]-px[0]
        if abs(edge1[0]*edge2[1]-edge1[1]*edge2[0])>6000 and y<500:continue
        ix=int(np.clip(x,0,W-1));iy=int(np.clip(y,0,H-1))
        col=sample(x,y,max(3,min(15,int(np.ptp(px,axis=0).mean()/2.8))))
        if (x<0 or x>W or y>H) and vertices[face,1].max()<-.3 and not water[iy,ix]:continue
        if water[iy,ix] and y>507:
            v=np.array([CAM+ray(*q)*(-CAM[1]/ray(*q)[1]) for q in px])
            meshes['Water'].tri(*v,col,False)
            # No painted land surface under water.
            continue
        name='Terrain'
        if 860<x<1750 and y<505:name='SnowRange'
        elif inside(FOREGROUND,x,y) or inside(MESA,x,y) or inside(MINI,x,y):name='ForegroundCliffs'
        v=vertices[face]
        if np.cross(v[1]-v[0],v[2]-v[0])[1]<0:v=v[[0,2,1]]
        meshes[name].tri(*v,col,False)
    def surface(x,y):
        f=mesh2.find_simplex([x,y])
        if f<0:return world_point(x,y)
        b=mesh2.transform[f,:2]@([x,y]-mesh2.transform[f,2]); weights=np.r_[b,1-b.sum()]
        v=vertices[mesh2.simplices[f]]
        depths=np.linalg.norm(v-CAM,axis=1)
        weights=weights/depths;weights/=sum(weights)
        return (v*weights[:,None]).sum(axis=0)
    return meshes,surface

def prepare_clouds(mesh):
    boxes=[(970,113,1321,219,1700),(638,226,944,314,1900),(0,238,236,342,1900),(238,302,518,370,2100),(582,309,710,337,2500),(1635,290,1672,339,2600),(1319,331,1424,362,3000),(1498,324,1617,358,3400)]
    for x0,y0,x1,y1,depth in boxes:
        region=source[y0:y1,x0:x1]
        r,g,b=region.transpose(2,0,1)
        mask=((r>.72)&(r>b*.89)&(g>.73)).astype(np.uint8)
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        dist=cv2.distanceTransform(mask,cv2.DIST_L2,5)
        for contour in contours:
            if cv2.contourArea(contour)<14:continue
            outline=cv2.approxPolyDP(contour,1.4,True)[:,0,:].astype(float)
            pts=list(outline)
            for py in np.arange(0,y1-y0,17):
                for px in np.arange(0,x1-x0,18):
                    if cv2.pointPolygonTest(contour,(float(px),float(py)),False)>0:pts.append([px+rng.uniform(-2,2),py+rng.uniform(-2,2)])
            pts=np.unique(np.round(pts,3),axis=0)
            if len(pts)<4:continue
            tri=Delaunay(pts)
            front=[];back=[]
            for px,py in pts:
                radius=dist[int(np.clip(py,0,dist.shape[0]-1)),int(np.clip(px,0,dist.shape[1]-1))]
                front.append(CAM+ray(px+x0,py+y0)*(depth-radius*depth*.0011))
                back.append(CAM+ray(px+x0,py+y0)*(depth+max(4,radius)*depth*.0013))
            front=np.array(front);back=np.array(back)
            for f in tri.simplices:
                c=pts[f].mean(axis=0)
                if cv2.pointPolygonTest(contour,tuple(c.astype(float)),False)<0:continue
                col=sample(c[0]+x0,c[1]+y0,2)
                mesh.tri(*front[f],col,False)
                mesh.tri(*back[f[[0,2,1]]],rgb('d9dce2'),False)
            # Actual sidewalls close each cloud volume for alternate viewpoints.
            for a,b in zip(outline,np.roll(outline,-1,axis=0)):
                ia=np.argmin(np.linalg.norm(pts-a,axis=1));ib=np.argmin(np.linalg.norm(pts-b,axis=1))
                mesh.quad(front[ia],front[ib],back[ib],back[ia],rgb('e6e6e7'),False)

def prepare_details(meshes,surface):
    tree=meshes['Groves']; house=meshes['Hamlets'];roads=meshes['Paths']
    lum=analysis.mean(axis=2);local=gaussian_filter(lum,7)
    dark=((lum<local-.04)&(gg>bb*1.04)&(gg>rr*1.025)&(yy>550)&(water==0)).astype(np.uint8)
    count,labels,stats,centroids=cv2.connectedComponentsWithStats(dark)
    positions=[]
    for st,c in zip(stats[1:],centroids[1:]):
        x,y=c;area=st[4]
        if not 5<=area<=120 or st[2]>st[3]*3.2 or st[3]>st[2]*4:continue
        if x>1100 and y>700:continue
        if x<225 and y>680:continue
        if 650<x<905 and 350<y<610:continue
        if rng.random()<.62:continue
        positions.append((x,y,min(10,max(2.8,math.sqrt(area)*.78))))
    positions.extend([(759,864,20),(954,771,19),(972,761,21),(997,763,14),(515,748,18),(490,749,14),(566,715,9),(597,715,12)])
    for sx,sy,pix in positions:
        p=surface(sx,sy);d=np.linalg.norm(p-CAM);h=pix*d/F
        tree.rod(p,p+[0,h*.56,0],h*.055,rgb('696e52'),5)
        tree.ellipsoid(p+[0,h*.62,0],[h*.31,h*.51,h*.29],rgb('7b8b62')*rng.uniform(.91,1.10),5,7,.13)
    def house_at(sx,sy,s=1):
        p=surface(sx,sy);d=np.linalg.norm(p-CAM);a=max(.5,s*d/F*.73)
        house.box(p+[0,a*.65,0],[a*1.6,a*1.3,a*1.25],rgb('c8c3a4'))
        verts=[p+q for q in [(-a,a*1.25,-a*.8),(a,a*1.25,-a*.8),(a,a*2,0),(-a,a*2,0),(-a,a*1.25,a*.8),(a,a*1.25,a*.8)]]
        house.quad(*[verts[i] for i in [0,1,2,3]],rgb('7e877b'))
        house.quad(*[verts[i] for i in [3,2,5,4]],rgb('8c927e'))
        house.box(p+[0,a*.42,a*.633],[a*.29,a*.83,.05],rgb('747762'))
    for cx,cy in [(835,747),(972,699),(1023,582),(1333,627),(617,577),(337,557),(739,620),(899,569),(291,635),(1125,614),(1620,631)]:
        for k in range(rng.integers(4,11)):house_at(cx+rng.normal(0,7),cy+rng.normal(0,3),rng.uniform(2.0,3.8))
    # Stone citadel, scaled and placed from its image landmarks.
    p=surface(914,643);stone=rgb('d7c699')
    for x,z,w,h in [(-25,0,4,18),(24,0,4.5,17),(-22,-22,3.5,15),(22,-22,4,19),(-8,-11,9,16),(5,-9,7,22),(0,-13,3.3,28)]:
        w*=.60;h*=.77
        house.box(p+[x,h*.5,z],[w,h,w],stone)
        house.rod(p+[x,h,z],p+[x,h+3.5,z],w*.68,rgb('b2a57e'),4,0)
    for x in np.linspace(-23,23,12):
        house.box(p+[x,1.4,0],[4.2,2.8,1.1],stone)
        house.box(p+[x,3.4,0],[1.2,.8,1.3],stone)
    for z in np.linspace(-22,0,8):
        for x in [-24,24]:house.box(p+[x,1.6,z],[1.1,3.2,3.5],stone)
    for k in range(18):house_at(914+rng.normal(0,28),639+rng.normal(0,8),rng.uniform(2,3))
    paths=[[(799,975),(803,918),(827,883),(819,862),(843,829),(853,792),(884,762),(892,744),(919,717),(918,696),(899,676),(911,650)],[(847,787),(815,788),(774,774),(741,772),(711,758),(681,767),(646,754),(620,743),(621,721),(595,700)],[(915,717),(949,707),(988,710),(1028,691),(1070,688),(1090,674),(1114,670)],[(849,789),(867,773),(857,757),(835,748)],[(534,700),(564,695),(592,678),(635,668),(661,654),(669,642)],[(321,568),(347,588),(354,617),(339,635)],[(1172,605),(1227,624),(1283,629),(1333,627),(1371,615),(1405,602)]]
    for line in paths:
        for a,b in zip(line,line[1:]):
            a=np.array(a,float);b=np.array(b,float)
            for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/3)))[:-1]:
                u=a+(b-a)*t;v=a+(b-a)*min(1,t+3/max(3,np.linalg.norm(b-a)))
                pu=surface(*u)+[0,.12,0];pv=surface(*v)+[0,.12,0]
                width=max(.25,(u[1]/900)**4*1.5)
                n=np.cross(pv-pu,[0,1,0]);n/=max(np.linalg.norm(n),1e-8);n*=width
                roads.quad(pu-n,pu+n,pv+n,pv-n,rgb('d0c8a0'),False)

def save_control_meshes(meshes):
    data={};meta=[]
    for i,(group,m) in enumerate(meshes):
        if not m.p:continue
        key=f'm{i}';data[key+'_p']=np.asarray(m.p,dtype=np.float32);data[key+'_c']=np.asarray(m.c,dtype=np.float32)
        meta.append(dict(key=key,name=m.name,group=group,triangles=len(m.p)//3))
    data['metadata']=np.array(json.dumps(meta))
    np.savez_compressed(ROOT/'blender/control_meshes.npz',**data)
    (ROOT/'blender/model_manifest.json').write_text(json.dumps(meta,indent=2))
    print('Prepared',len(meta),'meshes;',sum(m['triangles'] for m in meta),'triangles',flush=True)

if __name__=='__main__':
    meshes,surface=prepare_ground()
    print('Terrain control mesh ready',flush=True)
    prepare_clouds(meshes['Clouds']);prepare_details(meshes,surface)
    all_meshes=[('Landscape',m) for m in meshes.values()]
    def collect(mesh_list,filename):
        group='Propeller' if filename=='propeller.glb' else 'Airship'
        all_meshes.extend((group,m) for m in mesh_list)
    lib.save_glb=collect
    lib.ship()
    save_control_meshes(all_meshes)
