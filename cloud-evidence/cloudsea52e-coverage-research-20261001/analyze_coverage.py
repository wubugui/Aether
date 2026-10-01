#!/usr/bin/env python3
"""Read-only source triangle coverage at exact saved51b/52e anchors and cameras.
Produces diagnostic masks, never source assets or engine beauty evidence.
"""
import hashlib
import json
import math
import re
import struct
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, label

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PROJECT = ROOT/'candidates/round40-exclusive-20260930/project'
RUN = ROOT/'cloud-evidence/cloudsea52e-paired-20261001T050129Z-geTptG'


def glb_meshes(path):
    raw=path.read_bytes(); n=struct.unpack_from('<I',raw,12)[0]
    data=json.loads(raw[20:20+n]); start=20+n
    size,kind=struct.unpack_from('<II',raw,start); binary=raw[start+8:start+8+size]
    assert kind==0x004e4942
    def accessor(index):
        a=data['accessors'][index]; view=data['bufferViews'][a['bufferView']]
        dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
        dim={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        item=np.dtype(dtype).itemsize; offset=view.get('byteOffset',0)+a.get('byteOffset',0)
        stride=view.get('byteStride',dim*item)
        return np.ndarray((a['count'],dim),dtype=dtype,buffer=binary,offset=offset,strides=(stride,item)).copy()
    result=[]
    for node in data['nodes']:
        if 'mesh' not in node: continue
        assert not any(k in node for k in ('matrix','rotation','translation','scale','children')), 'Unexpected GLB transform; extend parser, never guess'
        for primitive in data['meshes'][node['mesh']]['primitives']:
            pos=accessor(primitive['attributes']['POSITION']).astype(np.float64)
            idx=accessor(primitive['indices']).reshape(-1,3)
            result.append({'name':node['name'],'triangles':pos[idx]})
    return result


def raster(triangles, shape, project, y_values=False):
    h,w=shape; coverage=np.zeros(shape,bool); top=np.full(shape,-np.inf)
    for tri in triangles:
        p=project(tri)
        lo=np.floor(p.min(axis=0)).astype(int); hi=np.ceil(p.max(axis=0)).astype(int)
        xmin,ymin=np.maximum(lo,[0,0]); xmax,ymax=np.minimum(hi,[w-1,h-1])
        if xmax<xmin or ymax<ymin: continue
        ax,ay=p[0];bx,by=p[1];cx,cy=p[2]
        den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        if abs(den)<1e-12: continue
        xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
        u=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/den
        v=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/den
        inside=(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)
        coverage[ymin:ymax+1,xmin:xmax+1]|=inside
        if y_values:
            heights=u*tri[0,1]+v*tri[1,1]+(1-u-v)*tri[2,1]
            current=top[ymin:ymax+1,xmin:xmax+1]
            np.maximum(current,np.where(inside,heights,-np.inf),out=current)
    return coverage,top


def clip_near(triangle,near):
    polygon=list(triangle)
    result=[]
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        ain=-a[2]>=near; bin=-b[2]>=near
        if ain:result.append(a)
        if ain!=bin:
            t=(-near-a[2])/(b[2]-a[2]);result.append(a+t*(b-a))
    return [np.asarray([result[0],result[i],result[i+1]]) for i in range(1,len(result)-1)]


if __name__ == '__main__':
    scene=(PROJECT/'scenes/candidate51b/Game51b.tscn').read_text()
    anchors=[]
    for match in re.finditer(r'\[node name="(CloudSea_[^"]+)" type="Node3D" parent="SkyRegion39"\]\ntransform = Transform3D\(([^)]+)\)\n\n\[node name="cloud_sea_46_([012])_continuous_crown"',scene):
        nums=np.array([float(v) for v in match[2].split(',')]);anchors.append({'name':match[1],'variant':int(match[3]),'basis':nums[:9].reshape(3,3).T,'position':nums[9:]})
    assert len(anchors)==25
    report={'method':'Sampled triangle unions of verifiedGLB source meshes at exact saved51b anchors; no AABB filling. Camera projection uses exact recorded1216 poses, verticalFOV62 and near. Diagnostic masks omit every non-CloudSea object/material/lighting; not rendered images or visual acceptance. Old46 GLB follows preserved46->51b geometry lineage;52e exact GLB hashes were verified in build.','source_files':[],'grid':{'roi_xz':[1475,1275,4925,4725],'step_m':10,'shape':[345,345]},'versions':{},'visual_acceptance':False,'suggested_next_candidate_built':False}
    captures={r['name']:r for r in json.loads((RUN/'51b/report.json').read_text())['captures']}
    for version in ('46','52e'):
        variants={}
        for vi in range(3):
            path=PROJECT/f'assets/clouds{version}/cloud_sea_{version}_{vi}.glb'
            variants[vi]=glb_meshes(path);report['source_files'].append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        world=[]
        for anchor in anchors:
            for part in variants[anchor['variant']]:world.append(part['triangles']@anchor['basis'].T+anchor['position'])
        triangles=np.concatenate(world)
        cover,top=raster(triangles,(345,345),lambda tri:(tri[:,[0,2]]-[1475,1275])/10,y_values=True)
        dist=distance_transform_edt(~cover)*10; max_y,max_x=np.unravel_index(dist.argmax(),dist.shape)
        labels,num=label(~cover); sizes=np.bincount(labels.ravel())[1:]
        rows={'world_triangles':len(triangles),'interior_topdown_coverage_fraction':float(cover.mean()),'uncovered_fraction':float((~cover).mean()),'largest_empty_sample_radius_m':float(dist.max()),'largest_empty_center_xz':[1475+(max_x+.5)*10,1275+(max_y+.5)*10],'largest_connected_empty_sample_area_m2':int(sizes.max()*100),'top_visible_surface_height_percentiles_m':{str(p):float(np.percentile(top[cover],p)) for p in (0,10,50,90,100)},'camera_cloudsea_triangle_coverage':[]}
        image=np.zeros((*cover.shape,3),np.uint8);image[:]=[16,26,49]
        t=np.clip((top[cover]-500)/650,0,1);image[cover]=np.column_stack([75+130*t,120+105*t,155+85*t]).astype(np.uint8)
        Image.fromarray(image).resize((690,690),Image.Resampling.NEAREST).save(OUT/f'{version}-topdown-triangle-height.png')
        for name in ('1216-front','1216-side','1216-back'):
            c=captures[name];vals=np.array(c['camera_transform']);basis=vals[:9].reshape(3,3).T;position=vals[9:]
            cam=(triangles-position)@basis
            clipped=[]
            for tri in cam:
                if np.all(-tri[:,2]>=c['camera_near']):clipped.append(tri)
                elif np.any(-tri[:,2]>=c['camera_near']):clipped.extend(clip_near(tri,c['camera_near']))
            h,w=166,295;cot=1/math.tan(math.radians(c['camera_fov'])/2)
            def project(tri):
                depth=-tri[:,2];return np.column_stack(((tri[:,0]/depth*cot/(w/h)*.5+.5)*w,(-tri[:,1]/depth*cot*.5+.5)*h))
            mask,_=raster(np.array(clipped),(h,w),project)
            topthird=mask[:55];lower=mask[83:];middle=mask[55:111]
            row={'name':name,'full_frame_fraction':float(mask.mean()),'lower_half_fraction':float(lower.mean()),'middle_third_fraction':float(middle.mean()),'upper_third_fraction':float(topthird.mean()),'size':[w,h],'camera':c['camera_transform'],'fov':c['camera_fov']}
            rows['camera_cloudsea_triangle_coverage'].append(row)
            Image.fromarray(np.where(mask[:,:,None],np.array([161,197,227],dtype=np.uint8),np.array([16,26,49],dtype=np.uint8))).resize((1180,664),Image.Resampling.NEAREST).save(OUT/f'{version}-{name}-triangle-mask.png')
        report['versions'][version]=rows
    (OUT/'coverage-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['versions'],indent=2))
