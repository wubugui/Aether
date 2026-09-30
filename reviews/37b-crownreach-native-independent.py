from pathlib import Path
import ast,re,json,struct,hashlib
from collections import Counter
import numpy as np
from scipy.spatial import cKDTree
R=Path(__file__).resolve().parents[1];N=R/'captures/crownreach_study_37b';A=R/'captures/crownreach_study_37a'
RUN=R/'captures/validation_runs/crownreach37b-20260909T033100Z-fd503709954645d3a7e601e40b8f4cd6';I=RUN/'images'
def text(p):return p.read_text(encoding='utf-8-sig')
def read(p):return json.loads(text(p))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
decoder=text(R/'reviews/round-32b-asset-footprint-decoder.py')
decoder=decoder.replace('def asset_world_triangles(path):','def named_triangles(path):').replace('tris=[]','tris={}; current=[]').replace("if 'mesh' in node:\n   for prim", "if 'mesh' in node:\n   current=[]\n   for prim").replace('tris.extend(x[ix])','current.extend(x[ix])').replace("  for j in node.get('children',[]):", "   tris[node['name']]=np.array(current)\n  for j in node.get('children',[]):").replace('return np.array(tris)','return tris')
exec(decoder,globals())
old=named_triangles(A/'castle.glb');new=named_triangles(N/'castle.glb');plan=read(N/'model-report.json');runtime=read(I/'castle37b.json');manifest=read(RUN/'manifest.json')
declared={x['name'] for x in plan['changes']};unchanged=[];changed=[];edit_checks=[]
def tri_counter(t,decimals=5):
    return Counter(tuple(sorted(tuple(p) for p in tri)) for tri in np.round(t,decimals))
for name,t in old.items():
    u=new[name]
    same=np.array_equal(t,u)
    (unchanged if same else changed).append(name)
    if name in declared:
        expected=t.copy()
        if name.startswith('Courtyard paving'):expected[:,:,2][expected[:,:,2]<.68]-=1
        else:expected[:,:,0]=-14+(expected[:,:,0]-1.2)*.65;expected[:,:,1]+=17.8
        # Vertex multiset accommodates export re-triangulation of planar n-gons.
        ev=np.unique(np.round(expected.reshape(-1,3),5),axis=0);uv=np.unique(np.round(u.reshape(-1,3),5),axis=0)
        distance=cKDTree(ev).query(uv)[0];reverse=cKDTree(uv).query(ev)[0]
        edit_checks.append(dict(name=name,expected_vertex_set_max_error_m=float(max(distance.max(),reverse.max())),triangles_before=len(t),triangles_after=len(u),triangulation_counter_matches_expected=tri_counter(expected)==tri_counter(u)))
added=sorted(set(new)-set(old));alltris=np.concatenate(list(new.values()))
godot=alltris[:,:,[0,2,1]]*np.array([1,1,-1])
native=text(I/'castle37b.tscn');raw=re.search(r'^data = PackedVector3Array\((.*?)\)',native,re.M)[1];collision=np.fromstring(raw,sep=',').reshape(-1,3,3)
points=np.unique(godot.reshape(-1,3),axis=0);tree=cKDTree(points);_,gi=tree.query(godot.reshape(-1,3));cd,ci=tree.query(collision.reshape(-1,3))
indices=lambda a:Counter(tuple(sorted(map(int,t))) for t in a.reshape(-1,3))
collision_check=dict(glb_parts=len(new),glb_triangles=len(alltris),saved_collision_triangles=len(collision),saved_collision_nearest_glb_vertex_max_error_m=float(cd.max()),actual_triangle_correspondence=indices(gi)==indices(ci),runtime_triangles_match=runtime['collision_triangles']==len(collision),runtime612parts_count_matches=len(runtime['mesh_parts'])==len(new),note='Decode GLB hierarchy and actual saved Concave faces; nearest unique vertex mapping plus unordered triangle multiplicities. Imported finite precision is measured, not byte-exact positions.')

