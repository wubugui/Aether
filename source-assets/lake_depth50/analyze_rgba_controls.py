"""Independent saved PNG RGBA comparison; never confuses changed pixels with fidelity."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('images',type=Path);args=p.parse_args()
suffixes=['A49-original','B50-depth-disabled','A49-restored','C50-depth-enabled','B50-disabled-restored']
rows=[]
for first in sorted(args.images.glob('*--A49-original.png')):
 name=first.name.split('--')[0];paths=[args.images/(name+'--'+s+'.png') for s in suffixes]
 if not all(x.exists() for x in paths):continue
 arrays=[np.asarray(Image.open(x).convert('RGBA')) for x in paths]
 comparisons=[]
 for a,b,required in [(0,1,True),(0,2,True),(1,4,True),(1,3,name.startswith('outside-domain'))]:
  if arrays[a].shape!=arrays[b].shape: raise ValueError('Dimensions changed')
  different=np.any(arrays[a]!=arrays[b],axis=2);ys,xs=np.where(different)
  comparisons.append(dict(a=suffixes[a],b=suffixes[b],required_equal=required,changed_pixels=int(different.sum()),top300_changed_pixels=int(different[:300].sum()),changed_bounds_xyxy=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if xs.size else None))
 rows.append(dict(view=name,rgba_dimensions=list(arrays[0].shape),comparisons=comparisons,files=[dict(name=x.name,sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in paths]))
report=dict(completed_views=len(rows),expected_views=12,complete=len(rows)==12,all_required_equal=all(c['changed_pixels']==0 for r in rows for c in r['comparisons'] if c['required_equal']),views=rows,scope='Independent PNG RGBA only. Zero-difference controls do not certify physical motion, hardware GPU, or artistic fidelity.',visual_acceptance=False)
(args.images/'independent-pixel-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='views'}))
