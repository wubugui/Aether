"""Independent actual GLB audit; no production writes or engine launch."""
import ast
from pathlib import Path
src=Path(r'E:\FeiTing\reviews\audit_16b_geometry.py').read_text()
src=src.replace('16b','16f').replace('20260908T015118Z-c8ff6b7fed9d4c7dad11c4ffb2dac90d','20260908T045736Z-e74eb3b4aef7419f99ddd9ad5405864d')
old='target=q[a]*.38+q[b]*.62;linear_y=target[1];target[1]=min(q[a,1]+[2,3,2.5,3.5,2.5,2,1.5,1][k],q[b,1]-.5)'
new="fraction=item['shelf_controls'][k]['width_fraction'];linear_y=(q[a]*(1-fraction)+q[b]*fraction)[1];target=np.array(item['shelf_controls'][k]['shelf_blender_xyz'])[[0,2,1]]*np.array([1,1,-1])"
assert old in src
exec(compile(src.replace(old,new),'<16f adapted audit>','exec'))
item=next(x for x in manifest if x['name']=='cliff_central_wall')
p,f,c,sha=read(ROOT/'assets/models/cliff_central_wall.glb');q,h,c,nsha=read(ROOT/item['path'])
origin=np.array(cat[item['name']]['position']);native={}
for control in controls['assets'][item['name']]['upper_controls']:
    target=np.array(control['actual_world_xyz'])-origin
    idx={'mid':5,'front':10,'ridge':15,'shoulder':20,'rear':25}.get(control['row'])
    if idx is None:continue
    edit=next((x for x in item['controls'] if x['index']==idx+control['k']),None)
    if edit:target=np.array(edit['after'])[[0,2,1]]*np.array([1,1,-1])
    match=int(np.argmin(np.linalg.norm(q-target,axis=1)));assert np.linalg.norm(q[match]-target)<1e-4
    native[(control['row'],control['k'])]=match
for bend in item['wall_bend_controls']:
    target=np.array(bend['bend_blender_xyz'])[[0,2,1]]*np.array([1,1,-1]);match=int(np.argmin(np.linalg.norm(q-target,axis=1)));assert np.linalg.norm(q[match]-target)<1e-5
    native[('bend',bend['column'])]=match
    target=np.array(bend['middle_blender_xyz'])[[0,2,1]]*np.array([1,1,-1]);match=int(np.argmin(np.linalg.norm(q-target,axis=1)));assert np.linalg.norm(q[match]-target)<1e-5
    native[('mid',bend['column'])]=match
normal,area=normals(q,h);groups={}
for label,row1,row2 in [('lower_rock','mid','bend'),('upper_rock','bend','front'),('grass_cap','front','ridge')]:
    a={v for (row,k),v in native.items() if row==row1};b={v for (row,k),v in native.items() if row==row2};faces=[]
    for i,t in enumerate(h):
        ids=set(t)
        if ids<=a|b and ids&a and ids&b:
            faces.append({'face':i,'normal':normal[i].tolist(),'slope_degrees':float(np.degrees(np.arccos(np.clip(normal[i,1],-1,1)))),'area_m2':float(area[i]),'glb_xyz':q[t].tolist(),'linear_color':c[i].tolist()})
    groups[label]=faces
    print(label,len(faces),[round(x['slope_degrees'],3) for x in faces],flush=True)
report['assets']['cliff_central_wall']['actual_profile_triangle_groups']=groups
checks={}
for x in manifest:
    for suffix,expected in [('glb',report['assets'][x['name']]['source_glb_sha256']),('blend',x['source_sha256'])]:
        path=ROOT/('assets/models' if suffix=='glb' else 'blender/cliff_kit')/(x['name']+'.'+suffix)
        value=hashlib.sha256(path.read_bytes()).hexdigest();checks[str(path)]={'sha256':value,'matches_original':value==expected};assert value==expected
report['production_source_checks']=checks
report['run_status']=rm.get('status')
(ROOT/'reviews/round-16f-independent-geometry-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
