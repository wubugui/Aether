#!/usr/bin/env python3
"""Independent 1m XZ highest-static-surface bake of actual saved49 mesh triangles."""
import json, hashlib, time, math
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
META=json.loads((P/'support49-export.json').read_text())
B=np.array(META['domain_world_xz'],dtype=float); X0,Z0,X1,Z1=B
SPACING=1.0; W=int((X1-X0)/SPACING)+1; H=int((Z1-Z0)/SPACING)+1
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(P/META['vertex_binary'])==META['binary_sha256']
raw=np.fromfile(P/META['vertex_binary'],dtype='<f4').reshape(-1,3,3).astype(np.float64)
source_ids=np.empty(len(raw),np.int32)
for n,m in enumerate(META['included_meshes']):source_ids[m['byte_offset']//36:(m['byte_offset']+m['byte_length'])//36]=n
lo=raw[:,:,[0,2]].min(axis=1);hi=raw[:,:,[0,2]].max(axis=1)
mask=(hi[:,0]>=X0)&(lo[:,0]<=X1)&(hi[:,1]>=Z0)&(lo[:,1]<=Z1)
tri=raw[mask]; mids=source_ids[mask]; lo=lo[mask]; hi=hi[mask]
a,b,c=tri[:,0],tri[:,1],tri[:,2]
den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2])
vertical=np.abs(den)<1e-12
tri=tri[~vertical];mids=mids[~vertical];lo=lo[~vertical];hi=hi[~vertical];den=den[~vertical]
a,b,c=tri[:,0],tri[:,1],tri[:,2]
height=np.full((H,W),-np.inf,np.float64);owner=np.full((H,W),-1,np.int32)
start=time.time()
for k,t in enumerate(tri):
    ix0=max(0,int(math.ceil(lo[k,0]-X0-1e-8)));ix1=min(W-1,int(math.floor(hi[k,0]-X0+1e-8)))
    iz0=max(0,int(math.ceil(lo[k,1]-Z0-1e-8)));iz1=min(H-1,int(math.floor(hi[k,1]-Z0+1e-8)))
    if ix0>ix1 or iz0>iz1:continue
    xx=np.arange(ix0,ix1+1,dtype=float)[None,:]+X0
    zz=np.arange(iz0,iz1+1,dtype=float)[:,None]+Z0
    A,BB,C=t
    wa=((BB[2]-C[2])*(xx-C[0])+(C[0]-BB[0])*(zz-C[2]))/den[k]
    wb=((C[2]-A[2])*(xx-C[0])+(A[0]-C[0])*(zz-C[2]))/den[k]
    wc=1-wa-wb
    yy=A[1]*wa+BB[1]*wb+C[1]*wc
    sub=height[iz0:iz1+1,ix0:ix1+1]
    take=(wa>=-1e-8)&(wb>=-1e-8)&(wc>=-1e-8)&(yy>sub)
    sub[take]=yy[take];owner[iz0:iz1+1,ix0:ix1+1][take]=mids[k]
    if k%5000==0:print('raster',k,len(tri),round(time.time()-start,2),flush=True)
missing=~np.isfinite(height)
if missing.any():raise RuntimeError(f'Coverage holes: {missing.sum()}; no fabricated fill allowed')
fheight=height.astype('<f4');depth=np.maximum(0.0,-fheight).astype('<f4')
fheight.tofile(P/'height49-1m-rf.f32');depth.tofile(P/'depth49-1m-rf.f32');owner.astype('<i4').tofile(P/'highest-support-owner-i32.bin')
# Independently indexed XZ BVH: point ray queries vs rasterizer output.
centers=(lo+hi)*.5
nodes=[]
def build(ids):
    ni=len(nodes); nodes.append(None)
    bb=np.r_[lo[ids].min(axis=0),hi[ids].max(axis=0)]
    if len(ids)<=24:nodes[ni]=(bb,ids,None,None)
    else:
        axis=int(np.argmax(bb[2:]-bb[:2]));order=ids[np.argsort(centers[ids,axis],kind='stable')];m=len(order)//2
        l=build(order[:m]);r=build(order[m:]);nodes[ni]=(bb,None,l,r)
    return ni
