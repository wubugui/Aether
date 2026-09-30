"""World-space geography shared by Blender authoring and the Godot port.

There are no image coordinates, photo samples, projection UVs or billboards.
Distances are metres. Godot coordinates are X east, Y up, Z south.
"""
import numpy as np
import json
from pathlib import Path

CHUNK=768
CELLS=32
STEP=CHUNK/CELLS
BOUNDS=(-6,6,-10,5)
ART=json.loads((Path(__file__).with_name('art_layout.json')).read_text())
PEAKS=ART['peaks']
RIVERS=ART['rivers']
RIVER=RIVERS[0]['points']
COAST=ART['coast']
CASTLE=ART['castle_ground_position']
_water_file=Path(__file__).resolve().parents[1]/'assets/water_geography.json'
WATER_REGIONS=json.loads(_water_file.read_text()) if _water_file.exists() else []
_sculpt_file=Path(__file__).resolve().parents[1]/'assets/terrain_sculpt.json'
SCULPTS=json.loads(_sculpt_file.read_text()) if _sculpt_file.exists() else []
HAS_MOUNTAIN_KIT=(Path(__file__).resolve().parents[1]/'assets/mountain_kit.json').exists()
PORTS=[
    dict(id='hearth',name='Hearthwind Port',x=120,z=480,style='harbor'),
    dict(id='crown',name='Crownreach Citadel',x=CASTLE[0]+24,z=CASTLE[2]+16,style='castle'),
    dict(id='summit',name='Frostpeak Observatory',x=1080,z=-2800,style='observatory'),
    dict(id='mill',name='Amberfield Mills',x=1320,z=880,style='mill'),
    dict(id='lantern',name='Lantern Coast',x=-1120,z=-1910,style='lighthouse'),
    dict(id='ruins',name='Old Skygate',x=-710,z=2090,style='ruins')]

def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1)
    return t*t*(3-2*t)

def noise(x,z):
    return np.sin(x*.007+z*.004)*np.cos(z*.009-x*.003)*.50+np.sin(x*.021+z*.017)*.25+np.cos(x*.053-z*.041)*.15+np.sin(z*.13+x*.11)*.07

def sculpt_height(x,z,h):
    for sculpt in SCULPTS:
        x0,z0,x1,z1=sculpt['bounds']
        margin=np.minimum.reduce([x-x0,x1-x,z-z0,z1-z])
        blend=smooth(0,60 if 'foothills' in sculpt['name'] else 140,margin)
        if not np.any(blend>0):continue
        points=np.asarray(sculpt['points'])
        for indices in sculpt['triangles']:
            a,b,c=points[indices]
            den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
            wa=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den
            wb=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den
            wc=1-wa-wb
            target=wa*a[1]+wb*b[1]+wc*c[1]+noise(x*1.3,z*1.3)*.85
            h=np.where((blend>0)&(wa>=-1e-7)&(wb>=-1e-7)&(wc>=-1e-7),h*(1-blend)+target*blend,h)
    return h

