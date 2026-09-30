from pathlib import Path
R=Path(__file__).resolve().parents[1]
exec(compile((R/'reviews/round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'glb_decoder','exec'))
from PIL import Image
P=R/'captures/lantern_island_study_30d'
run=R/'captures/validation_runs/lantern-island-30d-20260908T183203Z-dfad421d9cb14734824e8942e33ac04c'
png=run/'images/day-c-front.png';side=Path(str(png)+'.json');cam=json.loads(side.read_text())['camera']
e=json.loads((P/'geometry-evidence.json').read_text());actual=glb(P/'island_c.glb');triangles=np.concatenate(list(actual.values()))
source={}
for name,o in e['new'].items():
    v=np.array(o['vertices'])
    for i,f in enumerate(o['polygons']):
        if len(f)==3:source[tri_key(v[f])]=dict(name=name,face=i,vertices=f)
x,y,z=cam['rotation'];cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]);rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
basis=ry@rx@rz
to_blender=lambda p:np.array([p[0],-p[2],p[1]])
origin=to_blender(np.array(cam['position'])-np.array([-3050,0,-2650]))
w,h=Image.open(png).size;scale=math.tan(math.radians(cam['fov'])/2)
a=triangles[:,0];edge1=triangles[:,1]-a;edge2=triangles[:,2]-a
samples=[]
for pixel in [[620,548],[700,550],[770,552],[825,570],[900,548],[970,548]]:
    px,py=pixel;ndcx=2*(px+.5)/w-1;ndcy=1-2*(py+.5)/h
    direction=to_blender(basis@np.array([ndcx*w/h*scale,ndcy*scale,-1.]));direction/=np.linalg.norm(direction)
    pv=np.cross(direction,edge2);det=np.einsum('ij,ij->i',edge1,pv);valid=abs(det)>1e-10
    inv=np.divide(1.,det,out=np.zeros_like(det),where=valid);tv=origin-a;u=np.einsum('ij,ij->i',tv,pv)*inv
    qv=np.cross(tv,edge1);v=(qv@direction)*inv;t=np.einsum('ij,ij->i',edge2,qv)*inv
    good=valid&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>0)
    assert good.any(),pixel
    j=np.where(good,t,np.inf).argmin();point=origin+direction*t[j];normal=np.cross(edge1[j],edge2[j]);normal/=np.linalg.norm(normal)
    samples.append(dict(pixel=pixel,hit_blender_xyz=point.tolist(),triangle_blender_xyz=triangles[j].tolist(),normal_blender_xyz=normal.tolist(),source=source.get(tri_key(triangles[j])),distance_m=float(t[j])))
report=dict(scope='Targeted ray localization of directly viewed unobstructed grey-rock pixels in actual day-c-front. Camera projection uses actual Godot Euler YXZ and vertical FOV, fixed C origin. Intersects actual island GLB only; not a full scene visibility/segmentation test.',png_sha256=sha(png),sidecar_sha256=sha(side),glb_sha256=sha(P/'island_c.glb'),camera=cam,camera_blender_xyz=origin.tolist(),samples=samples,conclusion='Central visible day-c-front wall is on south/east-facing main terrain. West/Southwest/North cutbacks do not alone address this view; choose next edits from these source triangles and actual protected regions, not object names.')
out=R/'reviews/round-30d-visible-slope-localization.json';assert not out.exists();out.write_text(json.dumps(report,indent=2))
print(json.dumps([dict(pixel=s['pixel'],point=s['hit_blender_xyz'],source=s['source']) for s in samples],indent=2))
