"""Bounded offline triangle survey. Writes only beside this file, never launches an engine."""
from pathlib import Path
import os,sys,json,importlib.util,hashlib
os.environ['MPLCONFIGDIR']=str(Path(__file__).parent/'mpl-cache')
import numpy as np
import scipy.ndimage as ndi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent/'Aether'
SRC=ROOT/'source-assets/cloud-bank58/revision-k/world-trial-v1/provenance58k.py'
spec=importlib.util.spec_from_file_location('provenance58k_offline',SRC)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
NAMES=[f'CloudSea_{x}_{z}' for x in [0,1,2] for z in [0,1,2]]
m.NEIGHBORS=NAMES
C=m.decode_clouds(); SEL='CloudSea_1_1'
lo,hi=np.array(C[SEL]['world_bounds']); extent=[3500.,5200.,3300.,5100.]

def raster(tris,step):
    xs=np.arange(extent[0]+step/2,extent[1],step);zs=np.arange(extent[2]+step/2,extent[3],step)
    top=np.full((len(zs),len(xs)),-np.inf);bottom=np.full_like(top,np.inf); count=np.zeros(top.shape,np.uint16)
    skipped=0
    for t in tris:
        a,b,c=t[:,[0,2]];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-10:skipped+=1;continue
        ix0=max(0,int(np.ceil((min(a[0],b[0],c[0])-xs[0])/step)));ix1=min(len(xs),int(np.floor((max(a[0],b[0],c[0])-xs[0])/step))+1)
        iz0=max(0,int(np.ceil((min(a[1],b[1],c[1])-zs[0])/step)));iz1=min(len(zs),int(np.floor((max(a[1],b[1],c[1])-zs[0])/step))+1)
        if ix0>=ix1 or iz0>=iz1:continue
        x,z=np.meshgrid(xs[ix0:ix1],zs[iz0:iz1]); u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(z-c[1]))/den;v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(z-c[1]))/den;w=1-u-v
        keep=(u>=-1e-10)&(v>=-1e-10)&(w>=-1e-10);y=u*t[0,1]+v*t[1,1]+w*t[2,1]
        top[iz0:iz1,ix0:ix1]=np.maximum(top[iz0:iz1,ix0:ix1],np.where(keep,y,-np.inf));bottom[iz0:iz1,ix0:ix1]=np.minimum(bottom[iz0:iz1,ix0:ix1],np.where(keep,y,np.inf));count[iz0:iz1,ix0:ix1]+=keep
    return xs,zs,top,bottom,count,skipped

step=5.; R={k:raster(v['triangles'],step) for k,v in C.items()}
xs,zs,top,bottom,count,_=R[SEL]; M=np.isfinite(top)
neighbor=np.zeros(M.shape,bool)
for k,r in R.items():
    if k!=SEL:neighbor|=np.isfinite(r[2])
exclusive=M&~neighbor
labels,nlab=ndi.label(M);hole=ndi.binary_fill_holes(M)&~M
nearboundary=(ndi.distance_transform_edt(M,sampling=step)<=60)&M
stats=[]
for k,r in R.items():
    o=M&np.isfinite(r[2]);dist=np.maximum(np.maximum(bottom,r[3])-np.minimum(top,r[2]),0)
    h=o&(dist<=1e-8)
    d={kk:vv for kk,vv in C[k].items() if kk!='triangles'}
    d.update(projected_overlap_with_selected_m2=int(o.sum())*step**2,overlap_y_interval_m2=int(h.sum())*step**2,overlap_cells=int(o.sum()),vertical_envelope_gap_range_m=[float(dist[o].min()),float(dist[o].max())] if o.any() else None)
    stats.append(d)
for name,mask in [('selected',M),('exclusive',exclusive)]:
    yy=top[mask];print(name,mask.sum()*step**2,'Y percentiles',np.percentile(yy,[0,10,25,50,75,90,100]).round(2))
print('nearbound',nearboundary.sum()*25,'unsupported boundary',np.count_nonzero(nearboundary&~neighbor)*25)

# Cross-sections at X and Z values are direct vertical envelopes of indexed triangles at 5m-grid centers.
sections=[]
for axis,vals in [('z',[3550,3650,3850,4150,4450,4700,4875]),('x',[3750,3900,4100,4350,4600,4850,5000])]:
 for val in vals:
  i=int(np.argmin(abs((zs if axis=='z' else xs)-val)));mk=M[i,:] if axis=='z' else M[:,i];vals1=xs if axis=='z' else zs
  ids=np.where(mk)[0];runs=[]
  for rr in np.split(ids,np.where(np.diff(ids)>1)[0]+1):
   if len(rr):runs.append([float(vals1[rr[0]]-step/2),float(vals1[rr[-1]]+step/2)])
  sections.append({'fixed_axis':axis,'requested_coordinate':val,'sampled_coordinate':float((zs if axis=='z' else xs)[i]),'footprint_intervals_m':runs})
