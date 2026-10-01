"""Pre-union57-control actualtriangle support diagnostic, noBlender/world."""
import json
from pathlib import Path
import numpy as np
from triangle_checks58c import stations,vertical_hits
P=Path(__file__).resolve().parent;plan=json.loads((P/'authoring-plan58c.json').read_text());specs=json.loads((P/'native-control-input58c.json').read_text())['controls']
meshes=[(s['id'],np.asarray(s['vertices'])[np.asarray(s['faces'])]) for s in specs];rows=[]
for corridor in plan['valley_corridors']:
 samples=[];lo,hi=corridor['intended_floor_y_range_m']
 for station in stations(corridor):
  intervals=[]
  for name,t in meshes:
   hit=vertical_hits(t,station['world_xz'])
   for v in hit['solid_intervals']:intervals.append(dict(v,control=name))
  merged=[]
  for v in sorted(intervals,key=lambda q:-q['top_y_m']):
   if merged and v['top_y_m']>=merged[-1]['bottom_y_m']:
    merged[-1]['bottom_y_m']=min(merged[-1]['bottom_y_m'],v['bottom_y_m']);merged[-1]['control_ids'].append(v['control'])
   else:merged.append(dict(top_y_m=v['top_y_m'],bottom_y_m=v['bottom_y_m'],control_ids=[v['control']]))
  first=merged[0] if merged else None;good=bool(first and first['top_y_m']-first['bottom_y_m']>=160 and lo<=first['top_y_m']<=hi)
  samples.append(dict(station,merged_control_solid_intervals=merged,passed=good))
 rows.append(dict(id=corridor['id'],sample_count=len(samples),passed_count=sum(s['passed'] for s in samples),samples=samples))
out=dict(corridors=rows,method='Exactactualcontroltriangle rayintervalunion. Staticcontrolgeometry only; voxelunion must be tested independently.',blender_started=False,world_loaded=False)
(P/'static-support58c.json').write_text(json.dumps(out,indent=2)+'\n')
for r in rows:
 failed=[s for s in r['samples'] if not s['passed']];print(r['id'],r['passed_count'],'/',r['sample_count']);print(json.dumps(failed[:8],indent=2))
