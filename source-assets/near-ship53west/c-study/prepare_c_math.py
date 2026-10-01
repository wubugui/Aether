#!/usr/bin/env python3
"""CPU-only initial C search. Uses saved v2 conservative bounds, no Godot scene.

This is approximate projection over an already measured 3D bounding box, not
actual renderer, mesh-vertex, occlusion or physics acceptance. Runtime v3 must
verify every selected pose against the unchanged scene and exact mesh vertices.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math
import re
import numpy as np

ROOT = Path('/workspace/scratch/a29d03198654/Aether')
HERE = ROOT / 'source-assets/near-ship53west/c-study'
PRIOR = ROOT / 'cloud-evidence/near-ship53west-v2-renderer-20261001T072841Z-i9rjqlen/images/near-ship-report.json'
PRIOR_SHA = 'fefe96426b846e92c17120a97b752757273d59d19eb7b88a85a26d4063887dac'
MEASUREMENTS = HERE / 'reference-main-and-mirror-measurements.json'


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def bbox(uv):
    lo, hi = uv.min(axis=1), uv.max(axis=1)
    return lo, hi, (lo + hi) / 2, hi - lo


def main():
    assert sha(PRIOR) == PRIOR_SHA
    prior = json.loads(PRIOR.read_text())
    assert prior['complete'] and prior['limited_near_side_comparison_passed']
    measurements = json.loads(MEASUREMENTS.read_text())
    bounds = [c['details']['conservative_bounds'] for c in prior['checks'] if c['name'] == 'Actual visible geometry and two body shapes collected']
    results = {}
    for reference, bound in zip(['1128', '1129'], bounds):
        numbers = [float(s) for s in re.findall(r'-?\d+\.\d+', bound)]
        minimum, size = np.array(numbers[:3]), np.array(numbers[3:])
        # Additional5cm numerical reserve over the printed source bounds.
        minimum -= .05
        size += .10
        corners = np.array([minimum + size * np.array(bits) for bits in itertools.product([0, 1], repeat=3)])
        target = measurements[reference]
        target_center = np.array([target['ship_center_uv'], target['reflection_center_uv']])
        target_size = np.array([target['ship_size_uv'], target['reflection_size_uv']])
        fov = 64 if reference == '1128' else 66
        tangent = math.tan(math.radians(fov) / 2)
        aspect = 1179 / 664
        raw_aspect = 1672 / 941
        min_ship_y = -minimum[1] + .5
        depth_values = np.arange(32.5, 65.001, 1.25)
        ship_values = min_ship_y + np.arange(0, 8.001, .5)
        combos = np.array(list(itertools.product(depth_values, ship_values)))
        depth, ship_y = combos[:, 0], combos[:, 1]
        rows = []
        evaluated = 0
        for camera_y in np.arange(1., 6.001, .5):
            for pitch_deg in np.arange(-4., 2.001, .5):
                pitch = math.radians(pitch_deg)
                c, s = math.cos(pitch), math.sin(pitch)
                right = (target_center[:, 0].mean() - .5) * 2 * depth * tangent * aspect - (minimum[0] + size[0] / 2)

                def project():
                    lateral = right[:, None] + corners[:, 0]
                    distance = depth[:, None] - corners[:, 2]
                    height = ship_y[:, None] + corners[:, 1]
                    z_real = distance * c + (height - camera_y) * s
                    y_real = (height - camera_y) * c - distance * s
                    z_mirror = distance * c + (-height - camera_y) * s
                    y_mirror = (-height - camera_y) * c - distance * s
                    real = np.stack([.5 + lateral / (2 * z_real * tangent * aspect), .5 - y_real / (2 * z_real * tangent)], axis=2)
                    mirror = np.stack([.5 + lateral / (2 * z_mirror * tangent * aspect), .5 - y_mirror / (2 * z_mirror * tangent)], axis=2)
                    raw = np.stack([.5 + lateral / (2 * z_mirror * tangent * 1.08 * raw_aspect), .5 + y_mirror / (2 * z_mirror * tangent * 1.08)], axis=2)
                    return real, mirror, raw, z_real, z_mirror

                for _ in range(2):
                    real, mirror, raw, z_real, z_mirror = project()
                    center_x = (bbox(real)[2][:, 0] + bbox(mirror)[2][:, 0]) / 2
                    right += (target_center[:, 0].mean() - center_x) * 2 * depth * tangent * aspect
                real, mirror, raw, z_real, z_mirror = project()
                rb, mb, rawb = bbox(real), bbox(mirror), bbox(raw)
                observed_center = np.stack([rb[2], mb[2]], axis=1)
                observed_size = np.stack([rb[3], mb[3]], axis=1)
                scores = np.square(np.log(observed_size / target_size)).sum(axis=(1, 2)) + 64 * np.square(observed_center - target_center).sum(axis=(1, 2))
                inside = (z_real.min(axis=1) > .35) & (z_mirror.min(axis=1) > .35)
                for boxes in [rb, mb, rawb]:
                    inside &= (boxes[0].min(axis=1) >= .025) & (boxes[1].max(axis=1) <= .975)
                evaluated += len(scores)
                # Keep only the best local seeds; all true physical tests occur later.
                indices = np.argsort(np.where(inside, scores, np.inf))[:12]
                for index in indices:
                    if not inside[index]: continue
                    rows.append({'camera_y': float(camera_y), 'camera_pitch_degrees': float(pitch_deg),
                                 'horizontal_depth_m': float(depth[index]), 'ship_origin_y': float(ship_y[index]),
                                 'right_m': float(right[index]), 'score': float(scores[index]),
                                 'conservative_lowest_visual_y': float(ship_y[index] + minimum[1]),
                                 'main_box_uv': {'min': rb[0][index].tolist(), 'max': rb[1][index].tolist(), 'center': rb[2][index].tolist(), 'size': rb[3][index].tolist()},
                                 'mirror_box_uv': {'min': mb[0][index].tolist(), 'max': mb[1][index].tolist(), 'center': mb[2][index].tolist(), 'size': mb[3][index].tolist()},
                                 'raw_reflection_box_uv': {'min': rawb[0][index].tolist(), 'max': rawb[1][index].tolist()},
                                 'relative_main_size_residual': (rb[3][index] / target_size[0] - 1).tolist(),
                                 'relative_mirror_size_residual': (mb[3][index] / target_size[1] - 1).tolist()})
        rows.sort(key=lambda row: row['score'])
        seeds = rows[:48]
        assert seeds, f'No bounded conservative seed for {reference}'
        results[reference] = {'evaluated': evaluated, 'source_printed_padded_bounds': bound,
                              'additional_numerical_padding_m': .05, 'camera_y_range_m': [1, 6],
                              'camera_pitch_range_degrees': [-4, 2], 'depth_range_m': [32.5, 65],
                              'ship_origin_range_m': [float(ship_values.min()), float(ship_values.max())],
                              'target': target, 'ranked_seeds': seeds,
                              'best_on_camera_height_boundary': seeds[0]['camera_y'] in [1, 6],
                              'physics_verified': False, 'actual_mesh_projection_verified': False,
                              'full_reference_acceptance': False}
        print(reference, 'evaluated', evaluated, 'best', {key: seeds[0][key] for key in ['camera_y', 'camera_pitch_degrees', 'horizontal_depth_m', 'ship_origin_y', 'score', 'relative_main_size_residual', 'relative_mirror_size_residual']})
    report = {'version': 'C-initial-CPU-conservative-box-search-v1', 'candidate_sha256': prior['candidate_sha256'],
              'prior_runtime': str(PRIOR), 'prior_runtime_sha256': PRIOR_SHA,
              'measurements': str(MEASUREMENTS), 'measurements_sha256': sha(MEASUREMENTS),
              'method': 'CPU projection of saved v2 whole-ship padded bounds including full propeller revolution; unchanged cameraXZ, vertical FOV64/66, scale and1.08 optical overscan. CameraY1-6m, pitch-4..2deg and ship position jointly searched; no geometry or game scene loaded. Runtime exact vertices and actual physics remain mandatory.',
              'score': 'Sum of squared logarithmic main/mirror width and height ratios plus64 times squared main/mirror center UV residuals. No score threshold constitutes visual acceptance.',
              'scope': 'Initial finite search, not global optimum; preserves model proportion residuals. No image resizing, cropping, world save or renderer.',
              'references': results}
    (HERE / 'c-math-proposals.json').write_text(json.dumps(report, indent=2) + '\n')
    print('proposals_sha256', sha(HERE / 'c-math-proposals.json'))


if __name__ == '__main__':
    main()
