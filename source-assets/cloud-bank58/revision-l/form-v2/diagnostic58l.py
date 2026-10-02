"""One new form candidate admission after the exact saved/visually rejected predecessor."""
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
    prior_form_source()
    directories={HERE,HERE.parent/'source-v1',*HERE.parent.glob('source-runner-v*'),*HERE.parent.glob('source-recovery-v*'),*HERE.parent.glob('source-api-diagnostic-v*'),*HERE.parent.glob('form-v*')}
    allowed={}
    for i,name in enumerate(('source-runner-v3','source-recovery-v1')):
        allowed[HERE.parent/name/'source-attempt.json']=FAILURE_ADMISSIONS[i]
        allowed[HERE.parent/name/'source-terminal.json']=FAILURE_TERMINALS[i]
    predecessor=json.loads((HERE/'SOURCE_BINDING.json').read_text())['predecessor']
    allowed.update({ROOT/rel:row['sha256'] for rel,row in predecessor['consumed_admissions'].items()})
    for directory in directories:
        for old_stage in ('source','views'):
            for name in (old_stage+'-attempt.json',old_stage+'-terminal.json'):
                path=directory/name
                if not(path.exists() or path.is_symlink()):continue
                if path in allowed:require(not path.is_symlink() and path.is_file() and sha(path)==allowed[path],'Only exact preserved historical failed and predecessor records may precede form-v2')
                elif directory==HERE and stage=='views' and old_stage=='source':require(not path.is_symlink() and path.is_file(),'Current source records must be real files; full chain checked separately')
                else:raise ValueError('Diagnostic stage already attempted or foreign attempt exists; preserve evidence and stop: '+str(path))
    require(Path(source).resolve()==(HERE/'cloud_bank58l_form_v2.blend').resolve(),'Unique new form-v2 source output')
    if stage=='source':require(not Path(source).exists() and not Path(source).is_symlink(),'Never overwrite new form-v2 source')


def prior_form_source():
    """Bind the already published saved predecessor, not reuse its admission."""
    b=json.loads((HERE/'SOURCE_BINDING.json').read_text())['predecessor']
    require(b['published_commit']=='96b1384814c4d8fc1622ca3d17b8a3faa2883781','One fully published predecessor commit')
    require(b['source']=='source-assets/cloud-bank58/revision-l/source-api-diagnostic-v1/cloud_bank58l_api_diagnostic_v1.blend','One preserved predecessor source')
    require(b['source_sha256']=='7e72984235a84e63f5275f0287267656a8b11eaa651173856ae2beaa54ac5bd7','Exact prior source bytes')
    for relative,row in b['files'].items():
        path=ROOT/relative
        require(not path.is_symlink() and path.is_file() and path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'Preserve predecessor '+relative)
    require(sha(ROOT/b['source'])==b['source_sha256'],'Prior saved source preserved')
    directory=HERE.parent/'source-api-diagnostic-v1'
    for stage in ('source','views'):
        a=json.loads((directory/(stage+'-attempt.json')).read_text());t=json.loads((directory/(stage+'-terminal.json')).read_text());o=json.loads((directory/(stage+'-launch-observation.json')).read_text())
        receipt=json.loads((Path(t['run'])/'supervisor-terminal.json').read_text())
        require(a['stage']==t['stage']==receipt['stage']==stage and a['runner_version']==t['runner_version']==receipt['runner_version']=='cloudbank58l-source-api-diagnostic-v1','Exact predecessor stages')
        require(t['prepared_passed'] is True and t['passed'] is False and t['diagnostic_acceptance'] is False and t['full_native_acceptance'] is False,'Prior prepared status not completion authority')
        require(receipt['passed'] is True and receipt['diagnostic_acceptance'] is True and receipt['full_native_acceptance'] is False and receipt['worker_exit_observed'] is True and receipt['worker_returncode']==0 and receipt['all_owned_children_reaped'] is True,'Actual predecessor diagnostic terminal')
        require(o['actual_exit_code']==0 and o['process_exit_observed'] is True and 0<o['wall_seconds']<120 and o['remaining_owned_pids']==[],'Actual predecessor outer exit')
        require(t['source_sha256']==receipt['source_sha256']==b['source_sha256'],'Exact predecessor source throughout')
    return True
