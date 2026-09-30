from pathlib import Path
import ast,json,re,struct,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1]
RUN=R/'captures/validation_runs/highcoast-36b-20260909T015215Z-0c71bb650bcf43d890987772791f1dff'
N=R/'captures/candidate_highcoast36c'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def text(p):return p.read_text(encoding='utf-8-sig')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parser=text(R/'reviews/36-highcoast-occupancy-intake.py');tree=ast.parse(parser)
cls=ast.get_source_segment(parser,next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='MultiReader'))
cls=cls.replace('assert len(internals)==1;self.i=internals[0][1]','self.internal_table=internals;self.i=internals[-1][1]')
cls=cls.replace('assert sub==3,sub','if sub==2:\n                index=self.u32();return dict(path="embedded_internal://"+str(index),internal_table=self.internal_table)\n            assert sub==3,sub')
exec(cls,globals())
s=text(N/'World36c.tscn')
ext={i:dict(type=t,path=p) for t,p,i in re.findall(r'^\[ext_resource type="([^"]+)" path="([^"]+)" id="([^"]+)"\]',s,re.M)}
sections=re.split(r'(?m)(?=^\[)',s)
subs={re.search(r'id="([^"]+)"',x)[1]:x for x in sections if x.startswith('[sub_resource')}
nodes=[x for x in sections if x.startswith('[node')]
def attrs(header):return dict(re.findall(r'(\w+)="([^"]*)"',header))
def reference(line):
    kind,id=re.search(r'(Ext|Sub)Resource\("([^"]+)"\)',line).groups();return kind,id
cache={}
def resource(kind,id):
    key=(kind,id)
    if key in cache:return cache[key]
    if kind=='Ext':
        p=R/ext[id]['path'].removeprefix('res://');m=MultiReader(p);out=dict(count=len(m.transforms),transforms=m.transforms,path=ext[id]['path'])
    else:
        body=subs[id];cm=re.search(r'^instance_count = (\d+)',body,re.M);count=int(cm[1]) if cm else 0;m=re.search(r'^buffer = PackedFloat32Array\((.*?)\)',body,re.M)
        v=np.fromstring(m[1],sep=',',dtype=np.float32).reshape(-1,3,4) if m else np.empty((0,3,4),np.float32)
        assert len(v)==count
        out=dict(count=count,transforms=v,path='embedded:'+id)
    cache[key]=out;return out
groves={};counts=[];helpers=[]
for node in nodes:
    a=attrs(node.splitlines()[0])
    if a.get('parent')!='Vegetation':continue
    key=reference(re.search(r'^multimesh = (.*)',node,re.M)[1]);res=resource(*key);groves[a['name']]=(node,res)
    counts.append(dict(name=a['name'],count=res['count'],resource=res['path']))
    if a['name'].endswith('_CoastalPines36b'):
        script=reference(re.search(r'^script = (.*)',node,re.M)[1]);model=reference(re.search(r'^model_scene = (.*)',node,re.M)[1])
        helpers.append(dict(name=a['name'],script=ext[script[1]]['path'],model_scene=ext[model[1]]['path'],owner_attribute=a.get('owner'),owner_semantics='No explicit owner means scene root in this saved flat node declaration; natural reload owner must be checked by root process.',metadata_pine='metadata/asset_kind = "pine"' in node))
side=read(RUN/'images/alongshore-high.png.json');removals=side['harbor_study']['stone_paths']['vegetation_adjustments'];changes=[]
for row in removals:
    name=row['node'].split('/')[-1];node,res=groves[name];old=MultiReader(RUN/'images/native-scenes'/(name+'.res')).transforms
    indices=[r['index'] for r in row['removed_from_temporary_copy']];expected=np.delete(old,indices,axis=0);actual=res['transforms']
    tr=np.fromstring(re.search(r'^transform = Transform3D\((.*?)\)',node,re.M)[1],sep=',');basis=tr[:9].reshape(3,3).T;origin=tr[9:]
    positions=[(basis@old[i,:,3]+origin).tolist() for i in indices]
    changes.append(dict(name=name,old_adapter_count=len(old),saved_candidate_count=len(actual),removed_indices=indices,expected_remaining_shape_matches=actual.shape==expected.shape,all_remaining_rows_float32_exact=bool(np.array_equal(actual,expected)),max_remaining_component_delta=float(np.max(np.abs(actual-expected))),removed_world_positions_actual=positions,recorded_removals=row['removed_from_temporary_copy'],max_removed_position_record_error_m=max(float(np.max(np.abs(np.array(p)-q['position']))) for p,q in zip(positions,row['removed_from_temporary_copy']))))
