"""Real triangle unions; a repeated prototype is diagnostic, not authored variants."""
import hashlib,importlib.util,json,math,re
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt,label
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
SPEC=importlib.util.spec_from_file_location('coverage52e',ROOT/'cloud-evidence/cloudsea52e-coverage-research-20261001/analyze_coverage.py')
C=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(C)
OUT=P/'coverage-two-body';OUT.mkdir(exist_ok=True)
baseline=json.loads((C.OUT/'coverage-report.json').read_text())
for f in baseline['source_files']:
    assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
scene=(C.PROJECT/'scenes/candidate51b/Game51b.tscn').read_text();anchors=[]
for m in re.finditer(r'\[node name="(CloudSea_[^"]+)" type="Node3D" parent="SkyRegion39"\]\ntransform = Transform3D\(([^)]+)\)\n\n\[node name="cloud_sea_46_([012])_continuous_crown"',scene):
    nums=np.array([float(v) for v in m[2].split(',')]);anchors.append({'name':m[1],'variant':int(m[3]),'basis':nums[:9].reshape(3,3).T,'position':nums[9:]})
assert len(anchors)==25
original={i:C.glb_meshes(P.parent/f'cloud-sea52e/cloud_sea_52e_{i}.glb') for i in range(3)}
connector=C.glb_meshes(P/'cloud_sea_52f_pair_v0.glb');world=[]
for a in anchors:
    for part in original[a['variant']]+connector:world.append(part['triangles']@a['basis'].T+a['position'])
triangles=np.concatenate(world)
cover,top=C.raster(triangles,(345,345),lambda tri:(tri[:,[0,2]]-[1475,1275])/10,y_values=True)
dist=distance_transform_edt(~cover)*10;iy,ix=np.unravel_index(dist.argmax(),dist.shape)
labels,count=label(~cover);sizes=np.bincount(labels.ravel())[1:]
row={'world_triangles':len(triangles),'interior_topdown_coverage_fraction':float(cover.mean()),
     'uncovered_fraction':float((~cover).mean()),'largest_empty_sample_radius_m':float(dist.max()),
     'largest_empty_center_xz':[1475+(ix+.5)*10,1275+(iy+.5)*10],
     'largest_connected_empty_sample_area_m2':int(sizes.max()*100),
     'top_visible_surface_height_percentiles_m':{str(p):float(np.percentile(top[cover],p)) for p in (0,10,50,90,100)},
     'camera_cloudsea_triangle_coverage':[]}
im=np.zeros((*cover.shape,3),np.uint8);im[:]=[16,26,49];t=np.clip((top[cover]-500)/650,0,1)
im[cover]=np.column_stack([75+130*t,120+105*t,155+85*t]).astype(np.uint8)
Image.fromarray(im).resize((690,690),Image.Resampling.NEAREST).save(OUT/'prototype-repeated-topdown-triangle-height.png')
captures={r['name']:r for r in json.loads((C.RUN/'51b/report.json').read_text())['captures']}
for name in ('1216-front','1216-side','1216-back'):
    c=captures[name];vals=np.array(c['camera_transform']);basis=vals[:9].reshape(3,3).T;position=vals[9:]
    cam=(triangles-position)@basis;clipped=[]
    for tri in cam:
        if np.all(-tri[:,2]>=c['camera_near']):clipped.append(tri)
        elif np.any(-tri[:,2]>=c['camera_near']):clipped.extend(C.clip_near(tri,c['camera_near']))
    h,w=166,295;cot=1/math.tan(math.radians(c['camera_fov'])/2)
    def project(tri):
        depth=-tri[:,2]
        return np.column_stack(((tri[:,0]/depth*cot/(w/h)*.5+.5)*w,(-tri[:,1]/depth*cot*.5+.5)*h))
    mask,_=C.raster(np.array(clipped),(h,w),project)
    row['camera_cloudsea_triangle_coverage'].append({'name':name,'full_frame_fraction':float(mask.mean()),
     'lower_half_fraction':float(mask[83:].mean()),'middle_third_fraction':float(mask[55:111].mean()),
     'upper_third_fraction':float(mask[:55].mean()),'size':[w,h],'camera':c['camera_transform'],'fov':c['camera_fov']})
    Image.fromarray(np.where(mask[:,:,None],np.array([161,197,227],dtype=np.uint8),np.array([16,26,49],dtype=np.uint8))).resize((1180,664),Image.Resampling.NEAREST).save(OUT/f'prototype-repeated-{name}-triangle-mask.png')
report={'method':baseline['method'],
 'prototype_scope':'Two v0 connectors are authored. Coverage repeats their exact triangles at all 25 original roots with each original 52e variant retained. This is a sizing diagnostic, not three completed variants or a world scene.',
 'baseline':baseline['versions']['52e'],'first_saddle_diagnostic':json.loads((P/'coverage/coverage-report52f-prototype.json').read_text())['prototype_repeated_at_all_roots'],'prototype_repeated_at_all_roots':row,'grid':baseline['grid'],
 'baseline_source_hashes_rechecked':True,
 'new_source_sha256':hashlib.sha256((P/'cloud_sea_52f_pair_v0.glb').read_bytes()).hexdigest(),
 'old_75_upper_meshes_changed':False,'saved_world_modified':False,'visual_acceptance':False}
(OUT/'coverage-report52f-two-body.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
