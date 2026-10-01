"""Shared source identities and camera setup; no action on import."""
import hashlib
import json
from pathlib import Path
from types import ModuleType

import numpy as np

HERE = Path(__file__).resolve().parent
D = HERE.parent
BANK = D.parent
ROOT = BANK.parents[1]
PLAN = D / 'control-plan58d.json'
CAGE = D / 'prototype-01/native-cage-input58d.json'
STATIC = D / 'prototype-01/check_static58d.py'
FREEZE = D / 'static-freeze58d-20261001T1550Z.json'
SOURCE = HERE / 'fold58d.blend'
SETTINGS = HERE / 'preview-settings58d.json'
BINARY_SHA256 = '050c02562f81fe80ba616a80198fa02d381e60f8b61b8d39add881f4bca0d7d8'
MESH_NAME = 'CloudBank58D_small_continuous_fold_cage'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {k: native(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [native(v) for v in value]
    return value


def write(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(native(value), indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def load_pure(path):
    module = ModuleType(path.stem + '_58d_native')
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def frozen_inputs():
    frozen = json.loads(FREEZE.read_text())
    rows = frozen['files']
    assert all(sha(ROOT / p) == r['sha256'] for p, r in rows.items()), 'Frozen static D changed'
    proof = json.loads((D / 'prototype-01/static-check-01-20261001T1550Z/static-proof58d.json').read_text())
    assert proof['passed'] and proof['reconstructed_after_workspace_reset']
    plan, cage = json.loads(PLAN.read_text()), json.loads(CAGE.read_text())
    assert len(cage['vertices']) == 325 and len(cage['faces']) == 646
    assert len(plan['curves']) == 32 and len(plan['valley_controls']) == 2
    return plan, cage, json.loads(SETTINGS.read_text())


def source_coordinates(world, plan):
    q = np.asarray(world, float) - np.asarray(plan['anchor_godot_world_xyz'], float)
    return np.stack((q[..., 0], -q[..., 2], q[..., 1]), axis=-1)


def world_coordinates(source, plan):
    q = np.asarray(source, float)
    return np.stack((q[..., 0], q[..., 2], -q[..., 1]), axis=-1) + np.asarray(plan['anchor_godot_world_xyz'], float)


def all_guides(plan):
    return [*plan['curves'], *[dict(v, role='valley_floor') for v in plan['valley_controls']]]


def camera_resolution(scene, camera):
    scene.render.resolution_x, scene.render.resolution_y = camera['resolution_xy']
    scene.render.pixel_aspect_x, scene.render.pixel_aspect_y = camera['pixel_aspect_xy']
    scene.render.resolution_percentage = 100
    scene.camera = camera


def camera_proof(scene, camera, vertices, plan, settings):
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    camera_resolution(scene, camera)
    bpy.context.view_layer.update()
    points = [world_to_camera_view(scene, camera, p) for p in vertices]
    bounds = [[min(p[k] for p in points) for k in range(2)], [max(p[k] for p in points) for k in range(2)]]
    depths = [p.z for p in points]
    projection = camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),
        x=scene.render.resolution_x, y=scene.render.resolution_y,
        scale_x=scene.render.pixel_aspect_x, scale_y=scene.render.pixel_aspect_y)
    result = dict(name=camera['view_name'], matrix_world=[list(r) for r in camera.matrix_world],
                  projection=[list(r) for r in projection], actual_vertex_bounds_normalized=bounds,
                  depth_range_m=[min(depths), max(depths)], resolution_xy=list(camera['resolution_xy']),
                  pixel_aspect_xy=list(camera['pixel_aspect_xy']), all_vertices_in_front=min(depths) > 0,
                  actual_vertex_count=len(vertices), world_loaded=False, visual_acceptance=False)
    if camera['view_name'] == settings['front']['name']:
        expected = np.asarray(plan['camera']['camera_projection_columns'], float).T
        error = float(np.abs(np.asarray(projection) - expected).max())
        result.update(expected_reference_projection=expected.tolist(), maximum_projection_matrix_error=error,
                      passed=bool(error < settings['front']['maximum_projection_matrix_error'] and min(depths)>0),
                      crop_permitted_for_exact_reference_camera=True, reduced_resolution_not_reference_pixel_validation=True)
    else:
        margin = min(bounds[0] + [1 - p for p in bounds[1]])
        result.update(minimum_margin=margin, passed=bool(margin >= settings['complete_shape_minimum_margin'] and min(depths)>0),
                      all_actual_vertices_inside=margin>=0)
    return result


def create_cameras(scene, collection, bank, plan, settings):
    import bpy
    import math
    from mathutils import Matrix, Vector
    from bpy_extras.object_utils import world_to_camera_view
    vertices = [bank.matrix_world @ v.co for v in bank.data.vertices]
    camera_rows = []
    def new_camera(name, resolution, aspect):
        data = bpy.data.cameras.new('VIEW58D_' + name)
        ob = bpy.data.objects.new(data.name, data)
        collection.objects.link(ob)
        ob['view_name'], ob['resolution_xy'], ob['pixel_aspect_xy'] = name, resolution, aspect
        data.clip_start, data.clip_end = .35, 18000
        data.lens = 50
        return ob
    front = settings['front']
    camera = new_camera(front['name'], front['resolution_xy'], front['pixel_aspect_xy'])
    basis = plan['camera']['camera_transform']
    godot = Matrix([basis[0:3], basis[3:6], basis[6:9]]).transposed()
    conversion = Matrix(((1,0,0),(0,0,-1),(0,1,0)))
    matrix = (conversion @ godot).to_4x4()
    matrix.translation = Vector(source_coordinates(basis[9:], plan))
    camera.matrix_world = matrix
    camera.data.type, camera.data.sensor_fit = 'PERSP', 'VERTICAL'
    camera.data.sensor_height = 32
    camera.data.lens = 32 / (2 * math.tan(math.radians(plan['camera']['camera_fov']) / 2))
    camera.data.clip_start, camera.data.clip_end = plan['camera']['camera_near'], plan['camera']['camera_far']
    camera_rows.append(camera_proof(scene, camera, vertices, plan, settings))
    low = Vector([min(v[k] for v in vertices) for k in range(3)])
    high = Vector([max(v[k] for v in vertices) for k in range(3)])
    target = (low + high) / 2
    for spec in settings['complete_shape_views']:
        camera = new_camera(spec['name'], settings['complete_shape_resolution_xy'], settings['complete_shape_pixel_aspect_xy'])
        camera.data.type, camera.data.ortho_scale = 'ORTHO', 1600
        camera.location = target + Vector(spec['source_offset_xyz_m'])
        camera.rotation_euler = (target - camera.location).to_track_quat('-Z','Y').to_euler()
        camera_resolution(scene, camera)
        bpy.context.view_layer.update()
        points = [world_to_camera_view(scene, camera, p) for p in vertices]
        span = max(max(p.x for p in points)-min(p.x for p in points), max(p.y for p in points)-min(p.y for p in points))
        camera.data.ortho_scale *= span / settings['complete_shape_max_normalized_span']
        bpy.context.view_layer.update()
        points = [world_to_camera_view(scene, camera, p) for p in vertices]
        cx = (min(p.x for p in points)+max(p.x for p in points)) / 2
        cy = (min(p.y for p in points)+max(p.y for p in points)) / 2
        right = camera.matrix_world.to_quaternion() @ Vector((1,0,0))
        up = camera.matrix_world.to_quaternion() @ Vector((0,1,0))
        aspect = scene.render.resolution_x * scene.render.pixel_aspect_x / (scene.render.resolution_y * scene.render.pixel_aspect_y)
        camera.location += right * ((cx-.5)*camera.data.ortho_scale) + up * ((cy-.5)*camera.data.ortho_scale/aspect)
        camera_rows.append(camera_proof(scene, camera, vertices, plan, settings))
    camera_resolution(scene, bpy.data.objects['VIEW58D_' + front['name']])
    return camera_rows
