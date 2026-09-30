"""Bind a section-overlap report to the exact five frozen exported assets."""
import hashlib
import json
from pathlib import Path

EXPECTED = {'cliff_' + suffix for suffix in ('crown', 'western_slab', 'front_columns', 'shadow_buttress', 'central_wall')}

def validate_section_overlap(root: Path, report_path: Path, frozen_inputs: dict) -> dict:
    report = json.loads(report_path.read_text())
    def require(ok, message):
        if not ok:
            raise ValueError('Section overlap evidence: ' + message)
    require(report.get('passed') is True, 'report did not pass')
    entries = report.get('assets', [])
    names = [entry.get('name') for entry in entries]
    require(len(names) == len(EXPECTED) and set(names) == EXPECTED, 'requires exactly the five distinct section assets')
    verified = {}
    for entry in entries:
        name = entry['name']
        key = 'res://assets/models/' + name + '.glb'
        require(entry.get('passed') is True, name + ' did not pass')
        require(entry.get('invalid_projected_faces') == 0 and entry.get('downward_nonfloor_faces') == 0, name + ' has invalid faces')
        overlap = entry.get('overlapping_projected_roof_area_m2')
        require(isinstance(overlap, (int, float)) and abs(overlap) < .001, name + ' has overlap or missing measurements')
        require(key in frozen_inputs, 'missing frozen input ' + key)
        frozen = frozen_inputs[key]['sha256']
        require(entry.get('sha256') == frozen, name + ' report hash differs from the frozen asset')
        actual = hashlib.sha256((root / key.removeprefix('res://')).read_bytes()).hexdigest()
        require(actual == frozen, name + ' changed since input freeze')
        verified[name] = frozen
    return {'passed': True, 'report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(), 'asset_sha256': verified}
