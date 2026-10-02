"""Fail-closed contact proof for actual independently opened native arrays.

Pure imports, with injectable source/checker for non-native negative controls.
Does not weaken or replace the frozen source's existing verification gates.
"""
import hashlib
import json
from pathlib import Path
import traceback
EPS=1e-8
REPORT_NAME='saved-source-contact58j2.json'

def require(ok,message):
    if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,data):Path(path).write_text(json.dumps(data,indent=2)+'\n')

def validate_contact(proof,verified,source_sha,verify_sha,code_identities):
    require(verified['passed'] is True and verified['saved_source_validated'] is True and verified['source_unchanged'] is True,'Original saved-source verification failed')
    require(proof['state']=='completed' and proof['passed'] is True,'Contact verification failed or incomplete')
    require(proof['actual_saved_source_arrays'] is True,'Contact check did not use saved-source arrays')
    require(proof['source_sha256_before']==proof['source_sha256_after']==source_sha==verified['source_sha256'],'Contact source identity mismatch')
    require(proof['fresh_verified_report_sha256']==verify_sha,'Original verification report identity mismatch')
    require(proof['pid']==verified['pid'],'Contact not in same fresh verification process')
    require(proof['native_array_fingerprint']==verified['native_identity']['mesh'],'Contact arrays differ from saved native identity')
    require(proof['code_identities']==code_identities,'Contact verifier code identity mismatch')
    result=proof['contacts']
    require(result['eps_m']==EPS,'Contact tolerance changed')
    require(result['nonindexed_contact_violations']==[],'Nonindexed coplanar contact detected')
    require(result['coplanar_pairs']==verified['readback_intersections']['coplanar_pairs_tested'],'Coplanar coverage differs from original checker')
    require(result['aabb_pairs']==verified['readback_intersections']['aabb_pairs_tested'],'AABB coverage differs from original checker')
    return True

def verify_actual_saved_arrays(core,out,checker,code_identities):
    """core.fresh opens SOURCE independently; no reconstruction after that call."""
    path=out/REPORT_NAME
    require(not path.exists(),'Never replace a prior contact verification report')
    state=dict(state='running',passed=False,actual_saved_source_arrays=False,pid=core.os.getpid(),
               source_sha256_before=sha(core.SOURCE),code_identities=code_identities,visual_acceptance=False)
    write(path,state)
    try:
        core.fresh(out,'verify')
        verified_path=out/'saved-source-verify58j2.json'
        verified=json.loads(verified_path.read_text())
        state['fresh_verified_report_sha256']=sha(verified_path)
        require(verified['passed'] and verified['saved_source_validated'],'Original native verification did not pass')
        # The exact mesh left by fresh open/readback. No poly.build or rebuild.
        bank=core.bpy.data.objects[core.rebuild.BANK_NAME]
        V,F=core.rebuild.geometry_arrays(bank)
        state['actual_saved_source_arrays']=True
        state['native_array_fingerprint']=core.poly.fingerprint(V,F)
        state['contacts']=checker.check_coplanar_contacts(V,F,eps=EPS)
        state.update(state='completed',source_sha256_after=sha(core.SOURCE),passed=True)
        validate_contact(state,verified,sha(core.SOURCE),sha(verified_path),code_identities)
    except BaseException:
        state['passed']=False;state['error']=traceback.format_exc();raise
    finally:
        state.update(state='completed',source_sha256_after=sha(core.SOURCE))
        state['passed']=bool(state['passed'] and state['source_sha256_before']==state['source_sha256_after'])
        write(path,state)
    return state

def require_render_contact(out,source,code_identities):
    proof=json.loads((out/REPORT_NAME).read_text());file=out/'saved-source-verify58j2.json'
    verified=json.loads(file.read_text())
    validate_contact(proof,verified,sha(source),sha(file),code_identities)
    return proof
