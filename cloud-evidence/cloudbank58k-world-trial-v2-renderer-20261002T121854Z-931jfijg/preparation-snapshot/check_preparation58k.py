"""Read-only preparation proof. No relocation, renderer, or namespace probing."""
import ast
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import binding58k as b


def check():
    expected=b.preparation()
    actual=b.inspect_tree(b.SOURCE)
    b.require(actual['files']==expected,'Current original copy still exactly matches all 4889 parse members')
    b.require(not b.DESTINATION.exists(),'No actual relocation or second work project yet')
    for pattern in ['*-attempt.json','*-terminal.json']:
        b.require(not list(b.HERE.glob(pattern)),'No v2 actual attempt claimed')
    for path in b.HERE.glob('*.py'):ast.parse(path.read_text())
    b.require(not list(b.HERE.glob('*.gd')),'No altered native observation source')
    main=b.old.original.file_manifest(b.old.p.PROJECT)
    b.require(main==json.loads((b.old.p.NATIVE/'main-project-after.json').read_text()),'All original main-project identities unchanged')
    old_failed=json.loads((b.V1/'renderer-terminal.json').read_text())
    b.require(old_failed['passed'] is False,'Original renderer admission remains failed')
    failed_run=Path(old_failed['run'])
    b.require(b.sha(failed_run/'wrapper-report.json')==old_failed['wrapper_report_sha256'],'Original failed report identity')
    failure=json.loads((failed_run/'wrapper-report.json').read_text())
    b.require(failure['images']==0 and 'process' not in failure,'Original failure happened before native admission')
    return dict(passed=True,v2_frozen_files=len(json.loads((b.HERE/'preparation-freeze.json').read_text())['files']),
        original_v1_freeze_sha256=b.V1_FREEZE_SHA,original_parse_sha256=b.PARSE_SHA,
        original_parse_manifest_sha256=b.PARSE_MANIFEST_SHA,
        current_source=str(b.SOURCE),destination=str(b.DESTINATION),
        original_member_count=len(expected),directory_count=len(actual['directories']),
        actual_source_device=b.SOURCE.stat().st_dev,authorized_work_root_device=b.ROOT.parent.stat().st_dev,
        all_original_work_members_unchanged=True,main_project_file_count=len(main),main_project_unchanged=True,
        migration_performed=False,project_copy_created=False,engine_started=False,images=0,visual_acceptance=False)


if __name__=='__main__':print(json.dumps(check(),indent=2,allow_nan=False))
