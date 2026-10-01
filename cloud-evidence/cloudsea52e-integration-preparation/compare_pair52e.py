#!/usr/bin/env python3
"""Strict metadata pairing plus unmasked pixel differences, never visual acceptance."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

root = Path(sys.argv[1]).resolve()
a = json.loads((root / '51b/report.json').read_text())
b = json.loads((root / '52e/report.json').read_text())
aa = {x['name']: x for x in a['captures']}
bb = {x['name']: x for x in b['captures']}
expected = {f'{ref}-{view}' for ref in ('1128', '1343', '1216') for view in ('front', 'side', 'back')}
checks = []
pairs = []


def check(ok, name, details=None):
    checks.append({'passed': bool(ok), 'name': name, 'details': details})


check(a['baseline_sha256'] == b['baseline_sha256'] and a['candidate_sha256'] == b['candidate_sha256'], 'Same immutable scene pair')
check(a['limited_structural_runtime_passed'] and b['limited_structural_runtime_passed'], 'Both native structural/runtime verifiers passed')
check(set(aa) == set(bb) and expected <= set(aa), 'All nine reference views and same supplementary views captured')
fields = ['reference', 'view', 'camera_transform', 'camera_fov', 'camera_near', 'camera_far', 'size', 'environment', 'layers_hidden_for_capture', 'reflection_requested', 'clip_enabled', 'optical_overscan']
for name in sorted(aa.keys() & bb.keys()):
    left, right = aa[name], bb[name]
    different_fields = [field for field in fields if left[field] != right[field]]
    check(not different_fields, f'Exact camera/environment/time/settings pairing {name}', different_fields)
    ia = np.asarray(Image.open(left['path']).convert('RGBA'))
    ib = np.asarray(Image.open(right['path']).convert('RGBA'))
    delta = np.abs(ia.astype(np.int16) - ib.astype(np.int16))
    pairs.append({'name': name, '51b_image': left['path'], '52e_image': right['path'], 'same_observation_settings': not different_fields, 'different_pixels': int(np.any(delta, axis=2).sum()), 'pixel_count': int(ia.shape[0]*ia.shape[1]), 'max_channel_difference': int(delta.max()), 'mean_absolute_channel_difference': float(delta.mean()), '51b_cloud_center': left['cloud_center'], '52e_cloud_center': right['cloud_center'], 'visual_acceptance': False})

am = {x['name']: x for x in a['movements']}
bm = {x['name']: x for x in b['movements']}
check(set(am) == set(bm), 'Same attempted route segments')
routes = []
for name in sorted(am.keys() & bm.keys()):
    left, right = am[name], bm[name]
    fields = ['start', 'end', 'original350m', 'physical_camera_sphere_clear', 'safe_fraction', 'collider']
    drift = [field for field in fields if left[field] != right[field]]
    check(not drift, f'Terrain/physical path unchanged {name}', drift)
    routes.append({'name': name, '51b': left, '52e': right})
known = am.get('1128-original-plus350m', {})
check(known and not known['physical_camera_sphere_clear'], 'Original1128 350m failure remains recorded')

# Side-by-side actual image sheets, scaled only, with clearly labelled columns.
for ref in ('1128', '1343', '1216'):
    sheet = Image.new('RGB', (1180, 3*356+36), '#1b2229')
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 10), f'{ref}   LEFT: saved51b    RIGHT: saved52e    actual pixels, paired fixed settings', fill='white')
    for i, view in enumerate(('front', 'side', 'back')):
        key = f'{ref}-{view}'
        if key not in aa or key not in bb:
            continue
        y = 36+i*356
        draw.text((12, y), view, fill='white')
        for col, record in enumerate((aa[key], bb[key])):
            image = Image.open(record['path']).convert('RGB').resize((590, 332), Image.Resampling.LANCZOS)
            sheet.paste(image, (col*590, y+20))
    sheet.save(root/f'paired-{ref}.jpg', quality=94)

result = {'pair_metadata_and_preservation_passed': all(x['passed'] for x in checks), 'checks': checks, 'pairs': pairs, 'route_comparisons': routes, 'source_reports': [{'path': str(root/'51b/report.json'), 'sha256': hashlib.sha256((root/'51b/report.json').read_bytes()).hexdigest()}, {'path': str(root/'52e/report.json'), 'sha256': hashlib.sha256((root/'52e/report.json').read_bytes()).hexdigest()}], 'visual_acceptance': False, 'hardware_gpu_acceptance': False, 'complete_flight_passed': False, 'prior1344_conversion_gate_passed': False, 'original350m_gate_passed': False, 'scope': 'Differences are expected for a geometry comparison. Pixel statistics do not rate similarity to references. Physical path preservation never waives original failure. Supplementary cloud center/segment checks use actual source triangles; no full sphere/ship clearance claim.'}
(root/'paired-report.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({'paired': result['pair_metadata_and_preservation_passed'], 'image_pairs': len(pairs), 'failed_checks': [x for x in checks if not x['passed']]}, indent=2))
sys.exit(0 if result['pair_metadata_and_preservation_passed'] else 1)