# Resolve resource IDs semantically; reserialization may rename Ext/Sub IDs.
class Scene:
 def __init__(self,path):
  self.path=path;self.s=text(path);sections=re.split(r'(?m)(?=^\[)',self.s)
  self.ext={};self.sub={};self.nodes={};self.cache={}
  for section in sections:
   header=section.splitlines()[0];body='\n'.join(section.splitlines()[1:]).strip();a=dict(re.findall(r'(\w+)="([^"]*)"',header))
   if header.startswith('[ext_resource'):self.ext[a['id']]=a
   elif header.startswith('[sub_resource'):self.sub[a['id']]=(a['type'],body)
   elif header.startswith('[node'):
    key=(a.get('parent','ROOT')+'/'+a['name']).removeprefix('./');self.nodes[key]=(header,body,a)
 def resolve(self,kind,id):
  key=(kind,id)
  if key in self.cache:return self.cache[key]
  if kind=='Ext':value='EXT:'+self.ext[id]['type']+':'+self.ext[id]['path']
  else:
   t,b=self.sub[id];value='SUB:'+t+':'+hashlib.sha256(self.norm(b).encode()).hexdigest()
  self.cache[key]=value;return value
 def norm(self,s):return re.sub(r'(Ext|Sub)Resource\("([^"]+)"\)',lambda m:self.resolve(*m.groups()),s)
 def node(self,key):
  h,b,a=self.nodes[key];return self.norm(h+'\n'+b)
before=Scene(R/'captures/candidate_highcoast36c/World36c.tscn');after=Scene(I/'World37b.tscn');game=Scene(I/'Game37b.tscn')
castlekey='Settlements/castle_57174';iscastle=lambda k:k==castlekey or k.startswith(castlekey+'/')
outside_added=[k for k in after.nodes.keys()-before.nodes.keys() if not iscastle(k)];outside_removed=[k for k in before.nodes.keys()-after.nodes.keys() if not iscastle(k)]
outside_changed=[k for k in before.nodes.keys()&after.nodes.keys() if not iscastle(k) and before.node(k)!=after.node(k)]
orchardkey='Vegetation/Authored_CitadelOrchard'
def mm(scene,key):
 h,b,a=scene.nodes[key];kind,id=re.search(r'^multimesh = (Ext|Sub)Resource\("([^"]+)"\)',b,re.M).groups()
 if kind=='Sub':
  t,b=scene.sub[id];count=int(re.search(r'^instance_count = (\d+)',b,re.M)[1]);v=np.fromstring(re.search(r'^buffer = PackedFloat32Array\((.*?)\)',b,re.M)[1],sep=',',dtype=np.float32).reshape(-1,3,4)
  return v
 parser=text(R/'reviews/36-highcoast-occupancy-intake.py');cls=ast.get_source_segment(parser,next(n for n in ast.parse(parser).body if isinstance(n,ast.ClassDef) and n.name=='MultiReader'));exec(cls,globals());return MultiReader(R/scene.ext[id]['path'].removeprefix('res://')).transforms
