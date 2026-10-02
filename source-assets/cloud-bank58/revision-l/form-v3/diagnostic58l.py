"""New form-v3 only; real failed-build/fresh/views history, no replacement successes."""
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
    require(b['published_commit'] == runtime58l.PUBLISHED_PREDECESSOR, 'Fully published real form-v2 views predecessor')
    require(b['original_source_stage'] == b['combined_recovery']['original_source_stage']
            == b['completed_views']['original_source_stage'] == 'failed', 'Original form-v2 source remains failed')
    require(b['combined_recovery']['existing_saved_source_fresh_open_verified'] is True
            and b['completed_views']['views_chain_verified'] is True and b['completed_views']['full_native_acceptance'] is False,
            'Actual recovery and views diagnostic scopes')
    return {key: b[key] for key in ('published_commit', 'original_source_stage', 'combined_recovery', 'completed_views')}

def original_failures():
    with runtime58l.legacy() as (recovery, views):
        old = recovery.original.diagnostic58l.original_failures()
        failed = recovery.saved_predecessor()
        require(failed['original_source_stage'] == 'failed', 'Third historical source failure remains failed')
        actual = old + [recovery.OLD_ADMISSION_SHA]
    require(actual == list(FAILURE_ADMISSIONS), 'All three genuine source failures bound')
    return actual

def prior_form_source():
    b = read(HERE / 'SOURCE_BINDING.json')['predecessor']
    verify_files(b['files']); verify_files(b['consumed_admissions'])
    actual = runtime58l.inspect_historical()
    require(actual['failure_admissions'] == list(FAILURE_ADMISSIONS), 'Every old source failure preserved')
    require({k:actual[k] for k in predecessor()} == predecessor(), 'Real old build/fresh-only/views combined predecessor')
    return predecessor()

def require_new_admission(stage, source, *, check_prior=True):
    require(stage == 'source', 'Source-only preparation; views require a later published-source adapter')
    require(Path(source).resolve() == HERE / 'cloud_bank58l_form_v3.blend', 'Unique new form-v3 source output')
    for suffix in ('attempt', 'terminal', 'launch-observation', 'launch-validation'):
        p = HERE / (stage + '-' + suffix + '.json')
        require(not p.exists() and not p.is_symlink(), 'New stage already attempted; preserve all one-shot evidence')
    require(not source.exists() and not source.is_symlink(), 'Never overwrite new form-v3 source')
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
