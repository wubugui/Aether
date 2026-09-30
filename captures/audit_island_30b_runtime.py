from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
run=R/'captures/validation_runs/lantern-island-30b-20260908T181107Z-79169d5784aa499ea0429f797ff3fc6e'
old=R/'captures/validation_runs/lantern-island-30a-20260908T180129Z-961944bd320b46a4bb5f15256ceb5c8f'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(run/'manifest.json');assert m['passed'] and m['status']=='passed'
for name,item in m['artifacts'].items():assert sha(run/name)==item['sha256'],name
views=[]
for name in ['night-reference','day-reference','day-d-front','day-d-back','day-c-front']:
    p=run/'images'/(name+'.png.json');q=old/'images'/(name+'.png.json')
    a=read(p);b=read(q)
    assert a['camera']==b['camera'],name
    assert a['world_sha256']==b['world_sha256']==sha(R/'scenes/world/World.tscn')
    assert len(a['placements'])==len(b['placements'])
    maximum=0.
    for x,y in zip(a['placements'],b['placements']):
        assert x['kind']==y['kind'] and x.get('island')==y.get('island')
        maximum=max(maximum,max(abs(i-j) for i,j in zip(x['position'],y['position'])))
    assert maximum<.001,('Changed rock affected grounded fixture',name,maximum)
    footing=0.
    for x,y in zip(a['footing_samples'],b['footing_samples']):
        assert x['building']==y['building']
        for i,j in zip(x['samples'],y['samples']):footing=max(footing,abs(i['gap_m']-j['gap_m']))
    assert footing<.001,(name,footing)
    views.append(dict(view=name,actual_sidecar_sha256=sha(p),baseline_sidecar_sha256=sha(q),placements=len(a['placements']),maximum_position_delta_m=maximum,maximum_footing_delta_m=footing))
out=dict(passed=True,run_id=m['run_id'],binding_count=len(m['artifacts']),all_bound_hashes_match=True,views=views,scope='Incremental actual30b/30a fixed camera and whole-world identity, all fixture positions and building support samples; no flight or visual acceptance.')
p=R/'reviews/round-30b-runtime-incremental.json';assert not p.exists();p.write_text(json.dumps(out,indent=2))
print('30b incremental runtime passed',len(m['artifacts']),'bindings',max(x['maximum_position_delta_m'] for x in views))
