"""Author initial independent terrain modules and a seed layout for Godot assembly."""
from pathlib import Path
import sys,math,json,numpy as np,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'blender'))
import world_definition as W
import terrain_topology as T
H=W.surface_height
PREVIEW=True  # Model instances belong to Godot; this only authors a seed.
def bl(v):return (v[0],-v[2],v[1])
def linear(a):return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)

library=bpy.data.collections['Asset Library'];library.hide_render=True;library.hide_viewport=True
terrain_col=bpy.data.collections.new('Continuous Terrain');bpy.context.scene.collection.children.link(terrain_col)
detail_col=bpy.data.collections.new('World Models');bpy.context.scene.collection.children.link(detail_col)
cloud_col=bpy.data.collections.new('Cloud Volumes');bpy.context.scene.collection.children.link(cloud_col)
mat=bpy.data.materials['Environment pigment - vertex colors']
chunks={};props=[];terrain_objects=[];sampler=T.SurfaceSampler();triangle_count=0

def colored_mesh(name,vertices,faces,colors,collection,position=(0,0,0)):
    m=bpy.data.meshes.new(name+'Geometry');m.from_pydata([bl(p) for p in vertices],[],faces);m.update()
    attr=m.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER')
    values=np.array(colors,float)
    if values.ndim==1:values=np.tile(values,(len(faces),1))
    values=linear(values[:,:3]);rgba=np.c_[values,np.ones(len(values))]
    # Terrain faces and road quads may have different loop counts.
    rows=np.concatenate([np.tile(c,(len(p.loop_indices),1)) for c,p in zip(rgba,m.polygons)])
    attr.data.foreach_set('color',rows.astype(np.float32).ravel())
    m.color_attributes.active_color_index=0;m.color_attributes.render_color_index=0;m.materials.append(mat)
    o=bpy.data.objects.new(name,m);collection.objects.link(o);o.location=bl(position)
    return o

def instance(kind,x,y,z,scale=1,yaw=0,solid=True,collection=detail_col):
    entry=[kind,round(float(x),3),round(float(y),3),round(float(z),3),round(float(scale),3),round(float(yaw),4),solid]
    props.append(entry)
    if PREVIEW:return None
    prototype=bpy.data.objects[kind]
    o=bpy.data.objects.new(kind+' instance',prototype.data);collection.objects.link(o)
    o.location=bl((x,y,z));o.scale=(scale,scale,scale);o.rotation_euler.z=yaw
    return o

# Native constrained triangles follow complete world-space banks and ridges.
for cz in range(W.BOUNDS[2],W.BOUNDS[3]+1):
    for cx in range(W.BOUNDS[0],W.BOUNDS[1]+1):
        ox,oz=cx*W.CHUNK,cz*W.CHUNK
        vertices,faces=T.chunk_mesh(cx,cz);heights=vertices[:,1]
        sampler.add(cx,cz,vertices,faces);triangle_count+=len(faces)
        tris=vertices[faces];centers=tris.mean(axis=1)+[ox,0,oz]
        normals=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-8)
        variation=np.mod(np.sin(centers[:,0]*12.9898+centers[:,2]*78.233)*43758.5453,1)
        colors=[W.terrain_color(c,n,v) for c,n,v in zip(centers,normals,variation)]
        name=f'Ground_{cx}_{cz}'
        o=colored_mesh(name,vertices,faces,colors,terrain_col,(ox,0,oz));terrain_objects.append(o)
        o['world_chunk']=[cx,cz];o['spacing_metres']=W.STEP
        chunks[name]=dict(x=cx,z=cz,min_y=float(heights.min()),max_y=float(heights.max()),triangles=len(faces),topology='native constrained Delaunay')
    print('TERRAIN ROW',cz,'/',W.BOUNDS[3],flush=True)
H=sampler.height

# Deterministic forests and rocks, using full 3D Blender prototypes.
for name,chunk in chunks.items():
    cx,cz=chunk['x'],chunk['z'];rng=np.random.default_rng((cx*73856093 ^ cz*19349663)&0xffffffff)
    count=580
    x=(cx+rng.random(count))*W.CHUNK;z=(cz+rng.random(count))*W.CHUNK
    h=H(x,z);hx=H(x+6,z);hz=H(x,z+6)
    slope=np.maximum(np.abs(hx-h),np.abs(hz-h))/6
    cluster=W.noise(x*.22+945,z*.22-217)
    for i in range(count):
        if not 6<h[i]<370 or slope[i]>.7:continue
        if any(math.hypot(x[i]-p['x'],z[i]-p['z'])<110 for p in W.PORTS):continue
        if i<510:
            if cluster[i]<-.06:continue
            kind='pine' if h[i]>120 else ('oak' if rng.random()<.68 else 'poplar')
            scale=rng.uniform(.40,.86)
        else:kind='rock' if i%3 else 'bush';scale=rng.uniform(.6,1.8)
        instance(kind,x[i],h[i],z[i],scale,rng.uniform(0,math.tau))
    if cz%2==0 and cx==W.BOUNDS[1]:print('FOREST ROW',cz,'placements',len(props),flush=True)

