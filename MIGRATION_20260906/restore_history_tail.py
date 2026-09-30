"""Restore the migration supplement without changing frozen history snapshots."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('migration_directory', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    source = args.migration_directory.resolve()
    destination = root / 'restored_history_20260908'
    if destination.exists():
        raise FileExistsError(destination)
    history = json.loads((root / 'history/HISTORY_INDEX.json').read_text(encoding='utf-8-sig'))
    originals = {item['thread_id']: root / item['snapshot'] for item in history['snapshots']}
    delivery = json.loads((source / 'DELIVERY_VERIFY.json').read_text(encoding='utf-8-sig'))
    expected = next(item for item in delivery['files'] if item['name'] == 'MIGRATION_CONVERSATION_TAIL.zip')
    archive_path = source / expected['name']
    assert archive_path.stat().st_size == expected['bytes']
    assert digest(archive_path) == expected['sha256']
    with zipfile.ZipFile(archive_path) as archive:
        index = json.loads(archive.read('TAIL_INDEX.json'))
        for item in index['tails']:
            original = originals[item['thread_id']]
            assert original.stat().st_size == item['original_snapshot_bytes'], original
            assert digest(original) == item['original_snapshot_sha256'], original
            if item['path']:
                tail = archive.read(item['path'])
                assert len(tail) == item['tail_bytes']
                assert hashlib.sha256(tail).hexdigest() == item['tail_sha256']
                assert len(tail.splitlines()) == item['tail_records']
        destination.mkdir()
        records = []
        for entry in archive.infolist():
            target = (destination / entry.filename).resolve()
            assert target.is_relative_to(destination), entry.filename
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(entry))
        for item in index['tails']:
            if not item['path']:
                continue
            original = originals[item['thread_id']]
            combined = destination / (item['thread_id'] + '-complete.jsonl')
            with combined.open('xb') as output, original.open('rb') as snapshot:
                shutil.copyfileobj(snapshot, output)
                output.write(archive.read(item['path']))
            assert combined.stat().st_size == item['source_bytes_at_tail_snapshot']
            count = 0
            with combined.open(encoding='utf-8') as stream:
                for line in stream:
                    json.loads(line)
                    count += 1
            records.append({'thread_id': item['thread_id'], 'file': combined.name,
                            'bytes': combined.stat().st_size, 'sha256': digest(combined),
                            'json_records': count})
    report = {'passed': True, 'source_directory': str(source),
              'original_snapshots_verified': len(index['tails']), 'original_snapshots_modified': False,
              'history_cutoff_utc': index['cutoff_utc'], 'combined_histories': records}
    (destination / 'RESTORE_HISTORY_VERIFY.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
