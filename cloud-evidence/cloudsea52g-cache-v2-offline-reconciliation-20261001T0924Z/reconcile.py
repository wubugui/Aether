"""Read-only replay of the frozen validator with one precise phase-count repair.
No engine/process invocation; original run, native report and gates stay untouched.
"""
from pathlib import Path
from copy import deepcopy
from datetime import datetime,timezone
import ast,hashlib,json,struct,re
import numpy as np
from PIL import Image
ROOT=Path('/workspace/scratch/a29d03198654/Aether');DEST=Path(__file__).resolve().parent
RUN=ROOT/'cloud-evidence/cloudsea52g-cache-diagnostic-v2-front-20261001T091704Z-5rx_5cuu'
AB=ROOT/'cloud-evidence/cloudsea52g-d-ab-front-20261001T083354Z-3wbcs8h5'
SCENE_SHA='201f667747406b1414a298a6b5433ac1550d8b447dff8f6cb6823d94d2acbd7c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,value):(DEST/name).write_text(json.dumps(value,indent=2)+'\n')
assert DEST!=RUN and not str(DEST).startswith(str(RUN)+'/')
source_files=[p for p in RUN.rglob('*') if p.is_file()]+[AB/'images/report.json',AB/'images/1216-front-A.png',AB/'images/1216-front-A2.png']
before={str(p):sha(p) for p in source_files}
input_hashes=json.loads((RUN/'input-sha256.json').read_text());inputs_exact=all(Path(p).exists() and sha(p)==v for p,v in input_hashes.items())
process=json.loads((RUN/'process-report.json').read_text());original_gate=json.loads((RUN/'external-gate.json').read_text())
contract=json.loads((RUN/'temporary-world-comparison-contract.json').read_text());targets=contract['target_paths']
runner=(RUN/'runner.py').read_text();tree=ast.parse(runner);blocks=[node for node in tree.body if isinstance(node,ast.If) and isinstance(node.test,ast.Name) and node.test.id=='render' and len(node.body)==1 and isinstance(node.body[0],ast.Try)]
assert len(blocks)==1
validation=blocks[0].body[0]
material_details={}
def complete_material_proofs(native,targets):
 groups=native['live_cloud_bindings'];expected=['1216','A0','A1','R0','R1'];labels=[r['reference'] for r in groups]
 all_paths=[];row_status=[]
 for g in groups:
  rows=g['rows'];paths=[r['path'] for r in rows];pathset=set(paths);all_paths.append(pathset)
  old=sum('/CloudSea52e_' in p for p in paths);new=sum('/CloudSea52f_' in p for p in paths)
  roots={p.split('/')[1] for p in paths}
  all_flags=all(all(row[k] is True for k in ['lit_vertex_color_wrap','renderer_instance_valid','same_world','uses_shared_sun_ambient_fog','visible']) for row in rows)
  row_status.append({'reference':g['reference'],'rows':len(rows),'unique_paths':len(pathset),'roots':len(roots),'old':old,'new':new,'material_count':g['material_count'],'all_live_flags_true':all_flags,'ten_target_paths_present':set(targets).issubset(pathset),'passed':len(rows)==125 and len(pathset)==125 and len(roots)==25 and old==75 and new==50 and g['old']==75 and g['new']==50 and g['material_count']==3 and all_flags and set(targets).issubset(pathset)})
 ok=labels==expected and all(r['passed'] for r in row_status) and all(p==all_paths[0] for p in all_paths[1:])
 material_details.update({'expected_labels':expected,'actual_labels':labels,'rows':row_status,'all_five_exact_sets':ok})
 return ok
class CountRepair(ast.NodeTransformer):
 def __init__(self):self.replacements=0;self.old_expression=''
 def visit_Dict(self,node):
  node=self.generic_visit(node)
  for i,key in enumerate(node.keys):
   if isinstance(key,ast.Constant) and key.value=='three original active materials':
    self.old_expression=ast.unparse(node.values[i]);node.values[i]=ast.parse('complete_material_proofs(native, targets)',mode='eval').body;self.replacements+=1
  return node
def replay(block,label):
 # Frozen block's sole writer is atomic(pixel-diagnostic.json); redirect its
 # result to this independent audit directory, never to RUN.
 def atomic(path,value):
  assert Path(path)==RUN/'pixel-diagnostic.json'
  write(label+'-pixel-diagnostic.json',value)
 ns={'Path':Path,'json':json,'struct':struct,'out':RUN,'native':{},'pngs':[],'gate_errors':[],'targets':targets,'SCENE_SHA':SCENE_SHA,'sha':sha,'atomic':atomic,'complete_material_proofs':complete_material_proofs}
 module=ast.fix_missing_locations(ast.Module(body=[deepcopy(block)],type_ignores=[]));exec(compile(module,str(RUN/'runner.py')+'::offline-validation','exec'),ns)
 return ns
old=replay(validation,'original-rule-replay');repair=CountRepair();fixed=repair.visit(deepcopy(validation));assert repair.replacements==1
new=replay(fixed,'corrected-rule-replay')
assert old['gate_errors']==['three original active materials']
assert new['gate_errors']==[]
stdout=(RUN/'stdout.log').read_text();stderr=(RUN/'stderr.log').read_text()
errors=[line for line in (stdout+'\n'+stderr).splitlines() if line.startswith(('ERROR:','SCRIPT ERROR:','FAIL ')) or 'leaked' in line.lower() or 'handle_crash:' in line]
summary=json.loads((RUN/'images/A-native-baseline-summary.json').read_text());native=new['native']
source_bindings={'original_gate_process_sha_matches':original_gate['process_report_sha256']==sha(RUN/'process-report.json'),
 'original_gate_native_sha_matches':original_gate['native_report_sha256']==sha(RUN/'images/report.json'),
 'frozen_runner_copy_exact':any(Path(path).name=='run52g_cache.py' and digest==sha(RUN/'runner.py') for path,digest in input_hashes.items()),
 'typed_baseline_file_exact':summary['binary_sha256']==sha(RUN/'images/A-native-baseline.bin'),
 'all_four_native_digests_match_baseline':all(r['full_native_digest']==summary['typed_state_digest'] for r in native['phase_rows']),
 'all_four_node_counts_exact':all(r['node_count']==summary['nodes']==11423 for r in native['phase_rows']),
 'current_frozen_inputs_exact':inputs_exact}
