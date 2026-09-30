"""Read-only 16b GLB audit. Reuses independent parser definitions without executing 16a audit."""
import ast
from pathlib import Path
definition=Path(r'E:\FeiTing\reviews\audit_16a_geometry.py')
tree=ast.parse(definition.read_text());prefix=[]
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='manifest' for t in node.targets):break
    prefix.append(node)
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(definition),'exec'))
cat={x['name']:x for x in json.loads((ROOT/'assets/cliff_kit.json').read_text())}
manifest=json.loads((ROOT/'captures/foreground_study_16b/manifest.json').read_text())
controls=json.loads((ROOT/'reviews/restore-20260908-cliff-upper-control-audit.json').read_text())
run=ROOT/'captures/validation_runs/foreground-16b-20260908T015118Z-c8ff6b7fed9d4c7dad11c4ffb2dac90d'
rm=json.loads((run/'manifest.json').read_text())
report={'scope':'Actual 16b exported GLB geometry checks; independent images reviewed separately. No production writes, no Blender/Godot launched.','artifacts':{},'assets':{}}
for key,a in rm['artifacts'].items():
    if key.startswith('images/') or key.endswith('.glb'):
        sha=hashlib.sha256((run/key).read_bytes()).hexdigest();report['artifacts'][key]={'sha256':sha,'matches_run_manifest':sha==a['sha256']};assert sha==a['sha256']
for item in manifest:
    name=item['name'];p,f,c,sha=read(ROOT/'assets/models'/f'{name}.glb');q,h,nc,nsha=read(ROOT/item['path']);assert nsha==item['glb_sha256']
    source_rim,source_floor=rings(p,f);nr,nf=rings(q,h)
    expected=p.copy()
    for edit in item['controls']:
        before=np.array(edit['before'])[[0,2,1]]*np.array([1,1,-1]);after=np.array(edit['after'])[[0,2,1]]*np.array([1,1,-1]);i=int(np.argmin(np.linalg.norm(p-before,axis=1)));j=int(np.argmin(np.linalg.norm(q-after,axis=1)));assert np.linalg.norm(p[i]-before)<1e-5 and np.linalg.norm(q[j]-after)<1e-5;expected[i]=q[j]
    missing=[i for i,x in enumerate(expected) if np.min(np.linalg.norm(q-x,axis=1))>1e-5];added=[i for i,x in enumerate(q) if np.min(np.linalg.norm(expected-x,axis=1))>1e-5]
    entry={'source_glb_sha256':sha,'candidate_glb_sha256':nsha,'candidate_geometry':stat(q,h),'rim_count':len(nr),'floor_count':len(nf),'rim_exactly_same_as_production':{tuple(p[i]) for i in source_rim}=={tuple(q[i]) for i in nr},'floor_exactly_same_as_production':{tuple(p[i]) for i in source_floor}=={tuple(q[i]) for i in nf},'original_positions_missing_after_declared_moves':missing,'added_positions':q[added].tolist(),'candidate_intersections':intersections(q,h,True)}
    assert not missing
    if name=='cliff_crown':
        origin=np.array(cat[name]['position']);front=[];ridge=[];native={}
        for c in controls['assets'][name]['upper_controls']:
            if c['row'] not in ('front','ridge'):continue
            target=np.array(c['actual_world_xyz'])-origin;i=int(np.argmin(np.linalg.norm(p-target,axis=1)));assert np.linalg.norm(p[i]-target)<1e-4;j=int(np.argmin(np.linalg.norm(q-expected[i],axis=1)));native[(c['row'],c['k'])]=j
        shelf=[];profiles=[]
        for k in range(8):
            a=native[('front',k)];b=native[('ridge',k)];target=q[a]*.38+q[b]*.62;linear_y=target[1];target[1]=min(q[a,1]+[2,3,2.5,3.5,2.5,2,1.5,1][k],q[b,1]-.5);i=int(np.argmin(np.linalg.norm(q-target,axis=1)));assert np.linalg.norm(q[i]-target)<1e-4 and i in added;shelf.append(i)
            lower=q[i]-q[a];upper=q[b]-q[i];profiles.append({'column':k,'new_point_glb_xyz':q[i].tolist(),'below_linearly_interpolated_y_m':float(linear_y-q[i,1]),'lower_width_xz_m':float(np.linalg.norm(lower[[0,2]])),'lower_rise_m':float(lower[1]),'lower_profile_slope_degrees':float(np.degrees(np.arctan2(lower[1],np.linalg.norm(lower[[0,2]])))),'upper_profile_slope_degrees':float(np.degrees(np.arctan2(upper[1],np.linalg.norm(upper[[0,2]])))),'peak_ridge_same_as_production':bool(np.min(np.linalg.norm(p-q[b],axis=1))<1e-5)})
        normal,area=normals(q,h);shelf_set=set(shelf);front_set={native[('front',k)] for k in range(8)};ridge_set={native[('ridge',k)] for k in range(8)};groups={}
        for label,first,second in [('lower_grass',front_set,shelf_set),('upper_rock',shelf_set,ridge_set)]:
            faces=[]
            for i,face in enumerate(h):
                ids=set(face)
                if ids<=first|second and ids&first and ids&second:
                    faces.append({'candidate_face':i,'normal_y':float(normal[i,1]),'slope_degrees_from_horizontal':float(np.degrees(np.arccos(np.clip(normal[i,1],-1,1)))),'area_m2':float(area[i]),'color_linear':nc[i].tolist()})
            groups[label]=faces
        entry.update(shelf_profiles=profiles,actual_strip_triangles=groups)
        print('shelf',json.dumps(profiles),flush=True);print('grass angles',[round(z['slope_degrees_from_horizontal'],2) for z in groups['lower_grass']],flush=True)
    report['assets'][name]=entry;print(name,entry['candidate_geometry'],'rim',entry['rim_exactly_same_as_production'],'floor',entry['floor_exactly_same_as_production'],'added',len(added),'intersections',entry['candidate_intersections']['nonadjacent_triangle_crossings'],flush=True)
(ROOT/'reviews/round-16b-independent-geometry-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