coarse=raster(C[SEL]['triangles'],10.)
summary={'status':'offline existing-geometry survey, not a new model or native result','selected':SEL,'bounded_scope':NAMES,'world_frame':'Godot X east on plots, +Z upward on plan; Y is up, meters. Cardinal world meanings not asserted.', 'grid':{'cell_m':step,'extent_xmin_xmax_zmin_zmax':extent,'method':'Vertical barycentric intersections of all actual saved indexed triangles, projected union at cell centers; no AABB fill and no convex hull','source_arithmetic':'saved packed positions decoded float32 using existing reviewed decoder; transforms calculated float64 offline','projection_degenerate_triangles_selected':R[SEL][5]},'source_scene':str(m.SCENE.relative_to(ROOT)),'source_scene_sha256':hashlib.sha256(m.SCENE.read_bytes()).hexdigest(),'decoder_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'selected_projected_union_m2':int(M.sum())*25,'selected_projected_union_10m_m2':int(np.isfinite(coarse[2]).sum())*100,'selected_xz_aabb_area_m2':float((hi[0]-lo[0])*(hi[2]-lo[2])),'selected_exclusive_coverage_m2':int(exclusive.sum())*25,'projected_neighbor_union_overlap_m2':int((M&neighbor).sum())*25,'selected_footprint_connected_components_at_5m':int(nlab),'selected_footprint_internal_empty_cells_at_5m':int(hole.sum()),'selected_top_y_percentiles':dict(zip(['min','p10','p25','p50','p75','p90','max'],np.percentile(top[M],[0,10,25,50,75,90,100]).tolist())),'selected_thickness_y_percentiles':dict(zip(['min','p10','p25','p50','p75','p90','max'],np.percentile(top[M]-bottom[M],[0,10,25,50,75,90,100]).tolist())),'clouds':stats,'sections':sections,'limitations':['5m samples are not exact analytic union/intersection/contact','Y envelopes can bridge disconnected intervals; overlap is not proof of solid contact','9 spatially adjacent cloud meshes only; not global geometry, ship occlusion, pixel visibility or flight','No changes to any original source or scene; no engine launched']}
(OUT/'survey.json').write_text(json.dumps(summary,indent=2)+'\n')
np.savez_compressed(OUT/'survey-grids.npz',xs=xs,zs=zs,**{f'{k}_{v}':R[k][j] for k in NAMES for v,j in [('top',2),('bottom',3),('hits',4)]})
fig,axs=plt.subplots(1,2,figsize=(15,8),layout='constrained');colors={'CloudSea_0_0':'#8c6bb1','CloudSea_0_1':'#e76f51','CloudSea_0_2':'#b35806','CloudSea_1_0':'#2a9d8f','CloudSea_1_2':'#9467bd','CloudSea_2_0':'#72b7b2','CloudSea_2_1':'#d4a017','CloudSea_2_2':'#bc80bd'}
for ax in axs:
 for k,r in R.items():
  if k!=SEL and np.any(M&np.isfinite(r[2])):
   ax.contour(xs,zs,np.isfinite(r[2]),levels=[.5],colors=[colors[k]],linewidths=1.7)
   mask=np.isfinite(r[2])&M;yy,xx=np.where(mask);ax.text(xs[xx[len(xx)//2]],zs[yy[len(yy)//2]],k.replace('CloudSea_',''),color=colors[k],weight='bold',fontsize=10)
 ax.contour(xs,zs,M,levels=[.5],colors=['#172b4d'],linewidths=2)
 ax.set(xlim=(3500,5200),ylim=(3300,5100),xlabel='World X (m)',ylabel='World Z (m)');ax.set_aspect('equal');ax.grid(alpha=.2)
im=axs[0].imshow(np.where(M,top,np.nan),origin='lower',extent=extent,cmap='Blues_r',vmin=650,vmax=1080);fig.colorbar(im,ax=axs[0],shrink=.7,label='Topmost saved triangle Y (m)')
axs[0].set_title('MEASURED: old unit top envelope + actual neighbor outlines\n5 m triangle samples; not a rendered game view')
axs[1].imshow(np.where(M,np.where(exclusive,2,1),0),origin='lower',extent=extent,cmap=ListedColormap(['#ffffff','#a7d7c5','#b0b6db']),vmin=0,vmax=2)
axs[1].set_title('MEASURED: coverage responsibility\nPurple: old-only / green: projected neighbor overlap')
fig.suptitle('Existing CloudSea_1_1 survey | No new asset | Diagrams, not native screenshots',fontsize=16)
fig.savefig(OUT/'01-existing-footprint-survey.png',dpi=150)
print(json.dumps({k:summary[k] for k in ['selected_projected_union_m2','selected_projected_union_10m_m2','selected_xz_aabb_area_m2','selected_exclusive_coverage_m2','projected_neighbor_union_overlap_m2','selected_footprint_connected_components_at_5m','selected_footprint_internal_empty_cells_at_5m']},indent=2))
for v in stats:print(v['path'].split('/')[1],v['projected_overlap_with_selected_m2'],v['overlap_y_interval_m2'],v['vertical_envelope_gap_range_m'])