def raw_height(x,z):
    x,z=np.broadcast_arrays(np.asarray(x,dtype=float),np.asarray(z,dtype=float))
    n=noise(x,z)
    h=15+n*5+np.sin(x*.0031-z*.0023)*5+np.sin(x*.0009+z*.0015)*7
    h+=np.maximum(0,noise(x*.43+871,z*.43-319))**2*92
    for index,(px,pz,top,r,flat,ridges) in enumerate(PEAKS):
        # Foreground cliffs are separate complete Blender assets assembled in
        # Godot. The ground beneath them remains continuous meadow terrain.
        if 16<=index<=21:top=15+(top-15)*.42
        if index<10 and HAS_MOUNTAIN_KIT:top=15+(top-15)*.45
        dx=(x-px)/r;dz=(z-pz)/r
        dist=np.sqrt(dx*dx+dz*dz);angle=np.arctan2(dz,dx)
        profile=np.clip((1-dist*(1+np.sin(angle*5+px)*ridges+np.sin(angle*9)*ridges*.4))/(1-flat),0,1)**1.28
        mass=15+(top-15)*profile
        mass+=(np.sin(x*.07+z*.037)*2+np.sin(x*.13-z*.09))*profile*(1-profile)*min(top/100,2)
        h=np.maximum(h,mass)
    h=sculpt_height(x,z,h)
    # More ranges continue outside the authored heartland in every direction.
    far=smooth(4800,6600,np.maximum(np.abs(x),np.abs(z+1500)))
    remote=np.maximum(0,np.sin(x*.00063+np.sin(z*.00039)*1.7)*np.cos(z*.00051))**3*510
    h=np.maximum(h,remote*far)
    coast=np.interp(z,[p[0] for p in COAST],[p[1] for p in COAST])
    survey_bounds=ART.get('coast_survey_bounds',[-1e9,-1e9])
    waves=1-smooth(survey_bounds[0]-40,survey_bounds[0],z)*(1-smooth(survey_bounds[1],survey_bounds[1]+40,z))
    coast+=(np.sin(z*.09)*2+np.sin(z*.17)*1.5)*waves
    # Use distance perpendicular to the actual shore. X-distance alone makes
    # tight coves rise as razor teeth when their coast runs almost east-west.
    distance=np.abs(x-coast)
    for a,b in zip(COAST,COAST[1:]):
        az,ax=a;bz,bx=b
        if not np.any((x>=min(ax,bx)-151)&(x<=max(ax,bx)+151)&(z>=min(az,bz)-151)&(z<=max(az,bz)+151)):continue
        dx=bx-ax;dz=bz-az;t=np.clip(((x-ax)*dx+(z-az)*dz)/max(dx*dx+dz*dz,1e-9),0,1)
        distance=np.minimum(distance,np.hypot(x-ax-t*dx,z-az-t*dz))
    restore=smooth(22,60,distance)
    # The beach may blend back into a small hill, but must not release a
    # several-hundred-metre peak after a fixed 60 m transition.
    inland=np.minimum(h,distance*.52)
    land=np.minimum(h,distance*.30)*(1-restore)+inland*restore
    h=np.where(x<coast,np.minimum(h,-distance*.72),land)
    # Offshore archipelagos, not a flat infinite ocean at every western point.
    islands=np.maximum(0,1-np.sqrt(((x+2850)/600)**2+((z+120)/470)**2))*155
    islands=np.maximum(islands,np.maximum(0,1-np.sqrt(((x+1950)/430)**2+((z-1270)/350)**2))*115)
    h=np.maximum(h,islands-8)
    # The small visible offshore island is an actual landform above water.
    # A peak below the mainland's 15 m baseline cannot be made by max() before
    # coast clipping; author this independent island after the sea bed.
    px,pz,top,*_=PEAKS[22]
    dx=(x-px)/37;dz=(z-pz)/29
    d=np.sqrt(dx*dx+dz*dz);angle=np.arctan2(dz,dx)
    islet=-8+(top+8)*np.clip((1-d*(1+.10*np.sin(angle*5)))/.70,0,1)
    h=np.maximum(h,islet)
    for channel_index,channel in enumerate(RIVERS):
        if channel_index==0 and WATER_REGIONS:continue
        bank=np.full_like(h,1e9);inside=np.zeros(h.shape,dtype=bool)
        polygon=channel['banks'][0]+channel['banks'][1][::-1]
        for a,b in zip(polygon,polygon[1:]+polygon[:1]):
            dx=b[0]-a[0];dz=b[1]-a[1]
            t=np.clip(((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz),0,1)
            distance=np.sqrt((x-a[0]-t*dx)**2+(z-a[1]-t*dz)**2)
            bank=np.minimum(bank,distance)
            if abs(dz)>1e-9:inside^=((a[1]>z)!=(b[1]>z))&(x<dx*(z-a[1])/dz+a[0])
        bank=np.where(inside,-bank,bank)
        # A steep coastal massif may rise immediately behind its narrow beach;
        # do not cap an entire plateau with the lowland river-bank slope.
        h=np.where(bank<0,np.minimum(h,bank*.72),h*smooth(0,14,bank))
    for region in WATER_REGIONS:
        bounds=np.asarray(region['outer']);low=bounds.min(axis=0)-151;high=bounds.max(axis=0)+151
        if np.all((x<low[0])|(x>high[0])|(z<low[1])|(z>high[1])):continue
        distance=np.full_like(h,1e9);inside_water=np.zeros(h.shape,dtype=bool)
        for ring_index,polygon in enumerate([region['outer']]+region['holes']):
            inside=np.zeros(h.shape,dtype=bool)
            for a,b in zip(polygon,polygon[1:]+polygon[:1]):
                dx=b[0]-a[0];dz=b[1]-a[1];length=max(dx*dx+dz*dz,1e-10)
                t=np.clip(((x-a[0])*dx+(z-a[1])*dz)/length,0,1)
                distance=np.minimum(distance,np.hypot(x-a[0]-t*dx,z-a[1]-t*dz))
                if abs(dz)>1e-9:inside^=((a[1]>z)!=(b[1]>z))&(x<dx*(z-a[1])/dz+a[0])
            if ring_index==0:inside_water=inside
            else:inside_water&=~inside
        restore=smooth(100,150,distance)
        bank=np.minimum(h,distance*.38)*(1-restore)+h*restore
        h=np.where(inside_water,np.minimum(h,-distance*.72),bank)
    return np.maximum(h,-95)

for port in PORTS:
    port['ground']=19 if port['style']=='castle' else max(9,float(raw_height(port['x'],port['z'])))
    port['pad_y']=port['ground']+(.6 if port['style']=='castle' else 19)
    port['inner_radius']=22 if port['style']=='castle' else 46
    port['outer_radius']=36 if port['style']=='castle' else 100

def height(x,z):
    h=raw_height(x,z)
    for port in PORTS:
        dist=np.sqrt((np.asarray(x)-port['x'])**2+(np.asarray(z)-port['z'])**2)
        blend=1-smooth(port['inner_radius'],port['outer_radius'],dist)
        h=h*(1-blend)+port['ground']*blend
    return h

def vertex_xz(ix,iz):
    """Shared, irregular vertices; neighboring chunks use identical positions."""
    jx=np.mod(np.sin(ix*127.1+iz*311.7)*43758.5453,1)*2-1
    jz=np.mod(np.sin(ix*269.5+iz*183.3)*43758.5453,1)*2-1
    boundary=(np.mod(ix,CELLS)==0)|(np.mod(iz,CELLS)==0)
    jx=np.where(boundary,0,jx);jz=np.where(boundary,0,jz)
    return np.asarray(ix)*STEP+jx*7.5,np.asarray(iz)*STEP+jz*7.5

def surface_height(x,z):
    """Barycentric height on the actual irregular triangular ground mesh."""
    x,z=np.broadcast_arrays(np.asarray(x,dtype=float),np.asarray(z,dtype=float))
    ix=np.floor(x/STEP);iz=np.floor(z/STEP)
    found=np.zeros(x.shape,dtype=bool)
    selected=[np.zeros(x.shape) for _ in range(9)]
    for dz in (0,-1,1):
        for dx in (0,-1,1):
            gx,gz=ix+dx,iz+dz
            corners=[vertex_xz(gx,gz),vertex_xz(gx+1,gz),vertex_xz(gx,gz+1),vertex_xz(gx+1,gz+1)]
            even=np.mod(gx+gz,2)==0
            # Both diagonals use the same winding as the Blender export.
            for first,second in [((0,2,3),(0,2,1)),((0,3,1),(1,2,3))]:
                a,b,c=[tuple(np.where(even,corners[i][axis],corners[j][axis]) for axis in (0,1)) for i,j in zip(first,second)]
                den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
                wa=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(z-c[1]))/den
                wb=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(z-c[1]))/den
                wc=1-wa-wb
                inside=(wa>=-1e-7)&(wb>=-1e-7)&(wc>=-1e-7)&~found
                for k,value in enumerate((*a,*b,*c,wa,wb,wc)):
                    selected[k]=np.where(inside,value,selected[k])
                found|=inside
        if np.all(found):break
    if not np.all(found):raise ValueError('Irregular terrain contains an uncovered point')
    ax,az,bx,bz,cx,cz,wa,wb,wc=selected
    return height(ax,az)*wa+height(bx,bz)*wb+height(cx,cz)*wc

