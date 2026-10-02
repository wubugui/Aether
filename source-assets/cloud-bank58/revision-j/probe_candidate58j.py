"""One read-only math probe of the fixed J candidate, saving failure literally."""
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
import traceback
from collections import defaultdict
import numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P));import poly58j as poly
from check_preparation58j import project,visibility_proof,c,E_REPORT

def metric_areas(mesh):
 V,F=mesh['vertices'],mesh['faces'];T=V[F];cross=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);length=np.linalg.norm(cross,axis=1);areas=length*.5
 inc=np.degrees(np.arccos(np.clip(np.abs(cross[:,2])/length,0,1)))
 groups=defaultdict(lambda:dict(area_m2=0.,inclination_from_horizontal_degrees=None))
 for key,a,slope in zip(mesh['panels'],areas,inc):
  groups[key]['area_m2']+=float(a);groups[key]['inclination_from_horizontal_degrees']=float(slope)
 total=float(areas.sum())
 fractions=dict(within_15deg_horizontal=float(areas[inc<=15].sum()/total),within_15deg_vertical=float(areas[inc>=75].sum()/total),inclined_15_to_60deg=float(areas[(inc>15)&(inc<60)].sum()/total))
 return dict(measurement='Actual exposed union triangle area in physical source-local UVY, grouped by source plane; not input inclination labels',total_area_m2=total,fractions=fractions,authored_planes=dict(sorted(groups.items(),key=lambda x:-x[1]['area_m2'])),design_targets_only=dict(near_horizontal_lt_15pct=fractions['within_15deg_horizontal']<.15,near_vertical_lt_30pct=fractions['within_15deg_vertical']<.30,inclined_gt_35pct=fractions['inclined_15_to_60deg']>.35),visual_acceptance=False)

def main():
 start=time.monotonic();report=dict(candidate='58J',passed=False,state='running',native_started=False,images=[],visual_acceptance=False,geometry_modified_by_probe=False)
 path=P/'candidate-probe58j.json'
 if path.exists():raise RuntimeError('Never overwrite candidate evidence')
 cpus=sorted(os.sched_getaffinity(0))[:2];os.sched_setaffinity(0,cpus)
 report['cpu_affinity']=cpus
 try:
  config=json.loads((P/'design58j.json').read_text());report['design_sha256']=c.sha(P/'design58j.json')
  report['stage']='build';mesh=poly.build(config)
  report.update(topology=mesh['proof'],arithmetic_audit=mesh['audit'],exposed_clipped_polygon_count=mesh['exposed_polygon_count'],fingerprint=mesh['fingerprint'],metric_union_slopes=metric_areas(mesh))
  report['stage']='float64 intersections';report['double_precision_intersections']=poly.intersection_check(mesh['vertices'],mesh['faces'],eps=1e-8)
  frame=json.loads(c.PLAN.read_text());source=mesh['vertices']@poly.source_basis(frame).T;native=source.astype(np.float32).astype(float)
  report['stage']='float32 topology/intersections';report['float32_topology']=poly.topology(native,mesh['faces'],config['tolerances']);report['float32_intersections']=poly.intersection_check(native,mesh['faces'],eps=1e-8)
  displacement=float(np.linalg.norm(native-source,axis=1).max());report['float32_max_displacement_m']=displacement
  poly.require(displacement<=config['tolerances']['float32_max_displacement_m'],'Float32 displacement bound')
  report['stage']='regions';owners=sorted(set(mesh['owners']));report['exposed_regions']=owners
  poly.require(owners==sorted(r['id'] for r in config['controls']),'Every semantic region must remain exposed')
  report['stage']='fixed cameras';reference=next(r for r in json.loads(E_REPORT.read_text())['layouts'] if r['layout']=='B_staggered_crowns')
  report['cameras_static_only']=[]
  for camera in reference['cameras']:
   xy,row=project(native,camera);row['geometric_visibility']=visibility_proof(native,mesh['faces'],mesh['owners'],mesh['panels'],camera,xy);report['cameras_static_only'].append(row)
  side=report['cameras_static_only'][1]['geometric_visibility']['centroid_visible_area_pixels2_by_region']
  report['stage']='legacy region projected area gates'
  poly.require(side.get('Back_Diagonal_Ledge',0)>1000,'Diagonal ledge not exposed at fixed side view')
  poly.require(side.get('Front_Lower_Buttress',0)>1000 and side.get('Rear_Lower_Buttress',0)>1000,'Independent lower returns not exposed')
  report['stage']='complete';report['passed']=True
 except BaseException as error:
  report['error']=str(error);report['traceback']=traceback.format_exc()
 finally:
  report.update(state='completed',elapsed_seconds=time.monotonic()-start,actual_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
  c.write(path,report)
 print(json.dumps(c.native(report),indent=2))
 return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
