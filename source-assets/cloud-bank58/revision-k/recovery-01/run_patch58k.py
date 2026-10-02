"""Explicitly scheduled K envelope trial: one build, one fresh verification, two fresh views, 30s/CPU2/1.5GiB.

No work on import. Every attempted stage retains logs, actual wait4 exit/peak,
input identities and a wrapper terminal record. Nothing is published or sent.
"""
import argparse
from datetime import datetime, timezone
import json
import hashlib
import os
from pathlib import Path
import signal
import struct
import subprocess
import resource
import sys
import tempfile
import time
import traceback
import zlib
SUPPLEMENT = Path(__file__).resolve().parent
P = SUPPLEMENT.parent
sys.path.insert(0,str(SUPPLEMENT))
sys.path.insert(1,str(P))
import contact_guard58k as contact_guard
import source_contact58k as contact_entry
sys.path.insert(0, str(P.parent / 'revision-d/native-01'))
import common58d as c
SOURCE = SUPPLEMENT / 'authored_envelope58k.blend'
VIEWS = ['1216-source-front', 'shared-side-back']
LIMIT_SECONDS = 30
MAX_RSS_KIB = 1572864
MAX_SOURCE_BYTES = 200000

def require(value, message):
    if not value:
        raise ValueError(message)

def file_sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def rss_kib(pid):
    try:
        lines = (Path('/proc') / str(pid) / 'status').read_text().splitlines()
        row = next((line for line in lines if line.startswith('VmRSS:')), None)
        return int(row.split()[1]) if row else 0
    except FileNotFoundError:
        return 0

def matches(rows):
    try:
        return all(((c.ROOT / key).is_file() and file_sha(c.ROOT / key) == row['sha256'] for key, row in rows.items()))
    except OSError:
        return False

