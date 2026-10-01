"""Static61 data and tiny inherited60 template; never run or save the world."""
from pathlib import Path
import json,re,hashlib,numpy as np
D=Path(__file__).resolve().parent;R=D.parents[1];P=R/'candidates/round40-exclusive-20260930/project';S=R/'source-assets/coast57/revision-b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=P/'scenes/candidate53d-west/Game53dWest.tscn';text=source.read_text();blocks=re.split(r'\n(?=\[(?:node|sub_resource|ext_resource) )',text);resources={};nodes={};siblings={}
for block in blocks:
 m=re.match(r'\[sub_resource type="([^"]+)" id="([^"]+)"',block)
 if m:resources[m[2]]=block
 m=re.match(r'\[node name="([^"]+)"[^\n]* parent="([^"]+)"',block)
 if m:
  parent,name=m[2],m[1];path=parent+'/'+name if parent!='.' else name;index=siblings.get(parent,0);siblings[parent]=index+1;nodes[path]=(block,index)
rows=json.loads((S/'scatter-replacements-seated.json').read_text());scope=json.loads((S/'placement-scope57b.json').read_text());allowed_xz={(r['node'],r['index']) for r in scope['relocations']};groups={}
for row in rows:groups.setdefault(row['node'],[]).append(row)
out={};changes={};slot_counts={'x':0,'y':0,'z':0}
for path,entries in groups.items():
 block,index=nodes[path];rid=re.search(r'multimesh = SubResource\("([^"]+)"\)',block)[1];resource=resources[rid]
 values=np.fromstring(re.search(r'buffer = PackedFloat32Array\(([^)]+)\)',resource)[1],sep=',',dtype=np.float32);count=int(re.search(r'instance_count = (\d+)',resource)[1]);assert len(values)==count*12
 rowout={'buffer':values.tolist(),'float32_sha256':hashlib.sha256(values.tobytes()).hexdigest(),'instance_count':count,'node_index':index,'resource_id':rid,'changed_rows':[]}
 for row in entries:
  i=row['index'];before=np.array(row['before_buffer'],np.float32);after=np.array(row['candidate_buffer'],np.float32);assert values[i*12:i*12+12].tobytes()==before.tobytes()
  slots=np.flatnonzero(before!=after).tolist();assert set(slots)<={3,7,11}
  if 3 in slots or 11 in slots:assert (path,i) in allowed_xz
  for slot in slots:slot_counts[{3:'x',7:'y',11:'z'}[slot]]+=1
  if slots:rowout['changed_rows'].append({'index':i,'changed_slots':slots,'before_buffer':before.tolist(),'after_buffer':after.tolist()})
 out[path]=rowout
 if rowout['changed_rows']:changes[path]=rowout
assert len(rows)==60 and len(changes)==4 and sum(len(g['changed_rows']) for g in changes.values())==40 and len(allowed_xz)==7
(D/'static-multimesh-authority.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
lines=['[gd_scene load_steps=8 format=3]','','[ext_resource type="PackedScene" path="res://scenes/candidate60-observation/Game60Observation.tscn" id="1_base"]','[ext_resource type="ArrayMesh" path="res://assets/coast61/Ground_-5_-5_coast61.mesh" id="2_mesh"]','[ext_resource type="Shape3D" path="res://assets/coast61/Ground_-5_-5_coast61_collision.res" id="3_shape"]']
for i,path in enumerate(changes,4):lines.append(f'[ext_resource type="MultiMesh" path="res://assets/coast61/{path.rsplit("/",1)[1]}.res" id="{i}_scatter"]')
lines+=['','[node name="Skyfarer" instance=ExtResource("1_base")]','','[node name="Ground_-5_-5" parent="World/Terrain/Ground_-5_-5/Model" index="0"]','mesh = ExtResource("2_mesh")','','[node name="Shape" parent="World/Terrain/Ground_-5_-5/Collision" index="0"]','shape = ExtResource("3_shape")']
for i,path in enumerate(changes,4):lines+=['',f'[node name="{path.rsplit("/",1)[1]}" parent="World/Vegetation" index="{nodes[path][1]}"]',f'multimesh = ExtResource("{i}_scatter")']
(D/'Game61Coast.tscn.template').write_text('\n'.join(lines)+'\n')
native=json.loads((S/'native-authority/authority.json').read_text());candidate=json.loads((S/'candidate-native.json').read_text());idx=np.array(native['surfaces'][0]['arrays'][12],np.int32).reshape(-1,3);changed=set(candidate['changed_triangle_indices']);mapping=[];cursors=[0,0]
for face in range(len(idx)):
 surf=int(face in changed);mapping.append({'source_triangle':face,'surface':surf,'surface_triangle':cursors[surf],'source_vertex_indices':idx[face].tolist()});cursors[surf]+=1
used=set(idx[[i for i in range(len(idx)) if i not in changed]].ravel().tolist());unused=sorted(set(range(len(native['surfaces'][0]['arrays'][0])))-used)
(D/'surface-triangle-map.json').write_text(json.dumps({'triangle_mapping':mapping,'surface0_vertex_count':8264,'surface0_drawn_triangles':2111,'surface0_unused_original_vertex_indices':unused,'surface1_drawn_triangles':759,'source_lods_stored':'"lods"' in resources['ArrayMesh_5ypxy'],'source_shadow_mesh_stored':'shadow_mesh' in resources['ArrayMesh_5ypxy']},separators=(',',':'))+'\n')
files=[source,P/'project.godot',S/'candidate-native.json',S/'scatter-replacements-seated.json',S/'native-authority/authority.json',S/'verified-saved57b.json',S/'placement-scope57b.json',S/'source-result57b.json',S/'diagnostics-foot57b/prop-foot-geometry.json',S/'diagnostics-foot57b/continuous-foot-support57b.json',S/'diagnostics-foot57b/visible-geometry57b.json',S/'foot_geometry57b.py',S/'visible_geometry_core57b.py',D/'static-multimesh-authority.json',D/'surface-triangle-map.json',D/'Game61Coast.tscn.template',P/'scripts/open_world.gd',P/'scripts/game55_observation.gd',P/'assets/observation55/lake_observation_poses.json',P/'tools/reflection51b_saved_audit.gd']
# Existing56 resources are always protected;60 is sealed separately only after its
# independent actual scope/runtime gate is delivered. A present file is not that gate.
lineage=json.loads((S/'lineage.json').read_text())
files+= [R/path for path in lineage['immutable_project_files'] if (R/path) not in files]
manifest={'source_world_sha256':sha(source),'base':'res://scenes/candidate60-observation/Game60Observation.tscn','candidate':'res://scenes/candidate61-coast/Game61Coast.tscn','mesh_target':'World/Terrain/Ground_-5_-5/Model/Ground_-5_-5','shape_target':'World/Terrain/Ground_-5_-5/Collision/Shape','changed_groups':list(changes),'changed_root_count':40,'changed_component_counts':slot_counts,'checked_roots':60,'checked_groups':4,'full_group_instance_count':sum(g['instance_count'] for g in out.values()),'XZ_relocation_count':7,'template_bytes':(D/'Game61Coast.tscn.template').stat().st_size,'surface0_unused_vertex_count':len(unused),'immutable_inputs':{str(p):sha(p) for p in files},'base60_runtime_gate_required':True,'renderer_executed':False,'build_executed':False,'scope':'Static preparation only. Build requires independently verified and fixed60 base gate; no existing world/default edits.'}
(D/'preparation-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
gate=D/'base60-gate.json'
if not gate.exists():gate.write_text(json.dumps({'ready':False,'reason':'Await fixed60 scene/script/pose hashes and actual scope/runtime terminal gate from its completed validation','base_scene':'res://scenes/candidate60-observation/Game60Observation.tscn','required_reports':[],'immutable_inputs':{}},indent=2)+'\n')
print(json.dumps({k:v for k,v in manifest.items() if k!='immutable_inputs'},indent=2))
