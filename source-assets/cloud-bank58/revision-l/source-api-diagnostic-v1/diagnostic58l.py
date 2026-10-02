"""One explicitly scoped API diagnostic admission after TWO preserved failures."""
from pathlib import Path
import hashlib,json
from native_support58l import require,FAILURE_ADMISSIONS,DIAGNOSTIC_MODE
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
FAILURE_TERMINALS=('19bd0c016af2cb4ebae751e27f250408bdd30327e56792a69bb5c52e99102dc4','ab1e24362106a9c0be9cf3cd3c892cce3f10f0972bd987dddceb0fb6537934c7')
FAILURE_RUNS=('cloudbank58l-source-runner-v3-source-20261002T175127Z-synllgmt','cloudbank58l-source-recovery-v1-source-20261002T183837Z-52w0vvfv')

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def validate_failed_records(admission,terminal,receipt,native,observation,*,spec,run,source):
    require(all(r['stage']=='source' and r['runner_version']==spec['runner_version'] and r['run']==str(run) and r['source']==str(source) for r in (admission,terminal,receipt)),'Only exact original source failure chain')
    require(admission['state']=='admitted_one_shot_not_complete','Original one-shot admission retained')
    require(terminal['state']=='failed' and terminal['passed'] is False and terminal['prepared_passed'] is False and terminal['intended_worker_exit_code']==1,'Diagnostic rejects a successful original source')
    require(terminal['source_sha256'] is None and terminal['source_bytes'] is None and terminal['saved_source_unchanged'] is False and terminal['images']==[],'Original attempt has no saved source or image')
    require(len(terminal['stages'])==1 and terminal['stages'][0]['returncode']==1 and terminal['stages'][0]['native_exit_observed'] is True,'Exactly one actual failed original native child')
    require(receipt['passed'] is False and receipt['state']=='failed' and receipt['worker_exit_observed'] is True and receipt['worker_returncode']==1 and receipt['all_owned_children_reaped'] is True and receipt['ownership_observable'] is True,'Original failed worker exited and cleanup completed')
    require(native['mode']=='build' and native['passed'] is False and native['state']=='failed' and native['source_saved'] is False and native['images']==0 and spec['native_error'] in native['error'],'Specific original unsaved native failure')
    require(observation['actual_exit_code']==1 and observation['process_exit_observed'] is True and 0<observation['wall_seconds']<120 and observation['remaining_owned_pids']==[],'Original whole-launcher failure and no remaining descendants')
    require(terminal['admission_sha256']==receipt['admission_sha256']==spec['admission_sha256'],'Exact failed source admission')

def original_failures():
    binding=json.loads((HERE/'SOURCE_BINDING.json').read_text())
    require(binding['published_failure_commit']=='4cbe1f7cbf1ff690a2d2bd4693e42da5034309e2' and len(binding['failures'])==2,'Both fully published failures required')
    for relative,record in binding['failure_files'].items():
        p=ROOT/relative
        require(not p.is_symlink() and p.is_file() and p.stat().st_size==record['bytes'] and sha(p)==record['sha256'],'Preserve original failure bytes '+relative)
    read=lambda p:json.loads(p.read_text())
    for i,spec in enumerate(binding['failures']):
        require(spec['admission_sha256']==FAILURE_ADMISSIONS[i] and spec['terminal_sha256']==FAILURE_TERMINALS[i] and spec['run']==FAILURE_RUNS[i],'Precisely both historical failed admissions, ordered')
        directory=ROOT/spec['directory'];run=ROOT/'cloud-evidence'/spec['run'];source=ROOT/spec['source']
        require(directory==HERE.parent/('source-runner-v3' if i==0 else 'source-recovery-v1'),'Original failed runner location')
        require(source==HERE.parent/('source-v1/cloud_bank58l.blend' if i==0 else 'source-recovery-v1/cloud_bank58l_recovery_v1.blend'),'Original unsaved source location')
        require(not source.exists() and not source.is_symlink(),'Old failure never saved a source; no existing model bypass')
        ap=directory/'source-attempt.json';tp=directory/'source-terminal.json'
        require(sha(ap)==FAILURE_ADMISSIONS[i] and sha(tp)==FAILURE_TERMINALS[i],'Exact original attempt and failed terminal')
        validate_failed_records(read(ap),read(tp),read(run/'supervisor-terminal.json'),read(run/'outputs/build-result.json'),read(directory/'source-launch-observation.json'),spec=spec,run=run,source=source)
        require((run/'wrapper-report.json').read_bytes()==tp.read_bytes(),'Preserved original terminal/wrapper identity')
    return list(FAILURE_ADMISSIONS)

def require_new_admission(stage,source):
    require(stage in ('source','views'),'Known diagnostic stage')
    original_failures()
    directories={HERE,HERE.parent/'source-v1',*HERE.parent.glob('source-runner-v*'),*HERE.parent.glob('source-recovery-v*'),*HERE.parent.glob('source-api-diagnostic-v*')}
    allowed={}
    for i,name in enumerate(('source-runner-v3','source-recovery-v1')):
        allowed[HERE.parent/name/'source-attempt.json']=FAILURE_ADMISSIONS[i]
        allowed[HERE.parent/name/'source-terminal.json']=FAILURE_TERMINALS[i]
    for directory in directories:
        for old_stage in ('source','views'):
            for name in (old_stage+'-attempt.json',old_stage+'-terminal.json'):
                path=directory/name
                if not(path.exists() or path.is_symlink()):continue
                if path in allowed:require(not path.is_symlink() and path.is_file() and sha(path)==allowed[path],'Only both preserved exact old failed records may precede diagnostic')
                elif directory==HERE and stage=='views' and old_stage=='source':require(not path.is_symlink() and path.is_file(),'Current source records must be real files; full chain checked separately')
                else:raise ValueError('Diagnostic stage already attempted or foreign attempt exists; preserve evidence and stop: '+str(path))
    require(Path(source).resolve()==(HERE/'cloud_bank58l_api_diagnostic_v1.blend').resolve(),'Unique API diagnostic source output')
    if stage=='source':require(not Path(source).exists() and not Path(source).is_symlink(),'Never overwrite API diagnostic source')