GRASS=['b1af83','bab789','c2bc8e','c9c18f']
def terrain_color(center,normal,variation):
    import math
    h=center[1]
    patch=np.clip(.5+float(noise(center[0]*.14,center[2]*.14))*.52+(variation-.5)*.08,0,.999)
    color=GRASS[int(patch*len(GRASS))]
    if h<3.2:color='c4c3ad'
    elif h<7:color='c0c28d'
    rock=normal[1]<.78 and h>35
    if rock:color='aaa99e'
    alpine=(h>120 and center[2]<-1500) or (h>52 and 300<center[0]<1900 and -3500<center[2]<-980)
    if alpine:color='91a3bb'
    snowline=210+38*math.sin(center[0]*.009)+28*math.sin(center[2]*.014)
    snow=alpine and h>snowline and normal[1]>.40
    if snow:color='eeefec'
    rgb=np.array([int(color[i:i+2],16)/255 for i in (0,2,4)])
    sunlight=max(0,float(np.dot(normal,[-.48,.82,.30])))
    if alpine:
        shade=np.array([.67,.74,.85])*(1-sunlight)+np.array([1.02,1.01,1])*sunlight
        rgb*=shade
    elif rock:rgb*=.61+.49*sunlight
    else:rgb*=.80+.24*sunlight
    # A separate upland biome, attached to its real metre-space landscape.
    # Its broad grass faces are darker than the warm lowland fields.
    biome=smooth(-150,-50,center[0])*(1-smooth(260,350,center[0]))*smooth(-220,-100,center[2])*(1-smooth(140,240,center[2]))*smooth(10,25,h)
    if biome>0 and not rock:
        upland=['899871','9eaa78','91a177','a6b080'][int(patch*4)]
        rgb=rgb*(1-biome)+np.array([int(upland[i:i+2],16)/255 for i in (0,2,4)])*(.50+.62*sunlight)*biome
    return np.clip(rgb*(.99+variation*.02),0,1)
