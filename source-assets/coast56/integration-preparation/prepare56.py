"""Prepare static authority and the tiny inherited scene template. Never launch a renderer."""
import re,json,numpy as np,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];P=R/'candidates/round40-exclusive-20260930/project';S=D.parent
source=P/'scenes/candidate53d-west/Game53dWest.tscn';text=source.read_text();blocks=re.split(r'\n(?=\[(?:node|sub_resource|ext_resource) )',text);resources={};nodes={};siblings={}
for block in blocks:
 match=re.match(r'\[sub_resource type="([^"]+)" id="([^"]+)"',block)
 if match:resources[match[2]]=block
 match=re.match(r'\[node name="([^"]+)"[^\n]* parent="([^"]+)"',block)
 if match:
  parent,name=match[2],match[1];path=parent+'/'+name if parent!='.' else name
  index=siblings.get(parent,0);siblings[parent]=index+1;nodes[path]=(block,index)
rows=json.loads((S/'scatter-replacements.json').read_text());groups={}
for row in rows:groups.setdefault(row['node'],[]).append(row)
out={};changes={}
for path,entries in groups.items():
 block,index=nodes[path];rid=re.search(r'multimesh = SubResource\("([^"]+)"\)',block)[1];resource=resources[rid]
 values=np.fromstring(re.search(r'buffer = PackedFloat32Array\(([^)]+)\)',resource)[1],sep=',').astype(np.float32);count=int(re.search(r'instance_count = (\d+)',resource)[1]);assert len(values)==count*12
 out[path]={'buffer':values.tolist(),'float32_sha256':hashlib.sha256(values.tobytes()).hexdigest(),'instance_count':count,'node_index':index,'resource_id':rid,'changed_rows':[]}
 for row in entries:
  i=row['index'];assert np.array_equal(values[i*12:i*12+12],np.asarray(row['before_buffer'],np.float32))
  if row['before_buffer']!=row['candidate_buffer']:
   before=np.asarray(row['before_buffer'],np.float32);after=np.asarray(row['candidate_buffer'],np.float32);assert np.flatnonzero(before!=after).tolist()==[7]
   out[path]['changed_rows'].append({'index':i,'before_y':row['before_buffer'][7],'after_y':row['candidate_buffer'][7]})
 if out[path]['changed_rows']:changes[path]=out[path]
assert len(changes)==4 and sum(len(v['changed_rows']) for v in changes.values())==29
(D/'static-multimesh-authority.json').write_text(json.dumps(out,separators=(',',':')))
lines=['[gd_scene load_steps=8 format=3]','','[ext_resource type="PackedScene" path="res://scenes/candidate55-observation/Game55Observation.tscn" id="1_base"]','[ext_resource type="ArrayMesh" path="res://assets/coast56/Ground_-4_-4_coast56.mesh" id="2_mesh"]','[ext_resource type="Shape3D" path="res://assets/coast56/Ground_-4_-4_coast56_collision.res" id="3_shape"]']
for i,path in enumerate(changes,4):lines.append(f'[ext_resource type="MultiMesh" path="res://assets/coast56/{path.rsplit("/",1)[1]}.res" id="{i}_scatter"]')
lines+=['','[node name="Skyfarer" instance=ExtResource("1_base")]','','[node name="Ground_-4_-4" parent="World/Terrain/Ground_-4_-4/Model" index="0"]','mesh = ExtResource("2_mesh")','','[node name="Shape" parent="World/Terrain/Ground_-4_-4/Collision" index="0"]','shape = ExtResource("3_shape")']
for i,path in enumerate(changes,4):lines+=['',f'[node name="{path.rsplit("/",1)[1]}" parent="World/Vegetation" index="{nodes[path][1]}"]',f'multimesh = ExtResource("{i}_scatter")']
(D/'Game56Coast.tscn.template').write_text('\n'.join(lines)+'\n')
files=[source,P/'scenes/candidate55-observation/Game55Observation.tscn',P/'project.godot',S/'candidate-native.json',S/'scatter-replacements.json',S/'native-authority/authority.json',S/'verified-static56.json',D/'static-multimesh-authority.json',D/'Game56Coast.tscn.template',P/'scripts/open_world.gd',P/'scripts/game55_observation.gd',P/'tools/reflection51b_saved_audit.gd']
manifest={'source_world_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'base':'res://scenes/candidate55-observation/Game55Observation.tscn','candidate':'res://scenes/candidate56-coast/Game56Coast.tscn','mesh_target':'World/Terrain/Ground_-4_-4/Model/Ground_-4_-4','shape_target':'World/Terrain/Ground_-4_-4/Collision/Shape','changed_groups':list(changes),'changed_slots':29,'checked_roots':44,'checked_groups':6,'template_bytes':(D/'Game56Coast.tscn.template').stat().st_size,'immutable_inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'renderer_executed':False,'build_executed':False,'scope':'Preparation and parse only; no generated world resources or target scene yet'}
native=json.loads((S/'native-authority/authority.json').read_text());candidate=json.loads((S/'candidate-native.json').read_text());idx=np.asarray(native['surfaces'][0]['arrays'][12],np.int32).reshape(-1,3);changed=set(candidate['changed_triangle_indices']);mapping=[];cursors=[0,0]
for face in range(len(idx)):
 surface=int(face in changed);mapping.append({'source_triangle':face,'surface':surface,'surface_triangle':cursors[surface],'source_vertex_indices':idx[face].tolist()});cursors[surface]+=1
used=set(idx[[i for i in range(len(idx)) if i not in changed]].ravel().tolist());unused=sorted(set(range(len(native['surfaces'][0]['arrays'][0])))-used)
mapfile=D/'surface-triangle-map.json';mapfile.write_text(json.dumps({'triangle_mapping':mapping,'surface0_vertex_count':9423,'surface0_drawn_triangles':2665,'surface0_unused_original_vertex_indices':unused,'surface1_drawn_triangles':533,'source_lods_stored':('"lods"' in resources['ArrayMesh_136tc']),'source_shadow_mesh_stored':('shadow_mesh' in resources['ArrayMesh_136tc'])},separators=(',',':')))
manifest['immutable_inputs'][str(mapfile)]=hashlib.sha256(mapfile.read_bytes()).hexdigest();manifest['surface0_unused_vertex_count']=len(unused)
(D/'preparation-manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps({k:v for k,v in manifest.items() if k!='immutable_inputs'},indent=2))
