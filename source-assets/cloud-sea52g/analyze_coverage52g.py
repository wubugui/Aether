"""Real triangle unions; a repeated prototype is diagnostic, not authored variants."""
import hashlib,importlib.util,json,math,re
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt,label
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
SPEC=importlib.util.spec_from_file_location('coverage52e',ROOT/'cloud-evidence/cloudsea52e-coverage-research-20261001/analyze_coverage.py')
C=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(C)
OUT=P/'coverage';OUT.mkdir(exist_ok=True)
baseline=json.loads((C.OUT/'coverage-report.json').read_text())
for f in baseline['source_files']:
    assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
scene=(C.PROJECT/'scenes/candidate51b/Game51b.tscn').read_text();anchors=[]
for m in re.finditer(r'\[node name="(CloudSea_[^"]+)" type="Node3D" parent="SkyRegion39"\]\ntransform = Transform3D\(([^)]+)\)\n\n\[node name="cloud_sea_46_([012])_continuous_crown"',scene):
    nums=np.array([float(v) for v in m[2].split(',')]);anchors.append({'name':m[1],'variant':int(m[3]),'basis':nums[:9].reshape(3,3).T,'position':nums[9:]})
assert len(anchors)==25
original={i:C.glb_meshes(P.parent/f'cloud-sea52e/cloud_sea_52e_{i}.glb') for i in range(3)}
connectors={vi:C.glb_meshes(P.parent/f'cloud-sea52f/variants/cloud_sea_52f_additions_{vi}.glb') for vi in range(3)};world=[]
original[0]=C.glb_meshes(P/'cloud_sea_52g_upper_v0.glb')
for a in anchors:
    for part in original[a['variant']]+connectors[a['variant']]:world.append(part['triangles']@a['basis'].T+a['position'])
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
Image.fromarray(im).resize((690,690),Image.Resampling.NEAREST).save(OUT/'v0-upper-replacement-topdown-triangle-height.png')
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
    Image.fromarray(np.where(mask[:,:,None],np.array([161,197,227],dtype=np.uint8),np.array([16,26,49],dtype=np.uint8))).resize((1180,664),Image.Resampling.NEAREST).save(OUT/f'v0-upper-replacement-{name}-triangle-mask.png')
report={'method':baseline['method'],
 'prototype_scope':'Only ten original variant0 roots receive three new upper forms; their two52f low bodies remain exact. The other fifteen roots retain original52f upper and low bodies. This is source triangle coverage, not a saved world or visual acceptance.',
 'baseline':baseline['versions']['52e'],'saved52f_source_baseline':json.loads((P.parent/'cloud-sea52f/variants/coverage/coverage-report52f-variants.json').read_text())['three_variant_actual_assignment'],'only_v0_upper_replacement':row,'variant_root_counts':{str(vi):sum(a['variant']==vi for a in anchors) for vi in range(3)},'original_roots':[{'name':a['name'],'variant':a['variant'],'basis':a['basis'].tolist(),'position':a['position'].tolist()} for a in anchors],'grid':baseline['grid'],
 'baseline_source_hashes_rechecked':True,
 'new_source_sha256':hashlib.sha256((P/'cloud_sea_52g_upper_v0.glb').read_bytes()).hexdigest(),
 'ten_v0_roots_receive_three_new_upper_meshes':True,'fifteen_other_roots_unchanged':True,'saved_world_modified':False,'visual_acceptance':False}
(OUT/'coverage-report52g.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
