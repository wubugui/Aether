"""F2: nine local height edits to F; no camera fitting or asset writes.

This is a shape hypothesis, not visual acceptance. Load the frozen F constructor
into a private in-memory module, retain its X/Z coordinates and connectivity,
and re-author six lower returns, one waist and two belly folds. No plane clamp,
whole-object translation, rescaling, smoothing or Boolean operation is used.
"""
from pathlib import Path
from types import ModuleType
import hashlib
import numpy as np

P = Path(__file__).resolve().parent
F_PATCH = P.parent / 'revision-f/patch58f.py'
F_PATCH_SHA256 = 'af15b230605ede7d53d035beb50980a560e2f3e219c5dd2b426efe3bdf9e2bb2'
EXPECTED_CHANGED_VERTEX_IDS = [113, 127, 133, 134, 138, 141, 142, 166, 180]
LOWER_DROP_EDITS = {8: (152, 142), 14: (150, 115), 15: (160, 145),
                    19: (165, 155), 22: (158, 88), 23: (144, 134)}


def make_patch(frame):
    data = F_PATCH.read_bytes()
    assert hashlib.sha256(data).hexdigest() == F_PATCH_SHA256
    base = ModuleType('frozen_f_control_for_f2')
    exec(compile(data, str(F_PATCH), 'exec'), base.__dict__)
    original = base.make_patch(frame)
    for index, (before, after) in LOWER_DROP_EDITS.items():
        assert base.SIDE_DROPS[2][index] == before
        base.SIDE_DROPS[2][index] = after
    assert base.SIDE_DROPS[1][22] == 100
    base.SIDE_DROPS[1][22] = 65
    assert base.BELLY_Y[2][5] == 520 and base.BELLY_Y[4][5] == 550
    base.BELLY_Y[2][5], base.BELLY_Y[4][5] = 545, 580
    result = base.make_patch(frame)
    old, new = np.asarray(original['vertices']), np.asarray(result['vertices'])
    assert np.where(np.any(old != new, axis=1))[0].tolist() == EXPECTED_CHANGED_VERTEX_IDS
    assert np.array_equal(old[:, [0, 2]], new[:, [0, 2]])
    assert np.array_equal(old[:63], new[:63]), 'Crown/shoulder top grid must stay exact'
    assert original['faces'] == result['faces'] and original['groups'] == result['groups']
    local, rings = np.asarray(result['local_uv_y']), np.asarray(result['ring_indices'])
    assert np.all(np.diff(local[rings, 2], axis=0) < 0), 'Side stations must descend'
    result['f2_scope'] = dict(changed_vertex_ids=EXPECTED_CHANGED_VERTEX_IDS,
                             world_xz_exact=True, top_grid_exact=True,
                             topology_and_groups_exact=True,
                             camera_fitting_applied=False,
                             final_geometry_pass=False, visual_acceptance=False)
    return result
