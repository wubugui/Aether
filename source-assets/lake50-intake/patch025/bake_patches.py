#!/usr/bin/env python3
import json,math,hashlib,collections,time
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;BASE=P.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta=json.loads((BASE/'support49-export.json').read_text())
assert sha(BASE/'support49-world-f32.bin')==meta['binary_sha256']
assert meta['source_sha256']=='52d13fcb7ea412d3a0fae2eedb1d0f9c369dbe06c0da320d786c26c97c475ec8'
raw=np.fromfile(BASE/'support49-world-f32.bin',dtype='<f4').reshape(-1,3,3).astype(float)
lo=raw[:,:,[0,2]].min(1);hi=raw[:,:,[0,2]].max(1)
groups=collections.defaultdict(list)
for m in meta['included_meshes']:
 if m['category'].startswith('LakeIslands49/'):groups[m['path'].split('/')[2]].append(m)
patches=[]
for name,ms in groups.items():
 footprint=[min(m['world_aabb_min'][0] for m in ms),min(m['world_aabb_min'][2] for m in ms),max(m['world_aabb_max'][0] for m in ms),max(m['world_aabb_max'][2] for m in ms)]
 bounds=[math.floor(footprint[0]*4)/4-12,math.floor(footprint[1]*4)/4-12,math.ceil(footprint[2]*4)/4+12,math.ceil(footprint[3]*4)/4+12]
 x0,z0,x1,z1=bounds;spacing=.25;w=round((x1-x0)/spacing)+1;h=round((z1-z0)/spacing)+1
 mask=(hi[:,0]>=x0)&(lo[:,0]<=x1)&(hi[:,1]>=z0)&(lo[:,1]<=z1)
 indices=np.where(mask)[0];height=np.full((h,w),-np.inf,np.float64)
 for k in indices:
  a,b,c=raw[k];d=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
  if abs(d)<1e-12:continue
  ix0=max(0,int(math.ceil((lo[k,0]-x0)/spacing-1e-8)));ix1=min(w-1,int(math.floor((hi[k,0]-x0)/spacing+1e-8)))
  iz0=max(0,int(math.ceil((lo[k,1]-z0)/spacing-1e-8)));iz1=min(h-1,int(math.floor((hi[k,1]-z0)/spacing+1e-8)))
  if ix0>ix1 or iz0>iz1:continue
  xx=np.arange(ix0,ix1+1,dtype=float)[None,:]*spacing+x0;zz=np.arange(iz0,iz1+1,dtype=float)[:,None]*spacing+z0
  wa=((b[2]-c[2])*(xx-c[0])+(c[0]-b[0])*(zz-c[2]))/d
  wb=((c[2]-a[2])*(xx-c[0])+(a[0]-c[0])*(zz-c[2]))/d;wc=1-wa-wb
  yy=a[1]*wa+b[1]*wb+c[1]*wc;sub=height[iz0:iz1+1,ix0:ix1+1]
  take=(wa>=-1e-8)&(wb>=-1e-8)&(wc>=-1e-8)&(yy>sub);sub[take]=yy[take]
 assert np.isfinite(height).all(),f'{name} has uncovered samples; no fabricated fill allowed'
 path=P/(name+'-height025-rf.f32');assert not path.exists(),f'Refuse overwrite {path}'
 height.astype('<f4').tofile(path)
 margins=[footprint[0]-x0,footprint[1]-z0,x1-footprint[2],z1-footprint[3]]
 record={'name':name,'actual_ground_footprint_xmin_zmin_xmax_zmax':footprint,'world_bounds':bounds,'size':[w,h],'spacing_m':spacing,'feather_width_m':8.0,'footprint_margin_to_domain_m':margins,'footprint_margin_to_feather_inner_edge_m':[m-8 for m in margins],'minimum_margin_beyond_feather_m':min(margins)-8,'raw_float32_file':path.name,'raw_sha256':sha(path),'image_resource':name+'-height025-rf.res','exr_file':name+'-height025.exr','sample_count':int(height.size),'missing_samples':0,'min_height_y':float(height.min()),'max_height_y':float(height.max()),'projected_overlapping_input_triangles':len(indices),'source_meshes':[m['path'] for m in ms]}
 patches.append(record);print(name,bounds,[w,h],record['raw_sha256'],flush=True)
report={'purpose':'Additive 0.25m island height patches for existing49 material diagnosis only; no new candidate','source_scene_sha256':meta['source_sha256'],'source_export_manifest_sha256':sha(BASE/'support49-export.json'),'source_triangle_binary_sha256':meta['binary_sha256'],'frozen_base_height_rf_sha256':sha(BASE/'height49-1m-rf.f32'),'frozen_base_height_image_sha256':sha(BASE/'height49-1m-rf.res'),'source_geometry':'Same actual saved49 Mesh.get_faces world triangles as frozen1m bake, all intersecting static support including island roots/shoulders/wetshore/solid grass caps','sea_level_y':0,'pixel_uv':'((world_xz - world_bounds.xy) / spacing_m + vec2(0.5)) / vec2(size)','sampler':'filter_linear, repeat_disable, no mipmaps, no source_color/sRGB conversion','blend':'Outside bounds weight strictly0. Inside distance d=min(x-xmin,z-zmin,xmax-x,zmax-z); w=smoothstep(0,8,d); h=mix(base_signed_height,patch_signed_height,w); depth=max(0,-h). Four domains do not overlap.','patches':patches}
assert not (P/'patches.json').exists();(P/'patches.json').write_text(json.dumps(report,indent=2))