build(np.arange(len(tri)))
def top(x,z, return_owner=False):
    best=-np.inf; bestid=-1; todo=[0]
    while todo:
        bb,ids,l,r=nodes[todo.pop()]
        if x<bb[0]-1e-7 or z<bb[1]-1e-7 or x>bb[2]+1e-7 or z>bb[3]+1e-7:continue
        if ids is None:todo.extend((l,r));continue
        aa,bbv,cc=a[ids],b[ids],c[ids]
        wa=((bbv[:,2]-cc[:,2])*(x-cc[:,0])+(cc[:,0]-bbv[:,0])*(z-cc[:,2]))/den[ids]
        wb=((cc[:,2]-aa[:,2])*(x-cc[:,0])+(aa[:,0]-cc[:,0])*(z-cc[:,2]))/den[ids]
        wc=1-wa-wb;inside=(wa>=-1e-8)&(wb>=-1e-8)&(wc>=-1e-8)
        ys=aa[:,1]*wa+bbv[:,1]*wb+cc[:,1]*wc;ys[~inside]=-np.inf
        j=int(np.argmax(ys))
        if ys[j]>best:best=float(ys[j]);bestid=int(mids[ids[j]])
    return (best,bestid) if return_owner else best

def sample(x,z, data=fheight):
    gx=np.clip(x-X0,0,W-1);gz=np.clip(z-Z0,0,H-1)
    ix=min(W-2,int(gx));iz=min(H-2,int(gz));fx=gx-ix;fz=gz-iz
    return float(data[iz,ix]*(1-fx)*(1-fz)+data[iz,ix+1]*fx*(1-fz)+data[iz+1,ix]*(1-fx)*fz+data[iz+1,ix+1]*fx*fz)
def summary(values):
    v=np.asarray(values,float)
    return {'count':len(v),'max_m':float(v.max()) if len(v) else None,'mean_m':float(v.mean()) if len(v) else None,'p95_m':float(np.percentile(v,95)) if len(v) else None,'p99_m':float(np.percentile(v,99)) if len(v) else None}
rng=np.random.default_rng(490050)
grid_samples=[]
for ix,iz in zip(rng.integers(0,W,2500),rng.integers(0,H,2500)):
    exact=top(X0+int(ix),Z0+int(iz));error=abs(exact-float(fheight[iz,ix]));grid_samples.append(error)
continuous=[];water=[];points=[]
for x,z in zip(rng.uniform(X0,X1,4000),rng.uniform(Z0,Z1,4000)):
    exact=top(x,z); approx=sample(x,z);error=abs(exact-approx);continuous.append(error)
    if exact<=0:water.append(abs(max(0,-exact)-max(0,-approx)))
    if error>1:points.append({'x':x,'z':z,'actual_highest_y':exact,'baked_linear_height_y':approx,'error_m':error})
# Actual shoreline zero intersections, filtered through highest-surface BVH.
shore=[]
for k,t in enumerate(tri):
    if t[:,1].min()>0 or t[:,1].max()<0:continue
    crossings=[]
    for j in range(3):
        aa=t[j];bb=t[(j+1)%3]
        if aa[1]==0:crossings.append(aa.copy())
        if aa[1]*bb[1]<0:crossings.append(aa+(bb-aa)*(-aa[1]/(bb[1]-aa[1])))
    if len(crossings)<2:continue
    u,v=crossings[:2];tangent=(v-u)[[0,2]]
    length=np.linalg.norm(tangent)
    if length<1e-6:continue
    normal=np.array([-tangent[1],tangent[0]])/length
    for fraction in [.2,.5,.8]:
        p=u*(1-fraction)+v*fraction;x,z=p[[0,2]]
        if x<X0+.1 or x>X1-.1 or z<Z0+.1 or z>Z1-.1:continue
        exact,highest_owner=top(x,z,True)
        if abs(exact)>.005:continue # hidden/coincident lower crossing is not the actual shore
        approx=sample(x,z)
        # Locate nearest signed-height texture zero across local actual shoreline normal.
        shifts=np.linspace(-2,2,161);vals=[sample(x+normal[0]*s,z+normal[1]*s) for s in shifts]
        zeros=[]
        for j in range(len(shifts)-1):
            if vals[j]==0:zeros.append(float(shifts[j]))
            elif vals[j]*vals[j+1]<0:zeros.append(float(shifts[j]-vals[j]*(shifts[j+1]-shifts[j])/(vals[j+1]-vals[j])))
        shore.append({'world_xz':[float(x),float(z)],'source_mesh':META['included_meshes'][int(mids[k])]['path'],'actual_top_y':exact,'baked_signed_height_y':approx,'baked_vertical_depth_m':max(0,-approx),'nearest_texture_zero_offset_m':min(map(abs,zeros)) if zeros else None})
