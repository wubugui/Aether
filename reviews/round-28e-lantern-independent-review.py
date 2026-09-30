from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
run=root/'captures/validation_runs/lantern-lighting-28e-20260908T161327Z-30f38fcb128c469db1a26b76deef33dd'
manifest=json.loads((run/'manifest.json').read_text(encoding='utf-8'))
assert manifest['passed'] and manifest['status']=='passed'
views=['night-reference','night-beam-side','night-lamp-close','night-reverse','day-reference']
data={'run':run.name,'scope':'Independent review of actual five saved GPU views after ALBEDO repair; not full world acceptance','images':[]}
for name in views:
 p=run/'images'/(name+'.png');q=Path(str(p)+'.json');j=json.loads(q.read_text(encoding='utf-8'))
 assert j['run_id']==run.name
 data['images'].append({'view':name,'image_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sidecar_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'camera':j['camera'],'beams':len(j['lantern_lighting']['beams']),'world_sha256':j['world_sha256']})
data['verdict']='Rendering fix verified; visual rework required'
data['findings']=['28e shader now uses nonzero ALBEDO with unshaded Compatibility; actual reference and side views show spatial beams.','Distance density currently makes broad far sections brighter than source sections. Cone geometry widening without matching illumination falloff explains the observed distant haze bands.','Near-source contrast, beam color and shape, full camera occlusion and light-space shadows need further visual evidence; raw ray counts do not accept them.','Whole reference1342 retains substantial cloud, water, coast rock silhouette and settlement-density gaps.']
(root/'reviews/round-28e-lantern-independent-review.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data,indent=2))
