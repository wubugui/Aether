"""Actual1216 camera: conservative OBBs plus actual control-triangle ID samples.

This is a low-memory static projection diagnostic, not a Blender or world view.
Projected boxes do not measure visible silhouettes. Real triangle z-buffer
samples establish only pre-union control visibility, not visual acceptance.
"""
import hashlib,itertools,json,math,os
from pathlib import Path
import numpy as np
from geometry58c import all_controls
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
REPORT=ROOT/'cloud-evidence/cloudsea52h-d-ab-front-20261001T102736Z-svczz9fo/images/report.json'
plan=json.loads((P/'control-plan58c.json').read_text());camera=json.loads(REPORT.read_text())['captures'][0]
W,H=836,471 # samplinggrid; output converted to exact reference units byaxis
B=np.array(camera['camera_transform'][:9]).reshape(3,3).T;origin=np.array(camera['camera_transform'][9:]);projection=np.array(camera['camera_projection_columns']).T
# The measured float basis is not silently assumed perfectly orthogonal.
invB=np.linalg.inv(B);near=camera['camera_near']

def cam(v):return (np.asarray(v)-origin)@invB.T

def project_cam(v):
    q=np.c_[v,np.ones(len(v))]@projection.T;n=q[:,:3]/q[:,3:]
    return np.c_[(n[:,0]+1)*W/2,(1-n[:,1])*H/2,-v[:,2]]

def clip_near(t):
    poly=list(t);out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ai=-a[2]>=near;bi=-b[2]>=near
        if ai:out.append(a)
        if ai!=bi:out.append(a+(b-a)*((-near-a[2])/(b[2]-a[2])))
    return [np.array([out[0],out[i],out[i+1]]) for i in range(1,len(out)-1)]

def raster(vertices,faces,owner,zbuf,labels):
    cv=cam(vertices);ownmask=np.zeros((H,W),bool)
    for f in faces:
        for tri in clip_near(cv[np.array(f)]):
            p=project_cam(tri);lo=np.floor(p[:,:2].min(0)).astype(int);hi=np.ceil(p[:,:2].max(0)).astype(int)
            x0=max(0,lo[0]);x1=min(W-1,hi[0]);y0=max(0,lo[1]);y1=min(H-1,hi[1])
            if x1<x0 or y1<y0:continue
            a,b,c=p[:,:2];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-10:continue
            yy,xx=np.mgrid[y0:y1+1,x0:x1+1];xx=xx+.5;yy=yy+.5
            wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
            wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;wc=1-wa-wb
            mask=(wa>=-1e-9)&(wb>=-1e-9)&(wc>=-1e-9)
            with np.errstate(divide='ignore',invalid='ignore'):depth=1/(wa/p[0,2]+wb/p[1,2]+wc/p[2,2])
            ownmask[y0:y1+1,x0:x1+1]|=mask
            zb=zbuf[y0:y1+1,x0:x1+1];lb=labels[y0:y1+1,x0:x1+1];take=mask&(depth<zb);zb[take]=depth[take];lb[take]=owner
    return ownmask

controls=all_controls(plan);zbuf=np.full((H,W),np.inf);labels=np.full((H,W),-1,dtype=np.int16);rows=[]
for i,spec in enumerate(controls):
    row=spec['design'];size=np.array(row['design_extent_xyz_m']);corners=np.array(list(itertools.product([-.5,.5],repeat=3)))*size
    ang=math.radians(row['yaw_degrees']);co,si=math.cos(ang),math.sin(ang);rot=np.array([[co,0,-si],[0,1,0],[si,0,co]])
    corners=corners@rot.T+row['center_godot_world_xyz_m'];cv=cam(corners);pv=project_cam(cv) if (-cv[:,2]).min()>near else None
    ownmask=raster(spec['vertices'],spec['faces'],i,zbuf,labels);surface=cam(spec['vertices'])
    horiz=np.degrees(np.arctan2(surface[:,0],-surface[:,2]));vert=np.degrees(np.arctan2(surface[:,1],-surface[:,2]));ys,xs=np.where(ownmask)
    rows.append(dict(id=spec['id'],role=spec['role'],parent_form=spec['parent_form'],camera_depth_range_m=[float((-surface[:,2]).min()),float((-surface[:,2]).max())],
        conservative_obb_reference_pixel_bounds=None if pv is None else [float(pv[:,0].min()*2),float(pv[:,1].min()*941/H),float(pv[:,0].max()*2),float(pv[:,1].max()*941/H)],
        conservative_obb_is_visible_width=False,actual_control_vertex_horizontal_angles_deg=[float(horiz.min()),float(horiz.max())],actual_control_vertex_vertical_angles_deg=[float(vert.min()),float(vert.max())],
        isolated_actual_triangle_sample_count=int(ownmask.sum()),isolated_sample_reference_bbox=None if not len(xs) else [float(xs.min()*2),float(ys.min()*941/H),float((xs.max()+1)*2),float((ys.max()+1)*941/H)]))
