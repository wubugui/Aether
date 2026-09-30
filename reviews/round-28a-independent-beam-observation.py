from pathlib import Path
from PIL import Image
import json
import hashlib
root=Path(r'E:\FeiTing')
new=root/'captures/validation_runs/lantern-lighting-28a-20260908T155358Z-3417ba65aa8a47ad8c3d4faa1969df63/images'
old=root/'captures/validation_runs/coast-moon-readiness-27h-20260908T153333Z-8b7579b40e2d437a8b1142c3bfdb7403/images'
current=Image.open(new/'night-reference.png').convert('RGB')
prior=Image.open(old/'night-reference.png').convert('RGB')
rows=[]
for name,rect in [('lamp',(275,520,375,625)),('near_beam_water',(360,510,940,680)),('middle_lamp_and_water',(950,500,1150,680))]:
    a=current.crop(rect); b=prior.crop(rect)
    pairs=list(zip(a.getdata(),b.getdata()))
    rows.append(dict(name=name,rectangle=rect,pixels=len(pairs),changed_pixels=sum(x!=y for x,y in pairs),max_channel_difference=max(abs(x[i]-y[i]) for x,y in pairs for i in range(3)),warm_pixels_r_gt_g_gt_b=sum(x[0]>x[1]>x[2] and x[0]>32 for x,y in pairs)))
    a.save(root/'reviews'/('round-28a-independent-'+name+'-crop.png'))
side=Image.open(new/'night-beam-side.png').convert('RGB')
side.crop((345,320,860,535)).save(root/'reviews/round-28a-independent-side-crop.png')
result=dict(scope='Original unmodified PNG crops and limited same-camera pixel comparison only. Region names are viewing areas, not exact projected volume boundaries. No inference of absent shader or engine failure.',comparison_baseline=str(old/'night-reference.png'),rows=rows,png_sha256=hashlib.sha256((new/'night-reference.png').read_bytes()).hexdigest())
(root/'reviews/round-28a-independent-beam-observation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