def png_info(path):
    data = path.read_bytes()
    require(data[:8] == b'\x89PNG\r\n\x1a\n', 'Required invariant')
    offset = 8
    payload = []
    width = height = None
    ended = False
    while offset < len(data):
        length = struct.unpack('>I', data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        chunk = data[offset + 8:offset + 8 + length]
        crc = struct.unpack('>I', data[offset + 8 + length:offset + 12 + length])[0]
        require(zlib.crc32(kind + chunk) & 4294967295 == crc, 'Required invariant')
        if kind == b'IHDR':
            width, height, depth, color, compression, filter_type, interlace = struct.unpack('>IIBBBBB', chunk)
            require(depth == 8 and color == 2 and (compression == filter_type == interlace == 0), 'Required invariant')
        if kind == b'IDAT':
            payload.append(chunk)
        offset += 12 + length
        if kind == b'IEND':
            ended = True
            break
    require(ended and offset == len(data) and width and height, 'Required invariant')
    require(len(zlib.decompress(b''.join(payload))) == height * (1 + width * 3), 'Required invariant')
    return dict(path=str(path.relative_to(c.ROOT)), width=width, height=height, bytes=len(data), sha256=file_sha(path), original_png_crc_and_payload_verified=True)

def terminate_group(child):
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass

def signal_error(number, frame):
    raise RuntimeError('Wrapper received signal ' + str(number))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-approved-patch-trial', required=True, action='store_true')
    parser.parse_args()
    start = time.monotonic()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = Path(tempfile.mkdtemp(prefix='cloudbank58k-recovery01-' + stamp + '-', dir=c.ROOT / 'cloud-evidence'))
    for name in ('inputs', 'outputs', 'blender-config', 'xdg-cache', 'xdg-config', 'xdg-data'):
        (run / name).mkdir()
    print(run, flush=True)
    state = dict(candidate='58K', state='running', complete=False, passed=False, run_id=run.name, commands=[], images=[], limits=dict(total_seconds=LIMIT_SECONDS, cpu_threads=2, max_wrapper_plus_child_rss_kib=MAX_RSS_KIB, max_source_bytes=MAX_SOURCE_BYTES), world_loaded=False, final_geometry_pass=False, visual_acceptance=False)
    c.write(run / 'process-report.json', state)
    child = None
    prepared = {}
    protected = {}
    contact_outputs = {}
    reason = None
    error = None
    peak = actual_peak = 0
    row = None
    stage_start = None
    index = None
    stage_peak = 0
    aggregate_peak = 0
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, signal_error)
    try:
        available = sorted(os.sched_getaffinity(0))
        cpus = available[:2]
        require(1 <= len(cpus) <= 2, 'Required invariant')
        os.sched_setaffinity(0, cpus)
        state['cpu_affinity'] = cpus
        require(not SOURCE.exists(), 'Existing success/failure source retained; cannot overwrite or rerun in place')
        require(not (P / 'completed-freeze58k.json').exists() and not (SUPPLEMENT / 'completed-freeze-native-contact58k.json').exists(), 'Existing terminal evidence retained')
        freeze = SUPPLEMENT / 'preparation-freeze-native-contact58k.json'
        frozen = json.loads(freeze.read_text())
        prepared = dict(frozen['files'])
        prepared[str(freeze.relative_to(c.ROOT))] = dict(bytes=freeze.stat().st_size,sha256=file_sha(freeze))
        protected = frozen['protected_files']
        require(prepared and protected and matches(prepared) and matches(protected), 'Preparation/protected inputs changed')
        blender = c.ROOT.parent / 'tools-feiting/blender-4.5.14-linux-x64/blender'
        require(file_sha(blender) == c.BINARY_SHA256, 'Official Blender binary identity mismatch')
        snapshots = run / 'inputs/supplement-source-snapshots'
        snapshots.mkdir()
        source_snapshot_rows = {}
        for original in sorted(SUPPLEMENT.glob('*.py')):
            require(str(original.relative_to(c.ROOT)) in prepared,'Supplement source absent from preparation freeze')
            copy = snapshots / original.name
            copy.write_bytes(original.read_bytes())
            require(file_sha(copy)==file_sha(original),'Supplement source snapshot differs')
            key = str(copy.relative_to(c.ROOT))
            prepared[key] = dict(bytes=copy.stat().st_size,sha256=file_sha(copy))
            source_snapshot_rows[str(original.relative_to(c.ROOT))] = key
        manifest = run / 'inputs/input-sha256.json'
        c.write(manifest, dict(preparation_freeze_sha256=file_sha(freeze), files=prepared, protected_files=protected, supplement_source_snapshots=source_snapshot_rows, blender_sha256=c.BINARY_SHA256))
        input_digest = file_sha(manifest)
        env = os.environ.copy()
        env.pop('PYTHONOPTIMIZE', None)
        env.update(OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1', BLENDER_USER_CONFIG=str(run / 'blender-config'), XDG_CACHE_HOME=str(run / 'xdg-cache'), XDG_CONFIG_HOME=str(run / 'xdg-config'), XDG_DATA_HOME=str(run / 'xdg-data'))
        jobs = [dict(mode='build', view=None), dict(mode='verify', view=None)] + [dict(mode='render', view=view) for view in VIEWS]
        for index, job in enumerate(jobs):
            if time.monotonic() - start >= LIMIT_SECONDS:
                reason = '30 second total trial budget exhausted before next stage'
                break
            require(matches(prepared) and matches(protected), 'Inputs changed between stages')
            require(all(path.is_file() and file_sha(path)==digest for path,digest in contact_outputs.items()), 'Contact verification output changed before stage')
            argv = [str(blender), '--factory-startup', '--disable-autoexec', '-b', '-t', '2', '--python-exit-code', '1', '--python', str(SUPPLEMENT / 'source_contact58k.py'), '--', '--mode', job['mode'], '--out', str(run / 'outputs')]
            if job['view']:
                argv += ['--view', job['view']]
            row = dict(job=job, state='running', complete=False, argv=argv, input_manifest_sha256=input_digest, prepared_before=True, protected_before=True, source_sha256_before=file_sha(SOURCE) if SOURCE.exists() else None)
            state['commands'].append(row)
            c.write(run / 'process-report.json', state)
            stage_start = time.monotonic()
            stage_peak = 0
            with (run / f'{index}-stdout.log').open('wb') as stdout, (run / f'{index}-stderr.log').open('wb') as stderr:
                child = subprocess.Popen(argv, cwd=c.ROOT, env=env, stdout=stdout, stderr=stderr, start_new_session=True, preexec_fn=lambda: os.sched_setaffinity(0, cpus))
                row['pid'] = child.pid
                (run / f'{index}-child.pid').write_text(str(child.pid) + '\n')
                killed = False
                while True:
                    pid, status, usage = os.wait4(child.pid, os.WNOHANG)
                    if pid:
                        code = os.waitstatus_to_exitcode(status)
                        child.returncode = code
                        child = None
                        break
                    elapsed = time.monotonic() - start
                    current = rss_kib(child.pid)
                    wrapper_current = rss_kib(os.getpid())
                    stage_peak = max(stage_peak, current)
                    peak = max(peak, current)
                    aggregate = current + wrapper_current
                    aggregate_peak = max(aggregate_peak, aggregate)
                    if elapsed >= LIMIT_SECONDS:
                        reason = '30 second total trial budget exceeded'
                    if aggregate_peak > MAX_RSS_KIB:
                        reason = '1.5 GiB observed wrapper plus child RSS exceeded'
                    if reason and (not killed):
                        terminate_group(child)
                        killed = True
                    c.write(run / 'live-resource.json', dict(state='running', stage=index, elapsed_seconds=elapsed, current_rss_kib=current, wrapper_current_rss_kib=wrapper_current, aggregate_current_rss_kib=aggregate, peak_observed_aggregate_rss_kib=aggregate_peak, peak_observed_rss_kib=peak, stage_peak_observed_rss_kib=stage_peak))
                    time.sleep(0.05)
            actual_peak = max(actual_peak, usage.ru_maxrss)
            if time.monotonic() - start > LIMIT_SECONDS:
                reason = '30 second total trial budget exceeded'
            if usage.ru_maxrss + resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > MAX_RSS_KIB:
                reason = '1.5 GiB conservative sum of actual child and wrapper peaks exceeded'
            row.update(state='completed', actual_child_exit_code=code, elapsed_seconds=time.monotonic() - stage_start, peak_observed_rss_kib=stage_peak, actual_peak_child_rss_kib=usage.ru_maxrss, actual_child_user_seconds=usage.ru_utime, actual_child_system_seconds=usage.ru_stime, prepared_after=matches(prepared), protected_after=matches(protected), source_sha256_after=file_sha(SOURCE) if SOURCE.exists() else None)
            (run / f'{index}-child.exit-code').write_text(str(code) + '\n')
            row['complete'] = bool(code == 0 and (not reason) and row['prepared_after'] and row['protected_after'])
            if job['mode'] == 'build' and SOURCE.exists() and (SOURCE.stat().st_size > MAX_SOURCE_BYTES):
                reason = 'Source exceeds 200000 bytes; retained all editable controls and stopped'
                row['complete'] = False
            if row['complete'] and job['mode'] == 'build':
                built = json.loads((run / 'outputs/build-result58k.json').read_text())
                row['complete'] = bool(built['candidate_created'] and built['pre_save_geometry_controls_views_passed'] and (built['source_sha256'] == file_sha(SOURCE)) and (built['source_bytes'] == SOURCE.stat().st_size <= MAX_SOURCE_BYTES))
            if row['complete'] and job['mode'] == 'verify':
                verified = json.loads((run / 'outputs/saved-source-verify58k.json').read_text())
                row['complete'] = bool(verified['passed'] and verified['saved_source_validated'] and verified['source_unchanged'] and (verified['source_sha256'] == file_sha(SOURCE)) and (row['source_sha256_before'] == row['source_sha256_after']))
                contact = contact_guard.require_render_contact(run / 'outputs', SOURCE, contact_entry.code_identities())
                contact_outputs = {path:file_sha(path) for path in (run/'outputs'/contact_guard.REPORT_NAME, run/'outputs/saved-source-verify58k.json')}
                for original,digest in list(contact_outputs.items()):
                    copy = run/'inputs'/('verified-snapshot-'+original.name)
                    copy.write_bytes(original.read_bytes())
                    require(file_sha(copy)==digest,'Contact output snapshot differs')
                    contact_outputs[copy] = digest
                row['contact_result_sha256'] = file_sha(run/'outputs'/contact_guard.REPORT_NAME)
                row['actual_saved_contact_passed'] = contact['passed']
                row['complete'] = bool(row['complete'] and contact['passed'])
            if row['complete'] and job['mode'] == 'render':
                proof = json.loads((run / 'outputs' / (job['view'] + '-proof.json')).read_text())
                info = png_info(run / 'outputs' / ('58K-' + job['view'] + '.png'))
                expected = (836, 471) if job['view'] == VIEWS[0] else (836, 586)
                row['complete'] = bool(proof['passed'] and proof['image_sha256'] == info['sha256'] and ((info['width'], info['height']) == expected) and proof['source_unchanged'] and (row['source_sha256_before'] == row['source_sha256_after'] == proof['source_sha256']))
                state['images'].append(dict(view=job['view'], **info))
            require(all(path.is_file() and file_sha(path)==digest for path,digest in contact_outputs.items()), 'Contact verification output changed after stage')
            c.write(run / f'{index}-stage-result.json', row)
            c.write(run / 'process-report.json', state)
            if not row['complete']:
                break
    except BaseException:
        error = traceback.format_exc()
        (run / 'wrapper-error.log').write_text(error)
        if child is not None:
            terminate_group(child)
            pid, status, usage = os.wait4(child.pid, 0)
            child.returncode = os.waitstatus_to_exitcode(status)
            actual_peak = max(actual_peak, usage.ru_maxrss)
            row.update(state='completed', complete=False, actual_child_exit_code=child.returncode, elapsed_seconds=time.monotonic() - stage_start, peak_observed_rss_kib=stage_peak, actual_peak_child_rss_kib=usage.ru_maxrss, wrapper_exception=True)
            (run / f'{index}-child.exit-code').write_text(str(child.returncode) + '\n')
            child = None
        if row is not None:
            row.update(state='completed', complete=False, wrapper_exception=True)
            c.write(run / f'{index}-stage-result.json', row)
    finally:
        same = bool(protected) and matches(protected)
        inputs_same = bool(prepared) and matches(prepared)
        contact_same = bool(contact_outputs) and all(path.is_file() and file_sha(path)==digest for path,digest in contact_outputs.items())
        if time.monotonic() - start > LIMIT_SECONDS and (not reason):
            reason = '30 second total trial budget exceeded during terminal verification'
        if actual_peak + resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > MAX_RSS_KIB:
            reason = '1.5 GiB conservative child plus wrapper peak sum exceeded at terminal verification'
        complete = bool(len(state['commands']) == 4 and len(state['images']) == 2 and all((r['complete'] for r in state['commands'])) and same and inputs_same and contact_same and (not reason) and (not error))
        code = 0 if complete else 1
        state.update(state='completed', complete=complete, passed=complete, actual_wrapper_exit_code=code, error=error, limit_stop_reason=reason, elapsed_seconds=time.monotonic() - start, peak_observed_rss_kib=peak, actual_peak_child_rss_kib=actual_peak, actual_peak_wrapper_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, peak_observed_aggregate_rss_kib=aggregate_peak, conservative_sum_of_separate_peak_rss_kib=actual_peak + resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, protected_unchanged=same, prepared_inputs_unchanged=inputs_same, contact_outputs_unchanged=contact_same, contact_output_sha256={str(path.relative_to(c.ROOT)):digest for path,digest in contact_outputs.items()}, source=dict(path=str(SOURCE.relative_to(c.ROOT)), bytes=SOURCE.stat().st_size, sha256=file_sha(SOURCE)) if SOURCE.exists() else None)
        c.write(run / 'process-report.json', state)
        c.write(run / 'terminal-proof.json', dict(run_id=run.name, process_report_sha256=file_sha(run / 'process-report.json'), complete=complete, visual_acceptance=False))
        (run / 'wrapper.exit-code').write_text(str(code) + '\n')
        freeze_path = SUPPLEMENT / 'completed-freeze-native-contact58k.json'
        if not freeze_path.exists():
            paths = [p for p in run.rglob('*') if p.is_file() and (not any((part in ('xdg-cache', 'xdg-config', 'xdg-data', 'blender-config') for part in p.relative_to(run).parts)))]
            if SOURCE.exists():
                paths.append(SOURCE)
            rows = {str(p.relative_to(c.ROOT)): dict(bytes=p.stat().st_size, sha256=file_sha(p)) for p in paths}
            c.write(freeze_path, dict(status='Terminal trial evidence, not visual acceptance', files=rows, complete=complete, world_loaded=False, final_geometry_pass=False, visual_acceptance=False))
    print(json.dumps(state, indent=2), flush=True)
    return code
if __name__ == '__main__':
    sys.exit(main())
