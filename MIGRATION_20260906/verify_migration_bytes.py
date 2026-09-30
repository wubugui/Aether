"""Verify every frozen source file using the original migration SHA256 list."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'MIGRATION_20260906/FILE_MANIFEST.jsonl'


def verify(entry):
    try:
        assert entry['path'].startswith('test6/')
        target = (ROOT / entry['path'][6:]).resolve()
        assert target.is_relative_to(ROOT)
        if target.stat().st_size != entry['bytes']:
            return {'path': entry['path'], 'error': 'size mismatch'}
        digest = hashlib.sha256()
        with target.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        if digest.hexdigest() != entry['sha256']:
            return {'path': entry['path'], 'error': 'SHA256 mismatch'}
        return None
    except Exception as error:
        return {'path': entry['path'], 'error': str(error)}


if __name__ == '__main__':
    output = ROOT / 'MIGRATION_20260906/RESTORE_BYTE_VERIFY_20260908.json'
    assert not output.exists()
    started = datetime.now(timezone.utc).isoformat()
    failures = []
    checked = 0
    with MANIFEST.open(encoding='utf-8-sig') as stream, ThreadPoolExecutor(max_workers=8) as pool:
        for failure in pool.map(verify, (json.loads(line) for line in stream)):
            checked += 1
            if failure:
                failures.append(failure)
            if checked % 10000 == 0:
                print('BYTE VERIFY', checked, 'failures', len(failures), flush=True)
    report = {'passed': checked == 220703 and not failures,
              'started_utc': started, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'workspace': str(ROOT), 'manifest_sha256': hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
              'checked_original_files': checked, 'failures': failures,
              'scope': 'All original file sizes and SHA256 bytes before Godot import. Additional continuation files are outside the frozen manifest.'}
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report), flush=True)
    raise SystemExit(0 if report['passed'] else 1)
