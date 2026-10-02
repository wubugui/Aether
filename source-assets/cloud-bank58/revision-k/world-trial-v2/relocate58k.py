"""Explicit file-by-file move of this one disposable, bound work copy only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import tempfile
import time
import traceback
import sys
sys.dont_write_bytecode = True
import binding58k as b


def fsync_dir(path):
    fd = os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def signature(path):
    s = path.stat(follow_symlinks=False)
    return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode]


def directory_identities(root,names):
    return {name:signature(root if name=='.' else root/name) for name in ['.',*names]}


def append_event(journal,event):
    existed=journal.exists()
    with journal.open('a') as f:
        f.write(json.dumps(event,sort_keys=True,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
    if not existed:fsync_dir(journal.parent)


def move_member(source,destination,expected,journal,relative):
    """Single file only: copy, verify, sync, journal, remove source, journal.

    Any exception deliberately leaves both sides and the journal for explicit
    recovery. This function never overwrites, retries, reconstructs or rolls back.
    """
    b.require(source.is_file() and not source.is_symlink() and not destination.exists(),'One unmoved regular member and new destination')
    before = signature(source)
    append_event(journal,dict(member=relative,state='copy_started',source_signature=before,sha256=expected))
    hasher = hashlib.sha256()
    with source.open('rb') as src, destination.open('xb') as dst:
        while data := src.read(1024*1024):
            dst.write(data);hasher.update(data)
        dst.flush();os.fsync(dst.fileno())
    b.require(signature(source) == before and hasher.hexdigest() == expected,'Source identity and streamed bytes match original member')
    b.require(b.sha(destination) == expected,'Copied destination bytes independently rehashed')
    shutil.copystat(source,destination,follow_symlinks=False)
    with destination.open('rb') as dst: os.fsync(dst.fileno())
    fsync_dir(destination.parent)
    append_event(journal,dict(member=relative,state='destination_verified_and_synced',sha256=expected,bytes=before[2],destination_signature=signature(destination)))
    b.require(signature(source) == before and b.sha(source) == expected,'Original source still exact immediately before removal')
    source.unlink()
    fsync_dir(source.parent)
    append_event(journal,dict(member=relative,state='moved_source_removed',sha256=expected))


def partition(source,destination,expected):
    """Recoverable evidence for moved/unmoved/both/corrupt; never a resume."""
    rows = {}
    for name,digest in expected.items():
        a = source/name;z = destination/name
        errors=[];values=[]
        for label,path in [('source',a),('destination',z)]:
            try:values.append(b.sha(path) if path.is_file() and not path.is_symlink() else None)
            except InterruptedError:raise
            except OSError as error:
                values.append(None);errors.append(dict(side=label,error=repr(error)))
        sa,sz=values
        rows[name] = dict(source_sha256=sa,destination_sha256=sz,
            original_recoverable=sa == digest or sz == digest,
            read_errors=errors,
            state='both_verified' if sa == sz == digest else 'unmoved' if sa == digest else 'moved' if sz == digest else 'unresolved')
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--relocate-approved-copy',action='store_true');args=parser.parse_args()
    if not args.relocate_approved_copy:
        print('Prepared only; no file moved, project copied or engine launched.');return 0
    expected=b.preparation()
    b.require(not (b.HERE/'migration-attempt.json').exists() and not (b.HERE/'migration-terminal.json').exists(),'One relocation only; preserve prior attempt')
    b.require(b.SOURCE.is_dir() and not b.DESTINATION.exists(),'Original source exists and fixed shared destination is absent')
    before=b.inspect_tree(b.SOURCE);b.require(before['files']==expected,'All original parse members/bytes verified before relocation')
    # Preflight has made no filesystem mutation. Actual move is explicitly opted in.
    with (b.HERE/'migration-attempt.json').open('x') as f:
        json.dump(dict(source=str(b.SOURCE),destination=str(b.DESTINATION),pid=os.getpid()),f);f.flush();os.fsync(f.fileno())
    run=Path(tempfile.mkdtemp(prefix='cloudbank58k-world-trial-v2-migration-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=b.ROOT/'cloud-evidence'))
    fsync_dir(run.parent)
    print(run,flush=True);started=time.monotonic()
    report=dict(version=b.VERSION,passed=False,state='preparing',source=str(b.SOURCE),destination=str(b.DESTINATION),
        v1_freeze_sha256=b.V1_FREEZE_SHA,v2_freeze_sha256=b.sha(b.HERE/'preparation-freeze.json'),
        parse_report_sha256=b.PARSE_SHA,parse_manifest_sha256=b.PARSE_MANIFEST_SHA,
        source_device=b.SOURCE.stat().st_dev,destination_parent_device=b.ROOT.parent.stat().st_dev,
        file_count=len(expected),engine_started=False,project_rebuilt=False,whole_project_copy_created=False,
        migration_phase_limit_seconds=180,wrapper_limit_seconds=300,moved_file_count=0,
        main_project_unchanged=False,protected_inputs_unchanged=False)
    journal=run/'migration-journal.jsonl';main_before={};handlers={}
    def stop(number,frame): raise InterruptedError('Migration signal '+str(number))
    try:
        for s in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM):handlers[s]=signal.signal(s,stop)
        signal.setitimer(signal.ITIMER_REAL,180)
        cpus=sorted(os.sched_getaffinity(0))[:2];b.require(len(cpus)==2,'CPU2 available');os.sched_setaffinity(0,cpus)
        main_before=b.old.original.file_manifest(b.old.p.PROJECT)
        b.require(main_before==json.loads((b.old.p.NATIVE/'main-project-after.json').read_text()),'Original main project matches accepted v3 manifest')
        b.support.atomic_json(run/'main-project-before.json',main_before)
        b.support.atomic_json(run/'before-tree.json',before)
        report['before_tree_sha256']=b.sha(run/'before-tree.json')
        b.support.atomic_json(run/'before-directory-identities.json',directory_identities(b.SOURCE,before['directories']))
        report['before_directory_identities_sha256']=b.sha(run/'before-directory-identities.json')
        b.DESTINATION.parent.mkdir(exist_ok=True)
        b.require(not b.DESTINATION.parent.is_symlink(),'Authorized real shared working parent')
        fsync_dir(b.DESTINATION.parent.parent)
        b.DESTINATION.mkdir()
        for name in before['directories']:
            directory=b.DESTINATION/name;directory.mkdir();fsync_dir(directory.parent)
        fsync_dir(b.DESTINATION.parent)
        for name,digest in expected.items():
            move_member(b.SOURCE/name,b.DESTINATION/name,digest,journal,name)
            report['moved_file_count']+=1
            if report['moved_file_count']%100==0:b.support.atomic_json(run/'migration-report.json',report)
        after=b.inspect_tree(b.DESTINATION)
        b.require(after==before,'All relative files, directories and bytes unchanged after relocation')
        b.support.atomic_json(run/'after-directory-identities.json',directory_identities(b.DESTINATION,after['directories']))
        report['after_directory_identities_sha256']=b.sha(run/'after-directory-identities.json')
        b.require(not b.inspect_tree(b.SOURCE)['files'],'No source files remain; no second full project')
        for name in sorted(before['directories'],key=lambda x:(len(Path(x).parts),x),reverse=True):(b.SOURCE/name).rmdir()
        b.SOURCE.rmdir();fsync_dir(b.SOURCE.parent)
        b.support.atomic_json(run/'after-tree.json',after)
        report['after_tree_sha256']=b.sha(run/'after-tree.json')
        report.update(passed=True,state='completed',old_source_absent=not b.SOURCE.exists())
    except BaseException:
        report.update(passed=False,state='failed',error=traceback.format_exc())
    finally:
        report['migration_phase_elapsed_seconds']=time.monotonic()-started
        if report['migration_phase_elapsed_seconds']>180:report['passed']=False
        # Keep an explicit outer 300-second guard through final protection work.
        signal.setitimer(signal.ITIMER_REAL,max(.001,300-(time.monotonic()-started)))
        errors=[]
        try:
            b.require(time.monotonic()-started<300,'Outer deadline permits partition finalization')
            parts=partition(b.SOURCE,b.DESTINATION,expected)
            b.support.atomic_json(run/'member-partition.json',parts)
            report['all_original_members_recoverable']=all(x['original_recoverable'] for x in parts.values())
            report['partition_read_error_count']=sum(len(x['read_errors']) for x in parts.values())
            report['passed']=bool(report['passed'] and report['all_original_members_recoverable'] and not report['partition_read_error_count'])
        except BaseException:errors.append(dict(stage='partition',error=traceback.format_exc()));report['passed']=False
        try:
            b.require(time.monotonic()-started<300,'Outer deadline permits main protection finalization')
            after_main=b.old.original.file_manifest(b.old.p.PROJECT)
            b.support.atomic_json(run/'main-project-after.json',after_main)
            report['main_project_unchanged']=bool(main_before and main_before==after_main)
        except BaseException:errors.append(dict(stage='main_project_after',error=traceback.format_exc()));report['passed']=False
        try:
            b.require(time.monotonic()-started<300,'Outer deadline permits frozen-input finalization')
            b.preparation();report['protected_inputs_unchanged']=True
        except BaseException:errors.append(dict(stage='protected_inputs',error=traceback.format_exc()));report['passed']=False
        report['passed']=bool(report['passed'] and report['main_project_unchanged'] and report['protected_inputs_unchanged'])
        report['finalization_errors']=errors
        signal.setitimer(signal.ITIMER_REAL,0)
        for s,h in handlers.items():signal.signal(s,h)
        report['elapsed_seconds']=time.monotonic()-started
        if report['elapsed_seconds']>300:report['passed']=False
        if not report['passed']:report['state']='failed'
        b.support.atomic_json(run/'migration-report.json',report)
        b.support.atomic_json(b.HERE/'migration-terminal.json',dict(passed=report['passed'],run=str(run),v2_freeze_sha256=report['v2_freeze_sha256'],report_sha256=b.sha(run/'migration-report.json')))
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
