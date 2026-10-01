"""Bind only the actual already-completed60 scope/capture/flight evidence."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];P=R/'candidates/round40-exclusive-20260930/project'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=P/'scenes/candidate60-observation/verified60.json';v=json.loads(f.read_text())
assert v['candidate_sha256']=='8fcb0d24d503133a7e6ba29645291a73314c88b40ab447e0802937f1c802ac45'
assert all(v[k] for k in ['native_scope_passed','three_pose_capture_passed','ordinary_input_flight_passed'])
gate={'ready':True,'base_scene':'res://scenes/candidate60-observation/Game60Observation.tscn','verified60_path':str(f),'verified60_sha256':sha(f),'required_reports':[],'immutable_inputs':{}}
for path,digest in v['input_files'].items():
    p=Path(path);assert sha(p)==digest;gate['immutable_inputs']['res://'+str(p.relative_to(P))]=digest
for kind,proof in v['proofs'].items():
    p=Path(proof['process_report']);assert sha(p)==proof['sha256'];report=json.loads(p.read_text())
    assertions={'passed':True,'child_exit':0,'inputs_unchanged':True,'parse':False,'status':'finished','errors':[],'gate_errors':[]}
    assert all(report[k]==value for k,value in assertions.items())
    detail=Path(report['report']);json.loads(detail.read_text())
    gate['required_reports'].append({'kind':kind,'path':str(p),'sha256':sha(p),'assertions':assertions,'detail_report':str(detail),'detail_sha256':sha(detail)})
    gate['immutable_inputs'][str(detail)]=sha(detail)
gate['immutable_inputs'][str(f)]=sha(f)
assert {p['kind'] for p in gate['required_reports']}=={'scope','capture','flight'}
(D/'base60-gate.json').write_text(json.dumps(gate,indent=2)+'\n')
print('Fixed60 real scope/capture/flight prerequisites sealed; no renderer invocation')
