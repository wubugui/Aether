import ast
from pathlib import Path
definition=Path(r'E:\FeiTing\reviews\audit_16a_geometry.py');tree=ast.parse(definition.read_text());prefix=[]
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='manifest' for t in node.targets):break
    prefix.append(node)
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(definition),'exec'))
manifest=json.loads((ROOT/'captures/foreground_study_16f/manifest.json').read_text());report={}
audit=json.loads((ROOT/'reviews/round-16f-independent-geometry-audit.json').read_text())
for item in manifest:
    name=item['name'];p,f,c,sha=read(ROOT/'assets/models'/f'{name}.glb');q,h,nc,nsha=read(ROOT/item['path']);n,area=normals(q,h);labels={};before_by_q={}
    for edit in item['controls']:
        before=np.array(edit['before'])[[0,2,1]]*[1,1,-1];after=np.array(edit['after'])[[0,2,1]]*[1,1,-1];idx=int(np.argmin(np.linalg.norm(q-after,axis=1)));labels[idx]='native_'+str(edit['index']);before_by_q[idx]=before
    for row in item['shelf_controls']:
        for key in ('front','shelf','ridge'):
            target=np.array(row[key+'_blender_xyz'])[[0,2,1]]*[1,1,-1];idx=int(np.argmin(np.linalg.norm(q-target,axis=1)));labels[idx]=key+'_'+str(row['column'])
    for row in item['wall_bend_controls']:
        for key in ('middle','bend','front'):
            target=np.array(row[key+'_blender_xyz'])[[0,2,1]]*[1,1,-1];idx=int(np.argmin(np.linalg.norm(q-target,axis=1)));labels[idx]=key+'_'+str(row['column'])
    entries=[]
    for i in np.where(q[h][:,:,1].max(axis=1)>0)[0]:
        if n[i,1]>=-.001:continue
        points=q[h[i]];oldpoints=np.array([before_by_q.get(int(v),q[v]) for v in h[i]]);oldcross=np.cross(oldpoints[1]-oldpoints[0],oldpoints[2]-oldpoints[0]);oldn=oldcross/np.linalg.norm(oldcross)
        source_matches=[int(np.argmin(np.linalg.norm(p-x,axis=1))) for x in oldpoints];source_ok=all(np.linalg.norm(p[j]-x)<1e-5 for j,x in zip(source_matches,oldpoints));source_faces=[k for k,t in enumerate(f) if set(t)==set(source_matches)] if source_ok else []
        entries.append({'face':int(i),'normal':n[i].tolist(),'slope_degrees':float(np.degrees(np.arccos(np.clip(n[i,1],-1,1)))),'vertices':[{'glb_xyz':q[v].tolist(),'control':labels.get(int(v),'unchanged_original_or_unmapped'),'on_original_rim':int(np.argmin(np.linalg.norm(p-q[v],axis=1))) in rings(p,f)[0] and float(np.min(np.linalg.norm(p-q[v],axis=1)))<1e-5} for v in h[i]],'source_faces_if_original_connectivity':source_faces,'source_normal_if_original_connectivity':oldn.tolist() if source_faces else None})
    report[name]=entries
    if name=='cliff_central_wall':
        sets={key:{idx for idx,label in labels.items() if label.startswith(key+'_')} for key in ('middle','bend')};faces=[]
        for i,t in enumerate(h):
            ids=set(t)
            if ids<=sets['middle']|sets['bend'] and ids&sets['middle'] and ids&sets['bend']:
                faces.append({'face':i,'normal':n[i].tolist(),'slope_degrees':float(np.degrees(np.arccos(np.clip(n[i,1],-1,1))))})
        audit['assets'][name]['actual_profile_triangle_groups']['lower_rock']=faces
    print(name,json.dumps(entries),flush=True)
(ROOT/'reviews/round-16f-downward-localization.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(ROOT/'reviews/round-16f-independent-geometry-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
