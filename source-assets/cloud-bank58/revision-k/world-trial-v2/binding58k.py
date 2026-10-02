"""Fixed v1 parse authority and explicit one-copy cross-namespace relocation."""
import hashlib
import json
import os
from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
V1 = HERE.parent/'world-trial-v1'
sys.path.insert(0,str(V1))
import run_world58k as old
support = old.support
ROOT = old.ROOT
SOURCE = Path('/tmp/cloud58k-world-trial-v1-d92irkqc')
DESTINATION = ROOT.parent/'Aether-working/cloud58k-world-trial-v2'
PARSE_RUN = ROOT/'cloud-evidence/cloudbank58k-world-trial-v1-parse-20261002T113709Z-1s3mdfe0'
PARSE_SHA = 'a7325d6a678c761006205f798aaaba691a3c52060a06fe03ddb9aa09e17ae714'
PARSE_MANIFEST_SHA = '0cc6c72f733f51320a460a1e31be153b1516aafba3576abe792a3569685201ea'
V1_FREEZE_SHA = '4c99da76ec61bae16a3ec445f187286ef68471d1261bef989eb1c2bb352ae148'
VERSION = 'cloud58k-world-trial-v2'
require = old.require
sha = support.sha


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def relative_manifest(absolute, root):
    result = {}
    for name, digest in absolute.items():
        path = Path(name)
        require(path.is_absolute() and '..' not in path.parts,'Absolute clean bound file path')
        relative = path.relative_to(root).as_posix()
        require(relative and relative not in result,'Unique project member')
        result[relative] = digest
    return dict(sorted(result.items()))


def inspect_tree(root):
    require(root.is_dir() and not root.is_symlink(),'Real existing work-tree directory')
    directories = []; result = {}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(),'No symbolic member: '+str(path))
        if path.is_file(): result[path.relative_to(root).as_posix()] = sha(path)
        elif path.is_dir(): directories.append(path.relative_to(root).as_posix())
        else: raise ValueError('No special member: '+str(path))
    return dict(files=result,directories=directories)


def parse_authority():
    require(sha(V1/'preparation-freeze.json') == V1_FREEZE_SHA,'Original 47-file freeze unchanged')
    old.preparation()
    terminal = support.strict_json(V1/'parse-terminal.json')
    require(terminal['passed'] is True and terminal['run'] == str(PARSE_RUN) and terminal['freeze_sha256'] == V1_FREEZE_SHA and terminal['wrapper_report_sha256'] == PARSE_SHA,'Original actual successful parse terminal')
    require(sha(PARSE_RUN/'wrapper-report.json') == PARSE_SHA,'Original parse report bytes')
    report = support.strict_json(PARSE_RUN/'wrapper-report.json')
    require(report['passed'] is True and report['stage'] == 'parse' and report['temporary_project'] == str(SOURCE),'Original parse root and result')
    require(support.process_passed(report['process']) and not report['logged_errors'],'Actual parse wait4/log success')
    manifest = PARSE_RUN/'temporary-project-after.json'
    require(sha(manifest) == PARSE_MANIFEST_SHA == report['temporary_project_manifest_sha256'],'Original complete parse manifest')
    expected = relative_manifest(support.strict_json(manifest),SOURCE)
    require(len(expected) == 4889,'Exactly original parse membership')
    return expected


def preparation():
    expected = parse_authority()
    freeze = support.strict_json(HERE/'preparation-freeze.json')
    for name,row in freeze['files'].items():
        path = ROOT/name
        require(path.stat().st_size == row['bytes'] and sha(path) == row['sha256'],'v2 frozen file changed: '+name)
    return expected


def migrated_copy():
    expected = preparation()
    terminal = support.strict_json(HERE/'migration-terminal.json')
    require(terminal['passed'] is True and terminal['v2_freeze_sha256'] == sha(HERE/'preparation-freeze.json'),'Successful same-freeze one-time migration required')
    run = Path(terminal['run'])
    require(run.parent == ROOT/'cloud-evidence' and run.name.startswith('cloudbank58k-world-trial-v2-migration-'),'Exact relocation evidence scope')
    receipt_path = run/'migration-report.json'
    require(sha(receipt_path) == terminal['report_sha256'],'Bound completed relocation report')
    receipt = support.strict_json(receipt_path)
    require(receipt['passed'] is True and receipt['source'] == str(SOURCE) and receipt['destination'] == str(DESTINATION),'Explicit one-copy path rebasing')
    require(receipt['parse_report_sha256'] == PARSE_SHA and receipt['parse_manifest_sha256'] == PARSE_MANIFEST_SHA and receipt['v1_freeze_sha256'] == V1_FREEZE_SHA,'Original parse authority retained after relocation')
    require(not SOURCE.exists(),'Original work copy no longer present in this namespace')
    require(sha(run/'before-tree.json') == receipt['before_tree_sha256'] and sha(run/'after-tree.json') == receipt['after_tree_sha256'],'Full relocation manifest bytes')
    require(sha(run/'before-directory-identities.json') == receipt['before_directory_identities_sha256'] and sha(run/'after-directory-identities.json') == receipt['after_directory_identities_sha256'],'Original and relocated root/directory device/inode metadata evidence')
    before = support.strict_json(run/'before-tree.json'); after = support.strict_json(run/'after-tree.json')
    require(before == after and after['files'] == expected,'Exact original relative membership, directory set and bytes')
    require(inspect_tree(DESTINATION) == after,'Actual shared work tree exactly equals relocated parse copy')
    return expected,receipt
