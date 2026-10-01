#!/usr/bin/env python3
"""Pair only the seven recovered actual metadata rows; retain nine missing rows."""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image
import numpy as np

prep=Path(__file__).resolve().parent
repo=prep.parents[1]
prior=repo/'cloud-evidence/cloudsea52e-paired-20261001T050129Z-geTptG'
baseline=json.loads((prior/'51b/report.json').read_text());old={r['name']:r for r in baseline['captures']}
interrupted=json.loads((prep/'interrupted-nine-image-ledger.json').read_text())
sources=[Path(p).resolve() for p in sys.argv[1:]]
assert len(sources)==2,'Provide completed close and climb output directories'
rows=[];checks=[];provenance=[]
for directory in sources:
    path=directory/'images/report.json';r=json.loads(path.read_text());p=json.loads((directory/'process-report.json').read_text())
    checks.append({'name':r['subset']+' subset completion','passed':r['limited_remaining_subset_passed'] and p['python_returncode']==0 and p['all_frozen_input_files_unchanged']})
    provenance.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'process_report':str(directory/'process-report.json')})
    for item in r['captures']:
        a=old[item['name']]
        fields=['reference','view','camera_transform','camera_fov','camera_near','camera_far','size','environment','layers_hidden_for_capture','reflection_requested','clip_enabled','optical_overscan']
        drift=[k for k in fields if a[k]!=item[k]]
        checks.append({'name':item['name']+' observed metadata pairing','passed':not drift,'different_fields':drift})
        ia=np.asarray(Image.open(a['path']).convert('RGBA'));ib=np.asarray(Image.open(item['path']).convert('RGBA'))
        same_size=ia.shape==ib.shape
        d=np.abs(ia.astype(np.int16)-ib.astype(np.int16)) if same_size else None
        checks.append({'name':item['name']+' decoded image dimensions pair','passed':same_size,'51b_shape':list(ia.shape),'52e_shape':list(ib.shape)})
        rows.append({'name':item['name'],'actual51b':a,'actual52e':item,'same_recorded_camera_environment':not drift,'different_pixels':int(np.any(d,axis=2).sum()) if same_size else None,'max_channel_difference':int(d.max()) if same_size else None,'whole_live_streaming_graph_equality_proven':False})
names={r['name'] for r in rows};checks.append({'name':'Exactly7 distinct remaining images','passed':len(rows)==7 and len(names)==7})
result={'remaining7_metadata_and_process_checks_passed':all(r['passed'] for r in checks),'original_pair_complete_passed':False,'reference9_runtime_json_missing':True,'surviving_reference_images':interrupted['files'],'recovered_remaining_pairs':rows,'checks':checks,'source_reports':provenance,'baseline_repeated':False,'original52e_exit137_retained':True,'original350m_gate_passed':False,'prior1344_conversion_gate_passed':False,'visual_acceptance':False,'hardware_gpu_acceptance':False,'complete_flight_passed':False,'scope':'Remaining7 images have actual fresh-process metadata paired with prior51b camera/environment values. Nine earlier52e reference PNGs survive but their per-frame runtimeJSON never existed and is not reconstructed. The interrupted full run remains failed. Live generated streaming-graph equality across different preparation histories is not established.'}
(prep/'recovery-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'remaining7_passed':result['remaining7_metadata_and_process_checks_passed'],'original_pair_complete_passed':False,'failed_checks':[r for r in checks if not r['passed']]},indent=2))
raise SystemExit(0 if result['remaining7_metadata_and_process_checks_passed'] else 1)