repair=read(N/'repair-report.json');repair_checks=[]
for row in repair['records']:
    original=text(R/row['source']);actual=text(R/row['output']);expected=original
    for c in row['changes']:
        before=c['before'].replace(chr(92),chr(92)*2) if c['kind']=='weather_folder' else c['before']
        expected=expected.replace(before,c['after'])
    repair_checks.append(dict(output=row['output'],source_sha_matches=sha(R/row['source'])==row['source_sha256'],output_sha_matches=sha(R/row['output'])==row['sha256'],only_declared_text_replacements=expected==actual,changes=len(row['changes'])))
roots=[attrs(n.splitlines()[0]) for n in nodes if attrs(n.splitlines()[0]).get('parent')=='.']
tiles=[]
for n in nodes:
    a=attrs(n.splitlines()[0])
    if a.get('parent')!='Terrain':continue
    if 'instance=ExtResource' not in n.splitlines()[0]:continue
    kind,id=reference(n.splitlines()[0]);p=ext[id]['path']
    if '/highcoast-36b-' not in p:continue
    t=text(R/p.removeprefix('res://'));tiles.append(dict(name=a['name'],resource=p,exists=(R/p.removeprefix('res://')).exists(),required_fields=all(token in t for token in ['scripts/asset_instance.gd','name="Model"','name="Collision"','name="Shape"','surface_material =','collision_layer = 5','collision_mask = 2','type="ConcavePolygonShape3D"'])))
report=dict(scope='36c read-only saved candidate count, three known removals, persistent-node contracts and path repair. No engine/Blender/GPU or repeated terrain/support tests.36g pending.',world_path=str((N/'World36c.tscn').relative_to(R)),world_sha256=sha(N/'World36c.tscn'),game_sha256=sha(N/'Game36c.tscn'),repair_checks=repair_checks,saved_vegetation=dict(groups=len(counts),total=sum(g['count'] for g in counts),counts=counts,method='Read actual referenced external MultiMesh resources and embedded count/buffer fields; only two affected groups receive row-delta comparison.'),known_removed_instances=changes,adapter_stage_total=54800,complete_saved_candidate_total=sum(g['count'] for g in counts),difference=54800-sum(g['count'] for g in counts),direct_world_children=roots,temporary_root_collision_bodies=[r for r in roots if r.get('type') in ['StaticBody3D','CollisionShape3D']],changed_tile_contracts=tiles,new_pine_helpers=helpers,checks=dict(saved_total_54797=sum(g['count'] for g in counts)==54797,exact_three_known_removals=sum(len(x['removed_indices']) for x in changes)==3 and all(x['all_remaining_rows_float32_exact'] and x['max_removed_position_record_error_m']<.002 for x in changes),no_temporary_root_bodies=all(r.get('type') not in ['StaticBody3D','CollisionShape3D'] for r in roots),fourteen_tile_contracts=len(tiles)==14 and all(x['required_fields'] for x in tiles),pine_helpers=all(x['script']=='res://scripts/scatter_group.gd' and x['model_scene']=='res://scenes/prefabs/pine.tscn' and x['metadata_pine'] for x in helpers),declared_path_repairs_only=all(x['source_sha_matches'] and x['output_sha_matches'] and x['only_declared_text_replacements'] for x in repair_checks)),native_fresh_reload_proven=False,overall_candidate_accepted=False,visual_accepted=False,full_reference_accepted=False,limits=['TSCN owner semantics inspected statically; actual instantiated owner and tool button interaction await root36g.','54797 is complete savedWorld after3 later harbor-road removals;54800 remains correct only for preceding highcoast adapter stage.','No fullfoot or vehicle corridor claim; prior36b technical/run failure retained.'])
(R/'reviews/36c-candidate-native-independent.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(checks=report['checks'],groups=len(counts),total=report['complete_saved_candidate_total'],changes=changes,pine_helpers=len(helpers),repair_checks=repair_checks),ensure_ascii=False))
