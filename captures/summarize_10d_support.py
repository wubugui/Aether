import csv,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
R=Path('D:/test6')
d=json.loads((R/'captures/round-10d-readonly-support.json').read_text())
rows=d['affected_samples']
out=R/'reviews/round-10d-affected-samples.csv'
with out.open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['category','object','detail','x','old_y','z','old_ground_y','candidate_ground_y','support_delta_m','candidate_clearance_m','baseline_road_error_m','candidate_road_error_m','old_support_owner','new_support_owner'])
    for r in rows:w.writerow([r['category'],r['object'],r['detail'],*r['point'],r['baseline']['height'],r['candidate']['height'],r['support_delta_metres'],r['candidate_clearance_metres'],r.get('baseline_road_error',''),r.get('candidate_road_error',''),r['baseline']['owner'],r['candidate']['owner']])
rois={'dark_belly':[970,775,1190,941],'wide_wall':[1160,742,1300,870],'central_interior':[1280,765,1415,920],'foreground':[1070,622,1672,941]}
imgs={name:np.array(Image.open(R/path).convert('RGB'),dtype=np.float64) for name,path in [('reference','assets/reference.jpg'),('10c','captures/round-10c-study-opening.png'),('10d','captures/round-10d-study-opening.png')]}
stats={}
for name,(x0,y0,x1,y1) in rois.items():
    ref=imgs['reference'][y0:y1,x0:x1]
    stats[name]={'bounds':[x0,y0,x1,y1],'reference_mean_rgb':ref.mean((0,1)).tolist()}
    for version in ['10c','10d']:
        a=imgs[version][y0:y1,x0:x1]
        stats[name][version]={'rgb_mae':float(abs(a-ref).mean()),'mean_rgb':a.mean((0,1)).tolist()}
hashes={path:hashlib.sha256((R/path).read_bytes()).hexdigest() for path in ['assets/reference.jpg','captures/round-10d-study-opening.png','captures/round-10d-study-cliff-side.png','captures/round-10d-study-cliff-back.png','captures/round-10d-readonly-support.json','captures/round-10d-readonly-support-manifest.json','reviews/round-10d-affected-samples.csv']}
(R/'reviews/round-10d-readonly-summary.json').write_text(json.dumps({'rois':stats,'hashes':hashes},indent=2))
print(json.dumps({'rois':stats,'hashes':hashes},indent=2))
