"""One explicit recovery of one preserved, unsaved failed source attempt only."""
from pathlib import Path
import hashlib,json
from native_support58l import require,RECOVERY_FAILURE_SHA256
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OLD=HERE.parent/'source-runner-v3'
FAILURE_RUN='cloudbank58l-source-runner-v3-source-20261002T175127Z-synllgmt'
OLD_TERMINAL_SHA256='19bd0c016af2cb4ebae751e27f250408bdd30327e56792a69bb5c52e99102dc4'

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def validate_failed_records(admission,terminal,receipt,native,observation,*,run,source):
    """Semantic checks remain explicit even though the original bytes are pinned."""
    require(all(r['stage']=='source' and r['runner_version']=='cloudbank58l-source-runner-v3' and r['run']==str(run) and r['source']==str(source) for r in (admission,terminal,receipt)),'Only original source v3 failure chain')
    require(admission['state']=='admitted_one_shot_not_complete','Original one-shot admission retained')
    require(terminal['state']=='failed' and terminal['passed'] is False and terminal['prepared_passed'] is False and terminal['intended_worker_exit_code']==1,'Recovery rejects a successful original source')
    require(terminal['source_sha256'] is None and terminal['source_bytes'] is None and terminal['saved_source_unchanged'] is False and terminal['images']==[],'Original attempt has no saved source or image')
    require(len(terminal['stages'])==1 and terminal['stages'][0]['returncode']==1 and terminal['stages'][0]['native_exit_observed'] is True,'Exactly one actual failed original native child')
    require(receipt['passed'] is False and receipt['state']=='failed' and receipt['worker_exit_observed'] is True and receipt['worker_returncode']==1 and receipt['all_owned_children_reaped'] is True and receipt['ownership_observable'] is True,'Original failed worker exited and cleanup completed')
    require(native['mode']=='build' and native['passed'] is False and native['state']=='failed' and native['source_saved'] is False and native['images']==0 and 'Actual vertex group identities' in native['error'],'Specific original unsaved shared-group failure')
    require(observation['actual_exit_code']==1 and observation['process_exit_observed'] is True and 0<observation['wall_seconds']<120 and observation['remaining_owned_pids']==[],'Original whole-launcher failure and no remaining descendants')
    require(terminal['admission_sha256']==receipt['admission_sha256']==RECOVERY_FAILURE_SHA256,'One exact failed source admission')

def original_failure():
    binding=json.loads((HERE/'SOURCE_BINDING.json').read_text())
    require(binding['original_failure_run']==FAILURE_RUN and binding['original_admission_sha256']==RECOVERY_FAILURE_SHA256 and binding['published_failure_commit']=='b896f45d96ca07f33886b5931204d75db68ba878','Unique published original failure binding')
    for relative,record in binding['failure_files'].items():
        p=ROOT/relative
        require(not p.is_symlink() and p.is_file() and p.stat().st_size==record['bytes'] and sha(p)==record['sha256'],'Preserve original failure bytes '+relative)
    admission_path=OLD/'source-attempt.json';terminal_path=OLD/'source-terminal.json'
    require(sha(admission_path)==RECOVERY_FAILURE_SHA256 and sha(terminal_path)==OLD_TERMINAL_SHA256,'Exact original attempt and failed terminal')
    run=ROOT/'cloud-evidence'/FAILURE_RUN;source=HERE.parent/'source-v1/cloud_bank58l.blend'
    require(not source.exists() and not source.is_symlink(),'Old attempt never saved a source; no existing model may be bypassed')
    read=lambda p:json.loads(p.read_text())
    validate_failed_records(read(admission_path),read(terminal_path),read(run/'supervisor-terminal.json'),read(run/'outputs/build-result.json'),read(OLD/'source-launch-observation.json'),run=run,source=source)
    require((run/'wrapper-report.json').read_bytes()==terminal_path.read_bytes(),'Preserved original terminal/wrapper identity')
    return RECOVERY_FAILURE_SHA256

def require_new_admission(stage,source):
    require(stage in ('source','views'),'Known recovery stage')
    original_failure()
    # Only the two exact old failed source records are exceptions. A new folder
    # name cannot reset any prior source/recovery admission, successful or failed.
    directories={HERE,HERE.parent/'source-v1',*HERE.parent.glob('source-runner-v*'),*HERE.parent.glob('source-recovery-v*')}
    allowed={OLD/'source-attempt.json':RECOVERY_FAILURE_SHA256,OLD/'source-terminal.json':OLD_TERMINAL_SHA256}
    for directory in directories:
        for old_stage in ('source','views'):
            for name in (old_stage+'-attempt.json',old_stage+'-terminal.json'):
                path=directory/name
                if not(path.exists() or path.is_symlink()):continue
                if path in allowed:
                    require(not path.is_symlink() and path.is_file() and sha(path)==allowed[path],'Only preserved exact old failed records may precede recovery')
                elif directory==HERE and stage=='views' and old_stage=='source':
                    require(not path.is_symlink() and path.is_file(),'Current source records must be real files; full chain checked separately')
                else:raise ValueError('Recovery stage already attempted or foreign attempt exists; preserve evidence and stop: '+str(path))
    require(Path(source).resolve()==(HERE/'cloud_bank58l_recovery_v1.blend').resolve(),'Unique recovery source output')
    if stage=='source':require(not Path(source).exists() and not Path(source).is_symlink(),'Never overwrite recovery source')
