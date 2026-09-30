from pathlib import Path
import json,hashlib,math,sys
import numpy as np
R=Path(__file__).resolve().parents[1];run=R/'captures/validation_runs'/sys.argv[1]
old=R/'captures/validation_runs/lantern-island-30a-20260908T180129Z-961944bd320b46a4bb5f15256ceb5c8f'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(run/'manifest.json');assert m['passed'] and m['status']=='passed'
for name,item in m['artifacts'].items():assert sha(run/name)==item['sha256'],name
plan=read(R/'captures/lantern_island_study_30k/proportion-plan.json')['faceted_input_plan']
e=read(R/'captures/lantern_island_study_30k/geometry-evidence.json')
triangles=[]
for o in e['new'].values():
    v=np.array(o['vertices'])
    for f in o['polygons']:
        for i in range(1,len(f)-1):
            t=v[[f[0],f[i],f[i+1]]]
            if np.cross(t[1]-t[0],t[2]-t[0])[2]>1e-8:triangles.append(t)
def ground(xy):
    hits=[]
    for t in triangles:
        if np.any(np.array(xy)<t[:,:2].min(axis=0)-1e-5) or np.any(np.array(xy)>t[:,:2].max(axis=0)+1e-5):continue
        b=np.linalg.solve(np.vstack([t[:,:2].T,np.ones(3)]),[*xy,1])
        if min(b)>=-1e-5:hits.append(float(b@t[:,2]))
    assert hits,xy
    return max(hits)
def world_xz(island,xy):
    origin,yaw=([-3050,-2650],0.) if island=='island_c' else ([-2372,-1812],2.)
    x,y=xy;return [origin[0]+math.cos(yaw)*x-math.sin(yaw)*y,origin[1]-math.sin(yaw)*x-math.cos(yaw)*y]
views=[]
for name in ['night-reference','day-reference','day-d-front','day-d-back','day-c-front']:
    p=run/'images'/(name+'.png.json');q=old/'images'/(name+'.png.json');a=read(p);b=read(q)
    assert a['camera']==b['camera'] and a['world_sha256']==b['world_sha256']==sha(R/'scenes/world/World.tscn')
    assert len(a['placements'])==len(b['placements'])==59
    unchanged=0;maximum=0.;moves=[]
    for x,y in zip(a['placements'],b['placements']):
        assert x['kind']==y['kind'] and x.get('island')==y.get('island')
        requested=[]
        if y['kind']=='existing_native_pine' and y.get('island') in ['island_c','island_d']:
            requested=[r for r in plan['tree_relocations'] if max(abs(v-y['position'][i]) for v,i in zip(world_xz(y['island'],r['old_xy']),[0,2]))<.001]
        if requested:
            assert len(requested)==1;r=requested[0];expected=world_xz(x['island'],r['new_xy']);z=ground(r['new_xy'])
            assert max(abs(v-x['position'][i]) for v,i in zip(expected,[0,2]))<.001
            assert abs(x['position'][1]-z)<.001 and abs(x['scale']-r['scale'])<1e-6
            assert x['ground_normal'][1]>=.65 and x['ground_collider'].startswith(x['island_root']+'/')
            moves.append(dict(island=x['island'],old_position=y['position'],actual_position=x['position'],new_local_blender_xy=r['new_xy'],source_all_mesh_top_height_m=z,actual_height_error_m=x['position'][1]-z,ground_normal=x['ground_normal'],ground_collider=x['ground_collider'],island_root=x['island_root'],scale=x['scale']))
        else:
            unchanged+=1;maximum=max(maximum,max(abs(i-j) for i,j in zip(x['position'],y['position'])))
    assert len(moves)==4 and unchanged==55 and maximum<.001
    footing=0.
    for x,y in zip(a['footing_samples'],b['footing_samples']):
        assert x['building']==y['building']
        for i,j in zip(x['samples'],y['samples']):footing=max(footing,abs(i['gap_m']-j['gap_m']))
    assert footing<.001
    views.append(dict(view=name,actual_sidecar_sha256=sha(p),baseline_sidecar_sha256=sha(q),placements=len(a['placements']),unchanged_placements=unchanged,maximum_unchanged_position_delta_m=maximum,maximum_footing_delta_m=footing,declared_tree_relocations=moves))
out=dict(passed=True,run_id=m['run_id'],binding_count=len(m['artifacts']),all_bound_hashes_match=True,views=views,scope='Actual30k versus30a same camera/world and55 retained placements, four declared C/D tree relocations checked against all native source-mesh upper surfaces. Runtime normals/collider plus independent0.3m trunk support checks; no full flight/walking or visual acceptance.')
p=R/'reviews/round-30k-runtime-incremental.json';assert not p.exists();p.write_text(json.dumps(out,indent=2))
print('30k runtime audit passed',len(m['artifacts']),'bindings;55 unchanged placements and4 declared tree relocations')
