"""Finite actual compatibility/replay checks; no native asset process is launched."""
import copy,json,os,subprocess,sys,tempfile,time
from pathlib import Path
import recovery58l as r

def main():
    r.runtime();r.install_pidfd_bridge()
    report=dict(scope='Pure Python preparation only; no Blender/save/fresh-open/render',runtime=r.runtime(),engine_started=False,
                raw_or_validator_modified=False,numeric_tolerance_added=False,predecessor=r.saved_predecessor(),processes=[])
    # Full original exact-equality functions are run once against original real evidence.
    c,b=r.read(r.g.CANDIDATE_PATH),r.read(r.g.BINDING_PATH)
    raw=r.read(r.OLD_RUN/'outputs/build-raw.json');native=r.read(r.OLD_RUN/'outputs/build-result.json')
    started=time.monotonic()
    r.require(native['validation']==r.g.validate_native_raw(raw,c,b),'Whole original baseline report exact equality on bundled 3.11')
    exercise=r.original.validate_exercise(r.OLD_RUN/'outputs','build',c,b,r.g,raw)
    report['whole_build_report_exactly_equal']=True
    report['original_exercise']=exercise
    report['exact_replay_seconds']=time.monotonic()-started
    # Reuse the original normal-only runtime replay, including 3.12 negative control.
    external=r.read(r.FORM/'source-launch-observation.json')['command'][0]
    for label,python in [('bundled311',r.PYTHON),('original_external312',Path(external))]:
        p=subprocess.run([str(python),'-B',str(r.OLD_RUN/'replay_normal_runtime.py')],capture_output=True,text=True,timeout=20)
        r.require(p.returncode==0,'Normal replay process returned')
        result=json.loads(p.stdout)
        r.require(result['raw_count']==21,'All original 21 actual raw states')
        differences=sum(len(row['differences']) for row in result['rows'])
        r.require(differences==(0 if label=='bundled311' else 43),'Exact runtime positive/negative comparison preserved')
        report[label]=dict(executable=result['executable'],sys_version=result['sys_version'],raw_count=21,
                          all_whole_normal_reports_exactly_equal=result['all_whole_normal_reports_exactly_equal'],differences=differences)
    # Existing process fixture, original supervisor/helper source, short owned Python only.
    fixture=r.HERE.parent/'source-runner-v3/process_fixture.py'
    cases=('normal','registered_normal','registered_tree','register_failure','missing_metadata','late_receipt','rss_limit')
    with tempfile.TemporaryDirectory(prefix='aether-fresh-recovery-python-only-',dir='/tmp') as tmp:
        for case in cases:
            out=Path(tmp)/case;out.mkdir();start=time.monotonic()
            code="import sys;sys.path.insert(0,"+repr(str(r.HERE))+");import recovery58l as r;r.runtime();r.install_pidfd_bridge();import runpy;sys.argv=["+repr(str(fixture))+","+repr(case)+","+repr(str(out))+"];runpy.run_path("+repr(str(fixture))+",run_name='__main__')"
            p=subprocess.Popen([str(r.PYTHON),'-B','-c',code],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            stdout,stderr=p.communicate(timeout=5)
            returned=r.read(out/'returned.json');receipt=returned['result']
            expected=0 if case in ('normal','registered_normal') else 1
            r.require(p.returncode==returned['code']==expected,'Original fixture expected outcome '+case)
            r.require(receipt['supervisor_pid']==p.pid and type(p.pid) is int and p.pid>0,'Actual fixture Popen/PID')
            if case!='missing_metadata':r.require(receipt['all_owned_children_reaped'] is True,'Original fixture cleanup '+case)
            if case=='registered_tree':r.require(receipt['timeout_triggered'] is True,'Timeout tree rejected')
            if case=='rss_limit':r.require(receipt['rss_limit_triggered'] is True,'RSS rejected')
            records={str(f.relative_to(out)):f.read_text() for f in out.rglob('*') if f.is_file()}
            report['processes'].append(dict(case=case,pid=p.pid,actual_exit_code=p.returncode,wall_seconds=time.monotonic()-start,
                                            stdout=stdout,stderr=stderr,records=records))
    report.update(passed=True,fresh_open_passed=False,source_sha256=r.require_source(),old_source_stage='failed',
                  supervisor_sha256=r.sha(Path(r.deadline.__file__)),fixture_sha256=r.sha(fixture))
    return report

if __name__=='__main__':
    print(json.dumps(main(),ensure_ascii=False,indent=2))