ov=mm(before,orchardkey);nv=mm(after,orchardkey);row=runtime['scatter_changes'][0];removed=[v['index'] for v in row['removed']];expected=np.delete(ov,removed,axis=0)
tr=np.fromstring(re.search(r'^transform = Transform3D\((.*?)\)',before.nodes[orchardkey][1],re.M)[1],sep=',');basis=tr[:9].reshape(3,3).T;origin=tr[9:];actual_positions=[(basis@ov[i,:,3]+origin).tolist() for i in removed]
root_bodies=[a for h,b,a in after.nodes.values() if a.get('parent')=='.' and a.get('type')=='StaticBody3D']
orchard=dict(old_count=len(ov),new_count=len(nv),removed_indices=removed,remaining_rows_float32_exact=np.array_equal(expected,nv),removed_actual_world_positions=actual_positions,removed_positions_max_record_error_m=max(float(np.max(np.abs(np.array(p)-v['position']))) for p,v in zip(actual_positions,row['removed'])),all_other_world_node_resource_semantics_same=outside_changed==[orchardkey] and not outside_added and not outside_removed,other_changed_nodes=outside_changed,other_added_nodes=outside_added,other_removed_nodes=outside_removed,final_savedWorld_total_by_inherited773groups=54797-len(removed),scope='No wholesale resource rescan: prior World36c54797 plus exactly one orchard resource16->12; all other node/reference semantics compared.')
bindings=[dict(path=p,sha_matches=sha(RUN/p)==v['sha256'],size_matches=(RUN/p).stat().st_size==v['bytes']) for p,v in manifest['artifacts'].items()]
identity=dict(source37a_sha_matches=sha(A/'castle.blend')==plan['source_sha256'],frozen_assets_match=all(sha(N/p)==sha(RUN/p) for p in ['castle.blend','castle.glb','model-report.json','builder.py']),executed_script_matches=sha(R/'tools/render_crownreach37b.gd')==sha(RUN/'render_crownreach37b.gd'))
gameworld=[(k,h) for k,(h,b,a) in game.nodes.items() if a.get('name')=='World' and a.get('parent')=='.']
worldref=game.norm(gameworld[0][1]);current_orchard=after.nodes[orchardkey]
contract=dict(game_world_reference=worldref,game_world_ref_to_actual37b='World37b.tscn' in worldref,castle_root_transform=after.nodes[castlekey][1],castle_embedded_mesh_node_count=sum(a.get('type')=='MeshInstance3D' and iscastle(k) for k,(h,b,a) in after.nodes.items()),temporary_direct_world_body_count=len(root_bodies),castle_required_paths=all(k in after.nodes for k in [castlekey+'/Model',castlekey+'/Collision',castlekey+'/Collision/Shape']),castle_asset_script_and_material='asset_instance.gd' in after.node(castlekey) and 'surface_material' in after.node(castlekey),orchard_helper_retained='scatter_group.gd' in after.node(orchardkey) and 'model_scene' in current_orchard[1],owner_scope='World plain embedded castle/new nodes owned by scene root via own_boundaries; external instances remain boundaries. Static declarations/source inspected; full fresh Game reload/GUI authoring owner not yet independently executed.')
checks=dict(manifest_passed=manifest['status']=='passed' and manifest['passed'],bindings_match=all(x['sha_matches'] and x['size_matches'] for x in bindings),source_identity=all(identity.values()),source37a_retained_except_declared55= set(changed)==declared and len(changed)==55 and all(x['expected_vertex_set_max_error_m']<.00003 for x in edit_checks),new36pieces_added=len(added)==36,actual612parts26492collision=len(new)==612 and len(collision)==26492 and collision_check['actual_triangle_correspondence'] and cd.max()<.003,only_orchard_four_deletions=orchard['all_other_world_node_resource_semantics_same'] and len(ov)==16 and len(nv)==12 and removed==[0,2,4,8] and orchard['remaining_rows_float32_exact'] and orchard['removed_positions_max_record_error_m']<.0001,native_contract=contract['game_world_ref_to_actual37b'] and contract['castle_required_paths'] and contract['castle_embedded_mesh_node_count']==612 and contract['temporary_direct_world_body_count']==0 and contract['orchard_helper_retained'])
result=dict(scope='Bounded37b native castle, source37a delta, actual derived savedcollision, World36c->37b semantic preservation and orchard4removals. No Blender/Godot/GPU rerun.',run=RUN.name,bindings=bindings,identity=identity,source_delta=dict(old_parts=len(old),new_parts=len(new),unchanged_parts=len(unchanged),changed_names=changed,added_names=added,edit_checks=edit_checks),collision=collision_check,orchard=orchard,native_contract=contract,run_error_log_bytes=(RUN/'castle-native-gpu-error.log').stat().st_size,stage_exit_codes=[s['exit_code'] for s in manifest['stages']],limited_runtime=dict(paving_probes=len(runtime['paving_center_probes']),paving_gap_range_m=[min(p['gap_m'] for p in runtime['paving_center_probes']),max(p['gap_m'] for p in runtime['paving_center_probes'])],gate_rays=runtime['gate_rays'],orbit_camera_steps=len(runtime['orbit_camera_samples']),limits='40 bottom-center probes do not establish entire stone support or contact; gate3line rays not swept collisionbody.25 orbit steps directly set camera with game physics disabled, not physical flight. Game37b saved but not freshly reloaded; visual daytime overrides applied after save so savedGame launch visuals not established by thesePNGs.'),checks=checks,bounded_technical_pass=all(checks.values()),freshGame_reopen_proven=False,overall_candidate_accepted=False,visual_accepted=False,full_reference_accepted=False)
(R/'reviews/37b-crownreach-native-independent.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(checks=checks,delta=[len(old),len(new),len(changed),len(unchanged),len(added)],collision=collision_check,orchard=orchard,contract=contract),ensure_ascii=False))