process_checks={'child_exit0':process['python_returncode']==0 and process['shell_exit_code']==0 and process['terminating_signal'] is None,
 'not_stopped':process['stopped_for'] is None,'clean_recorded_and_reread_logs':process['log_errors']==[] and errors==[],
 'frozen_inputs_recorded_exact':process['frozen_inputs_unchanged'] is True,
 'old_failure_only_count_rule':process['runner_gate_errors']==['three original active materials'] and original_gate['failures']==['three original active materials'],
 'original_gate_stays_failed':original_gate['passed'] is False and (RUN/'wrapper.exit-code.txt').read_text().strip()=='1',
 'native_diagnostic_restoration_complete':native['diagnostic_complete'] is True and native['diagnostic_checks_passed'] is True and native['restoration_complete'] is True}
def rgba(path):return np.array(Image.open(path).convert('RGBA'))
a0=rgba(RUN/'images/1216-front-A0.png');r0=rgba(RUN/'images/1216-front-R0.png');a=rgba(AB/'images/1216-front-A.png');a2=rgba(AB/'images/1216-front-A2.png')
delta=a0.astype(np.int16)-r0.astype(np.int16);old_delta=a.astype(np.int16)-a2.astype(np.int16);mask=np.any(delta,axis=2);ys,xs=np.where(mask)
cross_a=a.astype(np.int16)-a0.astype(np.int16);cross_r=a2.astype(np.int16)-r0.astype(np.int16)
replica={'changed_pixels':int(mask.sum()),'changed_channels':int(np.count_nonzero(delta)),'max_channel_difference':int(np.abs(delta).max()),'total_absolute_channel_difference':int(np.abs(delta).sum()),'changed_fraction':float(mask.mean()),
 'entire_RGBA_difference_field_matches_original_AB_A2':bool(np.array_equal(delta,old_delta)),
 'pixels':[{'x':int(x),'y':int(y),'A0':a0[y,x].tolist(),'R0':r0[y,x].tolist(),'original_A':a[y,x].tolist(),'original_A2':a2[y,x].tolist()} for y,x in zip(ys,xs)],
 'unchanged_pair_exact':{'A0_A1':bool(np.array_equal(a0,rgba(RUN/'images/1216-front-A1.png'))),'R0_R1':bool(np.array_equal(r0,rgba(RUN/'images/1216-front-R1.png')))},
 'cross_process_baseline_difference_pixels':int(np.any(cross_a,axis=2).sum()),'cross_process_baseline_max_channel_difference':int(np.abs(cross_a).max()),
 'cross_process_baseline_difference_unchanged_by_rebind':bool(np.array_equal(cross_a,cross_r)),
 'bounded_conclusion':'In this fixed52f front observation on llvmpipe, exact-geometry resource rebind is sufficient to reproduce the same three-pixel residual without loading D geometry. Two before samples match and two after samples match. Renderer-internal shadow/cache/draw mechanisms were not separately observed or isolated.',
 'shadow_root_cause_proven':False,'cross_process_full_images_identical':False,'pixel_acceptance':False,'visual_acceptance':False}
write('pixel-residual-reproduction.json',replica)
after={str(p):sha(p) for p in source_files};unchanged=before==after
passed=all(source_bindings.values()) and all(process_checks.values()) and not new['gate_errors'] and all(new['requirements'].values()) and unchanged
result={'reconciled_diagnostic_execution_gate_passed':passed,'scope':'Offline complete replay of frozen native/image/file gate; single correction is exact initial1216+four-stage material proof accounting',
 'source_run':str(RUN),'original_gate_rewritten':False,'original_external_gate_passed':False,'engine_rerun':False,'all_original_run_and_AB_evidence_files_unchanged':unchanged,
 'rule_correction':{'old':repair.old_expression,'new':'Exactly [1216,A0,A1,R0,R1], each125 unique mesh paths/25 roots/75 old+50 new/3 materials/all native live flags, identical sets, ten scope targets present'},
 'original_validation_replay_errors':old['gate_errors'],'corrected_validation_replay_errors':new['gate_errors'],'all_replayed_requirements':new['requirements'],'material_proofs':material_details,'source_bindings':source_bindings,'process_checks':process_checks,
 'source_process_wall_seconds':process['wall_seconds'],'source_renderer':native['renderer'],'source_file_sha256_before':before,'source_file_sha256_after':after,'offline_script_sha256':sha(__file__),
 'reproduced_entire_original_delta':replica['entire_RGBA_difference_field_matches_original_AB_A2'],'pixel_acceptance':False,'visual_acceptance':False,'hardware_gpu_acceptance':False,'shadow_root_cause_proven':False,
 'finished_utc':datetime.now(timezone.utc).isoformat()}
write('reconciled-diagnostic-gate.json',result)
print(json.dumps({'diagnostic_gate':passed,'original_gate_untouched':unchanged,'material_labels':material_details['actual_labels'],'reproduced_original_delta':replica['entire_RGBA_difference_field_matches_original_AB_A2'],'changed_pixels':replica['changed_pixels'],'engine_rerun':False},indent=2))
assert passed
