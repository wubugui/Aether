from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
names={'27e':'coast-environment-27e-20260908T152222Z-bded23dbcd5c4849967297a6ad1a8f20','27f':'coast-environment-27f-20260908T152526Z-f1543e06af9f4533a1689edaf5dc0add'}
rows={}
for label,name in names.items():
    run=R/'captures/validation_runs'/name
    d=json.loads((run/'images/night-reference.png.json').read_text(encoding='utf-8'))
    env=run/'study-inputs'/('new-environment'+label)
    rows[label]={'moon':next(a for a in d['environment_study']['native_sky_assets'] if a['asset']=='moon'),'camera':d['camera'],'files':{n:hashlib.sha256((env/n).read_bytes()).hexdigest() for n in ['sky-assets/moon.glb','sky-assets/moon.blend','moon.gdshader','open_sky.gdshader']}}
out=R/'reviews/round-27f-moon-missing-input-diagnostic.json';assert not out.exists()
out.write_text(json.dumps({'scope':'Moon absent in both actual27f reference images. This compares frozen inputs only; cause is not established.','runs':rows},indent=2),encoding='utf-8')
print(json.dumps(rows,indent=2))