shore_errors=[abs(s['baked_signed_height_y']-s['actual_top_y']) for s in shore]
shore_offsets=[s['nearest_texture_zero_offset_m'] for s in shore if s['nearest_texture_zero_offset_m'] is not None]
edges={
 'west':fheight[:,0],'east':fheight[:,-1],'north_z_min':fheight[0,:],'south_z_max':fheight[-1,:]
}
edge_stats={k:{'min_height_y':float(v.min()),'max_height_y':float(v.max()),'water_samples':int((v<0).sum()),'total_samples':len(v)} for k,v in edges.items()}
report={
 'purpose':META['purpose'],'source_scene':META['source'],'source_scene_sha256':META['source_sha256'],
 'source_geometry_manifest':'support49-export.json','source_geometry_manifest_sha256':sha(P/'support49-export.json'),
 'raw_geometry_sha256':META['binary_sha256'],'source_mesh_hashes':[{k:m[k] for k in ['path','local_faces_raw_sha256','world_faces_raw_sha256']} for m in META['included_meshes']],
 'world_bounds_xmin_zmin_xmax_zmax':B.tolist(),'sea_level_y':0,'sample_spacing_m':1.0,'width':W,'height':H,
 'pixel_definition':'Pixel(i,j) stores highest actual saved static-support Y at world(x=768+i,z=-2304+j); x positive right, z positive down image rows; endpoints included. No dilation, blur, shore repaint or invented fill.',
 'shader_sampler':'sampler2D support_height : filter_linear, repeat_disable; uv=((world_xz-world_bounds.xy)/1m+vec2(0.5))/vec2(769,1537); depth=max(0,sea_level-texture(support_height,uv).r). Signed-height sampling preferred for authentic zero crossing. No mipmaps.',
 'outside_domain':'Do not extend clamped edge into other water. Mask strictly to bounds and retain original depth outside (or expand bake from actual sources).',
 'all_exported_triangle_count':len(raw),'projected_domain_nonvertical_triangle_count':len(tri),'vertical_projected_degenerate_triangles_skipped':int(vertical.sum()),
 'covered_samples':int((~missing).sum()),'missing_samples':int(missing.sum()),'minimum_height_y':float(fheight.min()),'maximum_height_y':float(fheight.max()),'maximum_depth_m':float(depth.max()),
 'files':{f:{'sha256':sha(P/f),'bytes':(P/f).stat().st_size} for f in ['height49-1m-rf.f32','depth49-1m-rf.f32','highest-support-owner-i32.bin']},
 'validation':{'seed':490050,'bvh_nodes':len(nodes),'grid_point_height_error':summary(grid_samples),'random_continuous_bilinear_height_error':summary(continuous),'random_water_vertical_depth_error':summary(water),'actual_exposed_shore_zero_height_error':summary(shore_errors),'actual_exposed_shore_texture_zero_offset':summary(shore_offsets),'shore_zero_not_found_within_2m':sum(s['nearest_texture_zero_offset_m'] is None for s in shore),'note':'Grid-point error tests storage/raster correctness. Continuous and shoreline errors quantify expected 1m bilinear approximation, including steep island sides and upper-envelope mesh transitions; they are NOT claimed zero.'},
 'domain_edges':edge_stats,'actual_shore_samples':shore,'worst_continuous_errors':sorted(points,key=lambda p:p['error_m'],reverse=True)[:30],
 'unchanged_source_expected_sha256':META['source_sha256'],'elapsed_seconds':time.time()-start,
 'candidate_created':False,'visual_acceptance':False,
}
(P/'depth49-bake-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ['width','height','covered_samples','minimum_height_y','maximum_height_y','maximum_depth_m','validation','domain_edges','elapsed_seconds']},indent=2),flush=True)
# User-inspectable diagnostic previews only. Scientific float textures remain authoritative.
from PIL import Image
img=np.zeros((H,W,3),np.uint8);d=np.clip(depth/40,0,1)
img[:,:,0]=(20*(1-d)).astype('uint8');img[:,:,1]=(180*(1-d)+30).astype('uint8');img[:,:,2]=(110+130*d).astype('uint8')
img[fheight>=0]=[101,124,74]
Image.fromarray(img).save(P/'depth49-1m-preview.png')
