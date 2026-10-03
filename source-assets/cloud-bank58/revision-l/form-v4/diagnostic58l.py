"""New form-v4 source only; actual form-v3 predecessor and failed form-v2 history."""
from pathlib import Path
import hashlib, json
from native_support58l import require, FAILURE_ADMISSIONS, DIAGNOSTIC_MODE
import runtime58l
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def read(path): return json.loads(Path(path).read_text())

def verify_files(rows):
    require(type(rows) is dict and rows, 'Nonempty exact historical file bindings')
    for rel, row in rows.items():
        p = ROOT / rel
        require(not Path(rel).is_absolute() and p.resolve().is_relative_to(ROOT) and not p.is_symlink()
                and p.is_file() and p.stat().st_size == row['bytes'] and sha(p) == row['sha256'],
                'Preserve bound original file ' + rel)

def predecessor():
    b = read(HERE / 'SOURCE_BINDING.json')['predecessor']
    require(b['published_commit'] == runtime58l.PUBLISHED_PREDECESSOR, 'Fully published actual form-v3 source/views predecessor')
    require(b['original_source_stage'] == b['completed_source']['original_source_stage']
            == b['completed_views']['original_source_stage'] == 'failed'
            and b['original_source_stage_refers_to'] == b['completed_source']['original_source_stage_refers_to'] == 'form-v2',
            'Historical form-v2 source remains failed, distinct from completed form-v3')
    require(b['completed_source']['source_chain_verified'] is True and b['completed_views']['views_chain_verified'] is True
            and b['completed_source']['full_native_acceptance'] is b['completed_views']['full_native_acceptance'] is False,
            'Actual completed form-v3 source/views diagnostic scope')
    require(b['environment_recovery']['published_commit'] == runtime58l.PUBLISHED_RECOVERY
            and b['environment_recovery']['historical_protected_directory_recreated'] is False,
            'Explicit new-environment recovery without fabricated old directory recreation')
    return {key: b[key] for key in ('published_commit', 'original_source_stage', 'original_source_stage_refers_to',
                                  'completed_source', 'completed_views', 'environment_recovery')}

def original_failures():
    from inspect_predecessor58l import original_failures as inspect_failures
    actual = inspect_failures()
    require(actual == list(FAILURE_ADMISSIONS), 'All three genuine source failures bound')
    return actual

def prior_form_source():
    b = read(HERE / 'SOURCE_BINDING.json')['predecessor']
    verify_files(b['files']); verify_files(b['consumed_admissions'])
    actual = runtime58l.inspect_historical()
    require(actual['failure_admissions'] == list(FAILURE_ADMISSIONS), 'Every old source failure preserved')
    require({k:actual[k] for k in predecessor()} == predecessor(), 'Actual completed form-v3 source/views predecessor')
    return predecessor()

def require_new_admission(stage, source, *, check_prior=True):
    require(stage == 'source', 'Source-only preparation; views require a later published-source adapter')
    require(Path(source).resolve() == HERE / 'cloud_bank58l_form_v4.blend', 'Unique new form-v4 source output')
    for suffix in ('attempt', 'terminal', 'launch-observation', 'launch-validation'):
        p = HERE / (stage + '-' + suffix + '.json')
        require(not p.exists() and not p.is_symlink(), 'New stage already attempted; preserve all one-shot evidence')
    require(not source.exists() and not source.is_symlink(), 'Never overwrite new form-v4 source')
    b = read(HERE / 'SOURCE_BINDING.json')['predecessor']
    allowed = b['consumed_admissions']
    for p in HERE.parent.rglob('*.json'):
        if not any(p.name.endswith('-' + suffix + '.json') for suffix in
                   ('attempt', 'terminal', 'launch-observation', 'launch-validation')): continue
        rel = str(p.relative_to(ROOT))
        require(rel in allowed and not p.is_symlink() and p.is_file() and p.stat().st_size == allowed[rel]['bytes']
                and sha(p) == allowed[rel]['sha256'], 'Unknown or changed historical admission; stop: ' + rel)
    if check_prior: prior_form_source()
    return predecessor()