# Six complete destinations, with platforms that are actually landable.
landmark={'harbor':'lighthouse','castle':'castle','observatory':'observatory','mill':'mill','lighthouse':'lighthouse','ruins':'ruins'}
for index,port in enumerate(W.PORTS):
    x,z=port['x'],port['z'];y=port['pad_y'];style=port['style']
    instance('dock',x,y,z,.55 if style=='castle' else 1,0)
    kind=landmark[style];bx=x+(42 if style=='harbor' else 0);bz=z-70
    if kind=='castle':bx,bz=W.CASTLE[0],W.CASTLE[2]
    by=float(H(bx,bz));instance(kind,bx,by,bz,.66 if kind=='castle' else 1,0)
    if kind=='mill':instance('mill_rotor',bx,by+9,bz+3.4,1,0,False)
    if style=='mill':
        for dx,dz in [(-60,-35),(70,-80)]:
            hy=float(H(x+dx,z+dz));instance('mill',x+dx,hy,z+dz,.85,0)
            instance('mill_rotor',x+dx,hy+9*.85,z+dz+3.4*.85,.85,0,False)
    rng=np.random.default_rng(800+index)
    for i in range(19 if style in ['harbor','castle','mill'] else 7):
        a=rng.uniform(0,math.tau);r=rng.uniform(106,210)
        px=x+math.cos(a)*r;pz=z+math.sin(a)*r;py=float(H(px,pz))
        if py<6 or abs(float(H(px+8,pz))-py)>5:continue
        instance('cottage',px,py-.2,pz,rng.uniform(.78,1.35),rng.choice([0,math.pi/2,math.pi,math.pi*1.5]))
    instance('crate',x+9,y+.25,z+1)

# Additional villages on actual terrain away from the reference direction.
for k,(x,z) in enumerate([(600,-1900),(2300,-600),(2800,900),(-690,-2600),(-1300,1300),(2250,-4200),(4700,-2000),(-3300,-5000),(3700,3150)]):
    rng=np.random.default_rng(1900+k)
    for i in range(12):
        px=x+rng.uniform(-55,55);pz=z+rng.uniform(-55,55);hy=float(H(px,pz))
        if 6<hy<190:instance('cottage',px,hy,pz,rng.uniform(.7,1.3),rng.uniform(0,math.tau))

# Roads and small cultivated plots are meshes draped over the terrain.
road_vertices=[];road_faces=[];road_colors=[]
routes=[[(120,480),(92,180),(55,45),(65,-115),(W.CASTLE[0],W.CASTLE[2])],[(120,480),(560,380),(1050,650),(1320,880)]]
for route in routes:
    for a,b in zip(route,route[1:]):
        a=np.array(a,float);b=np.array(b,float);length=np.linalg.norm(b-a);direction=(b-a)/length;n=np.array([-direction[1],direction[0]])*.9
        for t in np.arange(0,length,8):
            aa=a+direction*t;bb=a+direction*min(length,t+8)
            uv=[aa-n,aa+n,bb+n,bb-n]
            hh=[float(H(*p))+.22 for p in uv]
            if min(hh)<2:continue
            start=len(road_vertices);road_vertices.extend([(p[0],h,p[1]) for p,h in zip(uv,hh)])
            road_faces.append(tuple(range(start,start+4)));road_colors.append((.79,.76,.59))
if road_faces:
    o=colored_mesh('Roads',road_vertices,road_faces,road_colors,terrain_col);terrain_objects.append(o)
for i in range(12):
    x=1150+(i%4)*48;z=1050+(i//4)*36
    v=[(xx,float(H(xx,zz))+.25,zz) for xx,zz in [(x,z),(x+40,z),(x+40,z+27),(x,z+27)]]
    if min(p[1] for p in v)<4:continue
    o=colored_mesh('Field_'+str(i),v,[(0,3,2,1)],[(.67+(i%3)*.035,.68+(i%3)*.025,.37)],terrain_col);terrain_objects.append(o)

# Solid cloud volumes in all directions, with a few art-directed opening clouds.
for x,y,z,s in W.ART['clouds']:instance('cloud',x,y,z,s,0,False,cloud_col)
rng=np.random.default_rng(77)
for i in range(46):
    x=rng.uniform(-7000,7000);z=rng.uniform(-8500,5500)
    if z<250 and abs(x/(250-z))<1.18:continue
    instance('cloud',x,max(560,float(W.height(x,z))+190)+rng.uniform(0,420),z,rng.uniform(1.7,4.2),rng.uniform(0,math.tau),False,cloud_col)

# Navigation rings are real meshes; their progress is driven by the game.
rings=[]
for i,(x,z,extra) in enumerate([(0,-100,85),(120,-420,85),(420,-1050,150),(830,-2030,140),(1140,-2600,100),(1580,-1650,150),(1530,100,100),(1280,710,100),(-600,-1450,120),(-1040,-1840,100),(-320,1100,100),(-710,1980,90)]):
    y=max(float(W.height(x,z)),0)+extra
    rings.append(dict(position=[x,y,z],yaw=0))
    instance('sky_ring',x,y,z,1,0,False)

# Blender exports modules, never a runtime world scene. Godot owns placement.
from export_world_modules import export_modules
export_modules(terrain_objects)
layout=dict(revision=3,terrain_triangles=triangle_count,chunk_size=W.CHUNK,cells=W.CELLS,bounds=W.BOUNDS,peaks=W.PEAKS,river=W.RIVER,rivers=W.RIVERS,coast=W.COAST,ports=W.PORTS,chunks=chunks,props=props,rings=rings)
(ROOT/'assets/world_layout.json').write_text(json.dumps(layout,separators=(',',':')))

print('TERRAIN MODULE SEED COMPLETE',len(chunks),'terrain modules',len(props),'seed placements',triangle_count,'triangles',flush=True)
