#!/usr/bin/env python3
"""Identify actual52e cloud parts at observed pixels, without a renderer or edits."""
import json
import math
import re
import numpy as np
from analyze_coverage import ROOT,OUT,PROJECT,RUN,glb_meshes

scene=(PROJECT/'scenes/candidate51b/Game51b.tscn').read_text()
variants={i:glb_meshes(PROJECT/f'assets/clouds52e/cloud_sea_52e_{i}.glb') for i in range(3)}
parts=[]
for m in re.finditer(r'\[node name="(CloudSea_[^"]+)" type="Node3D" parent="SkyRegion39"\]\ntransform = Transform3D\(([^)]+)\)\n\n\[node name="cloud_sea_46_([012])_continuous_crown"',scene):
    t=np.array([float(v) for v in m[2].split(',')]);basis=t[:9].reshape(3,3).T
    for part in variants[int(m[3])]:parts.append({'path':m[1]+'/'+part['name'],'triangles':part['triangles']@basis.T+t[9:]})
captures={c['name']:c for c in json.loads((RUN/'51b/report.json').read_text())['captures']}
results=[]
for name,coordinates in {'1216-front':[(550,500),(535,540),(650,470),(810,374),(850,500),(315,455)],'1216-side':[(450,440),(730,530)]}.items():
    c=captures[name];t=np.array(c['camera_transform']);basis=t[:9].reshape(3,3).T;origin=t[9:];tan=math.tan(math.radians(c['camera_fov']/2));w,h=c['size']
    for px,py in coordinates:
        ray=basis@np.array([(2*(px+.5)/w-1)*tan*(w/h),(1-2*(py+.5)/h)*tan,-1]);ray/=np.linalg.norm(ray)
        hits=[]
        for part in parts:
            tr=part['triangles'];edge1=tr[:,1]-tr[:,0];edge2=tr[:,2]-tr[:,0]
            p=np.cross(ray,edge2);det=np.einsum('ij,ij->i',edge1,p);safe=np.abs(det)>1e-8
            inv=np.zeros(len(tr));inv[safe]=1/det[safe];q0=origin-tr[:,0]
            u=np.einsum('ij,ij->i',q0,p)*inv;q=np.cross(q0,edge1)
            v=np.einsum('j,ij->i',ray,q)*inv;distance=np.einsum('ij,ij->i',edge2,q)*inv
            good=safe&(u>=0)&(v>=0)&(u+v<=1)&(distance>c['camera_near'])&(distance<c['camera_far'])
            if np.any(good):hits.append((float(distance[good].min()),part))
        if not hits:results.append({'view':name,'pixel':[px,py],'cloudsea_ray_hit':False});continue
        distance,part=min(hits,key=lambda item:item[0]);vertices=part['triangles'].reshape(-1,3);camera=(vertices-origin)@basis;front=camera[-camera[:,2]>c['camera_near']]
        projection=np.column_stack(((front[:,0]/-front[:,2]/tan/(w/h)*.5+.5)*w,(-front[:,1]/-front[:,2]/tan*.5+.5)*h))
        lo=np.maximum(projection.min(axis=0),[0,0]);hi=np.minimum(projection.max(axis=0),[w,h])
        results.append({'view':name,'pixel':[px,py],'cloudsea_ray_hit':True,'nearest_part':part['path'],'distance_m':distance,'actual_mesh_projected_clipped_bbox':[lo.tolist(),hi.tolist()],'bbox_width_fraction':float((hi[0]-lo[0])/w),'bbox_height_fraction':float((hi[1]-lo[1])/h),'scope':'CloudSea-only exact ray hit and geometric projected part bbox, not rendered visible silhouette or reference segmentation'})
report={'observations':results,'reference_camera_runtime_source':'Actual51b report; prior52e runtimeJSON is missing. Input source52e triangles and25 root placements are immutable. This tests the intended paired pose and is not recovered52e runtime metadata.','visual_acceptance':False}
(OUT/'screen-scale-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(results,indent=2))
