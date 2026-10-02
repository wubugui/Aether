#!/usr/bin/env python3
"""Print normal-only replay with this Python runtime; no engine imports or writes."""
import hashlib, json, math, sys
from pathlib import Path
sys.dont_write_bytecode = True
run = Path(__file__).resolve().parent
here = run.parents[1] / 'source-assets/cloud-bank58/revision-l/form-v2'
sys.path.insert(0, str(here))
import native_support58l as s
def read(path):
    return json.loads(Path(path).read_text())
native = read(run/'outputs/build-result.json')
work = [(run/'outputs/build-raw.json', native['validation']['normals'])]
for probe in read(run/'outputs/build-exercise.json'):
    kinds = ('manual', 'combined', 'manual_restored', 'restored') if probe['id'] == 'manual_edit' else ('moved', 'restored')
    work += [(Path(probe[kind+'_path']), probe[kind+'_validation']['normals']) for kind in kinds]
rows = []
for path, recorded in work:
    raw = read(path)
    result = s.validate_normals(raw['mesh'])
    differences = [dict(key=k, native=recorded[k], replay=result[k], abs_difference=abs(recorded[k]-result[k]) if type(result[k]) in (float, int) else None) for k in sorted(recorded) if recorded[k] != result[k]]
    rows.append(dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), normal_validator_returned=True, whole_normal_report_exactly_equal=recorded==result, differences=differences))
print(json.dumps(dict(executable=sys.executable, sys_version=sys.version, math_module_path=getattr(math, '__file__', 'built-in'), engine_started=False, raw_count=len(rows), all_whole_normal_reports_exactly_equal=all(r['whole_normal_report_exactly_equal'] for r in rows), rows=rows), indent=2))
