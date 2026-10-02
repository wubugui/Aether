"""Pure Python protocol/negative controls; fake core is explicitly not Blender."""
import ast
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
import contact_guard58k as guard
import source_contact58k as entry

def main():
    rows=[]
    def check(name,value):
        guard.require(value,name);rows.append(dict(name=name,passed=True))
    def rejects(name,fn,phrase):
        try:fn()
        except (ValueError,KeyError,FileNotFoundError) as e:
            guard.require(phrase in str(e),name+' unexpected failure: '+str(e))
            rows.append(dict(name=name,passed=True,actual_error=str(e)))
        else:raise ValueError(name+' incorrectly accepted')
    for p in P.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    check('entry imports without bpy or launching native','bpy' not in sys.modules)
    code=entry.code_identities()
    contact=dict(aabb_pairs=8,coplanar_pairs=4,eps_m=1e-8,nonindexed_contact_violations=[])
    fingerprint=dict(vertices_sha256='actual-native-vertices-fixture',faces_sha256='actual-native-faces-fixture')
    with tempfile.TemporaryDirectory(prefix='j2-contact-protocol-') as tmp:
        base=Path(tmp);source=base/'fixture-source.bytes';source.write_bytes(b'FAKE saved source; NOT a Blender file')
        def make_core(out,original_pass=True):
            def fresh(actual,mode):
                check('fake fresh called only for verify',mode=='verify' and actual==out)
                verified=dict(passed=original_pass,saved_source_validated=original_pass,source_unchanged=True,
                    source_sha256=guard.sha(source),pid=os.getpid(),native_identity=dict(mesh=fingerprint),
                    readback_intersections=dict(aabb_pairs_tested=8,coplanar_pairs_tested=4))
                guard.write(out/'saved-source-verify58k.json',verified)
            def arrays(bank):
                guard.require(bank=='actual-opened-bank-fixture','Not actual opened object')
                return 'V_actual_saved_fixture','F_actual_saved_fixture'
            return SimpleNamespace(SOURCE=source,os=os,fresh=fresh,bpy=SimpleNamespace(data=SimpleNamespace(objects={'bank':'actual-opened-bank-fixture'})),
              rebuild=SimpleNamespace(BANK_NAME='bank',geometry_arrays=arrays),poly=SimpleNamespace(fingerprint=lambda V,F:fingerprint))
        def checker(V,F,eps):
            guard.require((V,F)==('V_actual_saved_fixture','F_actual_saved_fixture'),'Wrong readback arrays')
            guard.require(eps==1e-8,'Relaxed eps');return copy.deepcopy(contact)
        out=base/'positive';out.mkdir();core=make_core(out)
        proof=guard.verify_actual_saved_arrays(core,out,SimpleNamespace(check_coplanar_contacts=checker),code)
        verified=json.loads((out/'saved-source-verify58k.json').read_text());vsha=guard.sha(out/'saved-source-verify58k.json');ssha=guard.sha(source)
        check('actual-array extraction protocol positive',proof['passed'] and proof['actual_saved_source_arrays'])
        check('render prerequisite positive',guard.require_render_contact(out,source,code)==proof)
        rejects('never overwrite contact evidence',lambda:guard.verify_actual_saved_arrays(core,out,SimpleNamespace(),code),'Never replace')
        mutations=[('failed proof',lambda q:q.update(passed=False),'failed or incomplete'),
          ('unfinished proof',lambda q:q.update(state='running'),'failed or incomplete'),
          ('predicted arrays prohibited',lambda q:q.update(actual_saved_source_arrays=False),'did not use saved-source'),
          ('changed source',lambda q:q.update(source_sha256_after='bad'),'source identity mismatch'),
          ('wrong verify report',lambda q:q.update(fresh_verified_report_sha256='bad'),'report identity mismatch'),
          ('different PID',lambda q:q.update(pid=-999),'same fresh verification process'),
          ('wrong arrays',lambda q:q.update(native_array_fingerprint={}), 'arrays differ'),
          ('wrong checker code',lambda q:q.update(code_identities={}), 'code identity mismatch'),
          ('relaxed tolerance',lambda q:q['contacts'].update(eps_m=1e-7),'tolerance changed'),
          ('actual nonindexed contact',lambda q:q['contacts'].update(nonindexed_contact_violations=[dict(i=1,j=2)]),'contact detected'),
          ('missing coplanar pairs',lambda q:q['contacts'].update(coplanar_pairs=3),'Coplanar coverage differs'),
          ('missing AABB pairs',lambda q:q['contacts'].update(aabb_pairs=7),'AABB coverage differs')]
        for name,mutate,phrase in mutations:
            bad=copy.deepcopy(proof);mutate(bad)
            rejects(name,lambda:guard.validate_contact(bad,verified,ssha,vsha,code),phrase)
        missing=base/'missing';missing.mkdir()
        rejects('render cannot bypass missing proof',lambda:guard.require_render_contact(missing,source,code),'saved-source-contact58k.json')
        badout=base/'checker-failure';badout.mkdir()
        def fail_checker(V,F,eps):return dict(contact,nonindexed_contact_violations=[dict(i=1,j=2)])
        rejects('contact failure stops verify',lambda:guard.verify_actual_saved_arrays(make_core(badout),badout,SimpleNamespace(check_coplanar_contacts=fail_checker),code),'contact detected')
        fail=json.loads((badout/guard.REPORT_NAME).read_text())
        check('contact failure evidence retained',fail['state']=='completed' and not fail['passed'] and fail['contacts']['nonindexed_contact_violations'])
        rejects('failed proof blocks render',lambda:guard.require_render_contact(badout,source,code),'failed or incomplete')
        origout=base/'original-failure';origout.mkdir()
        rejects('original native failure not bypassed',lambda:guard.verify_actual_saved_arrays(make_core(origout,False),origout,SimpleNamespace(),code),'Original native verification did not pass')
        check('original failure retains contact failure',json.loads((origout/guard.REPORT_NAME).read_text())['passed'] is False)
    # Structural checks supplement executed guard controls. No runner main calls.
    runner=(P/'run_patch58k.py').read_text();source_entry=(P/'source_contact58k.py').read_text();g=(P/'contact_guard58k.py').read_text()
    checks={
      'runner loads dedicated supplement freeze':"freeze = SUPPLEMENT / 'preparation-freeze-native-contact58k.json'" in runner,
      'runner executes supplement entry':"str(SUPPLEMENT / 'source_contact58k.py')" in runner,
      'source code snapshot required':"Supplement source absent from preparation freeze" in runner and "supplement-source-snapshots" in runner,
      'result snapshots retained':"verified-snapshot-" in runner and "Contact output snapshot differs" in runner,
      'result immutability before stage':"Contact verification output changed before stage" in runner,
      'result immutability after stage':"Contact verification output changed after stage" in runner,
      'result identity required for terminal pass':"and contact_same and (not reason)" in runner,
      'failed stage breaks before render':"if not row['complete']:\n                break" in runner,
      'unchanged 30 second CPU2 RSS source caps':all(x in runner for x in ['LIMIT_SECONDS = 30','MAX_RSS_KIB = 1572864','MAX_SOURCE_BYTES = 200000','cpus = available[:2]']),
      'render fresh-process proof guard':"proof['pid']!=os.getpid()" in source_entry,
      'actual arrays no mathematical reconstruction':"core.rebuild.geometry_arrays(bank)" in g and 'poly.build(' not in g and 'rebuild_from_controls(' not in g}
    for name,value in checks.items():check(name,value)
    print(json.dumps(dict(passed=True,test_count=len(rows),tests=rows,optimized_python=not __debug__,native_started=False,
        scope='Pure Python fake-core protocol and static source checks only; no Blender or actual native proof'),indent=2))
if __name__=='__main__':main()