for i,row in enumerate(rows):
    yy,xx=np.where(labels==i);n=len(xx);row.update(nearest_actual_triangle_sample_count=n,visible_fraction_of_isolated_samples=n/row['isolated_actual_triangle_sample_count'] if row['isolated_actual_triangle_sample_count'] else None,
        nearest_sample_reference_bbox=None if not n else [float(xx.min()*2),float(yy.min()*941/H),float((xx.max()+1)*2),float((yy.max()+1)*941/H)],
        visibility_limit='Discrete nearest-surface sample spans may include disconnected patches, not continuous visible silhouette width. Pre-union controls only.')
summary={role:dict(count=sum(r['role']==role for r in rows),with_nearest_triangle_samples=sum(r['role']==role and r['nearest_actual_triangle_sample_count']>0 for r in rows),
    with_25_or_more_samples=sum(r['role']==role and r['nearest_actual_triangle_sample_count']>=25 for r in rows)) for role in sorted({r['role'] for r in rows})}
result=dict(camera_source=str(REPORT.relative_to(ROOT)),camera_source_sha256=hashlib.sha256(REPORT.read_bytes()).hexdigest(),camera={k:v for k,v in camera.items() if k in ['camera_transform','camera_projection_columns','camera_near','camera_far','camera_keep_aspect','camera_fov']},
    exact_reference_resolution=[1672,941],sampling_grid=[W,H],summary=summary,controls=rows,
    method='Actual native-authoring control triangles, near-plane clipped, perspective-correct nearest depth atpixelcentres. Oriented box projection is separately marked conservative.',
    limitations=['This omits external21roots, oldupperribbons,ship and everyworldobject','Actualunion geometry and anyreduction can change visibility','Nearest triangle samples and angle bounds are not continuous silhouette measurement or a rendered visual acceptance'],
    world_loaded=False,blender_started=False,visual_acceptance=False)
(P/'control-projection58c.json').write_text(json.dumps(result,indent=2)+'\n')
(P/'native-control-input58c.json').write_text(json.dumps(dict(plan_sha256=hashlib.sha256((P/'control-plan58c.json').read_bytes()).hexdigest(),controls=controls),indent=2)+'\n')
os.environ.setdefault('MPLCONFIGDIR','/tmp/feiting58c-matplotlib')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
palette=['#f2eee3']+['#496982' if r['role']=='lower_density' else '#bd7433' if r['role']=='primary_crown' else '#e2ae45' if r['role']=='medium_fold' else '#bd584d' for r in rows]
fig,ax=plt.subplots(figsize=(12,7));ax.imshow(labels+1,cmap=ListedColormap(palette),vmin=0,vmax=len(rows),extent=[0,1672,941,0],interpolation='nearest')
for i,r in enumerate(rows):
    yy,xx=np.where(labels==i)
    if len(xx)>12:ax.text(np.median(xx)*2,np.median(yy)*941/H,r['id'],fontsize=7,color='white',ha='center')
ax.set_title('C control triangle visibility diagnostic: actual 1216 camera\nBlue lower / brown primary / gold medium / red small; no world, no lighting, no visual acceptance',fontsize=11);ax.set_xlabel('Reference pixels X');ax.set_ylabel('Reference pixels Y');fig.tight_layout();fig.savefig(P/'control-projection58c.png',dpi=140);plt.close(fig)
print(json.dumps(dict(summary=summary,primary_rows=[r for r in rows if r['role']=='primary_crown'],medium_rows=[{k:r[k] for k in ['id','isolated_actual_triangle_sample_count','nearest_actual_triangle_sample_count','visible_fraction_of_isolated_samples']} for r in rows if r['role']=='medium_fold']),indent=2))
