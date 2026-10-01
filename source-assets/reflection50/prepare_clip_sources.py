#!/usr/bin/env python3
"""Strict exact-source clip-only insertion ledger. Never writes prior scene/materials."""
from pathlib import Path
import json,re,hashlib,difflib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent/'clip-sources';OUT.mkdir(exist_ok=True)
plan=json.loads((ROOT/'cloud-evidence/reflection50-material-intake/reflection50-binding-scope.json').read_text())
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
HEADER='\n// BEGIN REFLECTION50 CLIP DECLARATIONS\nuniform bool lake50_clip_enabled=false;\nvarying float reflection_world_y50;\n// END REFLECTION50 CLIP DECLARATIONS\n'
ASSIGN='\n    // BEGIN REFLECTION50 FINAL VERTEX WORLD Y\n    reflection_world_y50=(MODEL_MATRIX*vec4(VERTEX,1.0)).y;\n    // END REFLECTION50 FINAL VERTEX WORLD Y\n'
FRAGMENT='\n    // BEGIN REFLECTION50 CAMERA-ONLY CLIP\n    if(lake50_clip_enabled && (CAMERA_VISIBLE_LAYERS & 524288u)!=0u && reflection_world_y50<0.0){discard;}\n    // END REFLECTION50 CAMERA-ONLY CLIP\n'
def cleaned(s):
 # Replace comments with spaces without changing offsets/line breaks.
 return re.sub(r'/\*.*?\*/|//[^\r\n]*',lambda m:''.join('\n' if c=='\n' else ' ' for c in m[0]),s,flags=re.S)
def function_span(code,name):
 view=cleaned(code);matches=list(re.finditer(r'\bvoid\s+'+name+r'\s*\(\s*\)\s*\{',view))
 assert len(matches)<=1,(name,'ambiguous',len(matches))
 if not matches:return None
 begin=matches[0].end()-1;depth=1;i=begin+1
 while depth:
  assert i<len(view),'unbalanced'
  if view[i]=='{':depth+=1
  elif view[i]=='}':depth-=1
  i+=1
 return begin,i-1
codes={}
for g in plan['shader_groups']+plan['stream_authorities']:
 assert sha(g['shader_code'])==g['shader_sha256'];codes[g['shader_sha256']]={'code':g['shader_code'],'kind':'existing_shader'}
conversion=ROOT/'source-assets/reflection50/official-native-conversions'
for row in json.loads((conversion/'conversion-manifest.json').read_text())+json.loads((conversion/'conversion-manifest-group04.json').read_text()):
 code=(conversion/f"native_group_{row['group']:02d}.gdshader").read_text(newline='') if False else (conversion/f"native_group_{row['group']:02d}.gdshader").open(newline='').read()
 assert sha(code)==row['shader_sha256'];codes[sha(code)]={'code':code,'kind':'official_native_template','group':row['group'],'official_material_sha256':row['material_sha256']}
ledger=[]
for original_sha,entry in codes.items():
 code=entry['code'];view=cleaned(code)
 for forbidden in ['world_vertex_coords','skip_vertex_transform','POSITION']:
  assert not re.search(r'\b'+forbidden+r'\b',view),(original_sha,'needs dedicated transform handling',forbidden)
 assert 'lake50_clip_enabled' not in code
 vertex=function_span(code,'vertex');fragment=function_span(code,'fragment');assert fragment
 inserts=[]
 declared=re.search(r'\bshader_type\s+spatial\s*;',view);assert declared
 inserts.append((declared.end(),HEADER))
 vertex_body=code[vertex[0]+1:vertex[1]] if vertex else ''
 if vertex:
  assert not re.search(r'\breturn\b',cleaned(vertex_body)),(original_sha,'early vertex return would bypass final worldY')
  inserts.append((vertex[1],ASSIGN))
 else:inserts.append((len(code),'\nvoid vertex(){'+ASSIGN+'}\n'))
 inserts.append((fragment[0]+1,FRAGMENT))
 result=code
 for pos,text in sorted(inserts,reverse=True):result=result[:pos]+text+result[pos:]
 # Removing only precisely registered insertions recovers the original bytes.
 recovered=result
 for _,text in inserts:
  assert recovered.count(text)==1;recovered=recovered.replace(text,'',1)
 if not vertex:
  recovered=recovered.replace('\nvoid vertex(){}\n','',1)
 # Above synthesized vertex insertion was one full block already, no extra removal.
 assert recovered==code,(original_sha,'non-insertion changes')
 path=OUT/(original_sha+'.gdshader');assert not path.exists(),'Preserve earlier generated source, do not overwrite'
 path.write_text(result,newline='')
 row={k:v for k,v in entry.items() if k!='code'};row.update({'source_sha256':original_sha,'copy_sha256':sha(result),'output_path':str(path),'original_code':code,'copied_code':result,'insertion_only_roundtrip_exact':True,'vertex_existing':vertex is not None,'original_vertex_body':vertex_body,'vertex_world_y_position':'Final vertex body statement, after original VERTEX displacement','unsupported_render_modes_absent':True,'vertex_early_return_absent':True,'diff':''.join(difflib.unified_diff(code.splitlines(True),result.splitlines(True),fromfile=original_sha,tofile=sha(result)))})
 ledger.append(row)
output=OUT/'shader-injection-ledger.json';assert not output.exists();output.write_text(json.dumps({'clip_uniform':'lake50_clip_enabled','varying':'reflection_world_y50','marker_bit':524288,'old_shader_unique_count':8,'official_template_count':4,'shaders':ledger},indent=2))
print('Verified and generated',len(ledger),'exact insertion-only shader copies')
