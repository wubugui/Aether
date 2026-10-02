"""L source adapter, deliberately inert on import or ordinary execution.

Only run58l.py may admit build/verify. The identical file is an internal Text in
the saved source. Explicit EDIT58L.py execution invokes rebuild_from_controls;
there are no handlers, drivers, auto-run Texts, saves, exports or render calls.
This source file alone is not a native parse, creation, or successful readback.

STOPPED PREPARATION: the source below is a provisional, unexecuted adapter.
The whole-bank candidate/interface conflict is unresolved. Native stage entry
unconditionally rejects in this revision. No recipe or complete native validator
exists; no source/fresh-open/material/camera/control proof is claimed. A later
reviewed revision must complete the contract before reusing any of this code.
"""
from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import struct
import sys
import time
import traceback

ANCHOR = (3958.0, 0.0, 3667.0)
MASTER = 'L58_MASTER_EDITABLE'
EXPORT = 'L58_EXPORT_DERIVED'
MESH = 'L58_CANONICAL_MESH'
MATERIAL = 'L58_K_NORMAL_LIT_MATERIAL'
CAMERA_PREFIX = 'L58_CAMERA_'
CONTROL_PREFIX = 'L58_CONTROL_'
TEXT_NAMES = ('CANDIDATE58L.json', 'RECIPE58L.json', 'BINDINGS58L.json',
              'NATIVE58L.py', 'EDIT58L.py')
BASE_ATTRIBUTE = 'l58_authored_base'
LAST_ATTRIBUTE = 'l58_last_evaluated'
LOCK_ATTRIBUTE = 'l58_locked'
INDEX_ATTRIBUTE = 'l58_canonical_index'
FACE_ATTRIBUTE = 'l58_canonical_triangle'
EDIT_TEXT = '''"""Explicit edit action only; does not save, export, or render."""
import bpy
namespace = {"__name__": "l58_embedded_edit"}
exec(compile(bpy.data.texts["NATIVE58L.py"].as_string(), "NATIVE58L.py", "exec"), namespace)
namespace["rebuild_from_controls"]()
'''
_TELEMETRY = None
_START = time.monotonic()
PREPARATION_BLOCKER = 'SPATIAL_IMPLEMENTATION_UNRESOLVED: build-v1 is blocked source preparation; native stages are disabled'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def f32(value):
    return struct.unpack('<f', struct.pack('<f', float(value)))[0]


def local(world):
    x, y, z = world
    return [f32(x - ANCHOR[0]), f32(ANCHOR[2] - z), f32(y)]


def local_vector(world):
    x, y, z = world
    return [float(x), -float(z), float(y)]


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def strict_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('Nonfinite JSON: ' + value)
    value = json.loads(text, object_pairs_hook=unique, parse_constant=invalid)
    def finite(row):
        if isinstance(row, float):
            require(math.isfinite(row), 'Nonfinite JSON float')
        elif isinstance(row, dict):
            for item in row.values():
                finite(item)
        elif isinstance(row, list):
            for item in row:
                finite(item)
    finite(value)
    return value


def write_json(path, value, *, exclusive=False):
    payload = (json.dumps(value, ensure_ascii=False, allow_nan=False,
                          separators=(',', ':')) + '\n').encode('utf-8')
    with Path(path).open('xb' if exclusive else 'wb') as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def emit(stage, **details):
    usage = resource.getrusage(resource.RUSAGE_SELF)
    row = dict(stage=stage, pid=os.getpid(), elapsed_seconds=time.monotonic()-_START,
               native_user_seconds=usage.ru_utime,
               native_system_seconds=usage.ru_stime,
               native_peak_rss_kib=usage.ru_maxrss, **details)
    line = json.dumps(row, allow_nan=False, separators=(',', ':'))
    print('L58_STAGE ' + line, flush=True)
    if _TELEMETRY is not None:
        out, label = _TELEMETRY
        with (out/(label+'-events.jsonl')).open('a') as handle:
            handle.write(line+'\n'); handle.flush(); os.fsync(handle.fileno())
        temporary = out/(label+'-progress.json.tmp')
        write_json(temporary, row)
        temporary.replace(out/(label+'-progress.json'))
    return row


def read_collection(collection, property_name, kind='f', width=1):
    """Read actual native values using RNA foreach_get, never recipe substitution."""
    values = array(kind, [0]) * (len(collection) * width)
    collection.foreach_get(property_name, values)
    values = values.tolist()
    if width == 1:
        return values
    return [values[i:i+width] for i in range(0, len(values), width)]


def write_collection(collection, property_name, values, kind='f', width=1):
    flattened = values if width == 1 else [v for row in values for v in row]
    require(len(flattened) == len(collection)*width, 'RNA write length mismatch')
    collection.foreach_set(property_name, array(kind, flattened))


def get_candidate():
    import bpy
    return strict_json(bpy.data.texts['CANDIDATE58L.json'].as_string())


def validate_edit_schema(candidate):
    require(candidate.get('implementation_ready') is True,
            'Missing or blocked geometric candidate cannot create native source')
    vertices = candidate['vertices_world']; faces = candidate['faces']
    controls = candidate['controls']; locked = candidate['locked_indices']
    require(len(vertices) > 3 and len(faces) > 3 and len(controls) == 7,
            'A real closed candidate and exactly seven semantic controls required')
    require(len({c['id'] for c in controls}) == 7, 'Unique control ids')
    require(locked == sorted(set(locked)) and all(type(i) is int and 0 <= i < len(vertices) for i in locked),
            'Exact valid sorted locked vertex indices')
    require(all(len(p) == 3 and all(math.isfinite(v) for v in p) for p in vertices),
            'Finite world positions')
    require(all(len(f) == 3 and len(set(f)) == 3 and all(type(i) is int and 0 <= i < len(vertices) for i in f)
                for f in faces), 'Oriented triangular candidate topology')
    for row in controls:
        require(all(key in row for key in ('id', 'position_world', 'semantic', 'units',
                                           'default', 'min', 'max', 'weights', 'displacements_world')),
                'Complete semantic control schema')
        require(isinstance(row['semantic'], str) and bool(row['semantic']) and isinstance(row['units'], str),
                'Named meaningful parameter semantics')
        require(all(math.isfinite(row[k]) for k in ('default', 'min', 'max')) and
                row['min'] <= row['default'] <= row['max'] and row['min'] < row['max'],
                'Finite bounded control range')
        require(len(row['weights']) == len(vertices) and len(row['displacements_world']) == len(vertices),
                'Every canonical vertex has a bound scalar and per-unit displacement')
        require(all(math.isfinite(w) and 0 <= w <= 1 and f32(w) == w for w in row['weights']),
                'Actual vertex group weights are float32 in [0,1]')
        require(all(len(v) == 3 and all(math.isfinite(x) for x in v) for v in row['displacements_world']),
                'Finite vector displacement fields')
        require(all(row['weights'][i] == 0 and row['displacements_world'][i] == [0, 0, 0]
                    for i in locked), 'All control effects vanish on locked interfaces')
        require(any(any(x != 0 for x in v) for v in row['displacements_world']),
                'Every semantic control must have real response support')
    return True


def evaluated_edit(candidate, current, authored_base, last_evaluated, values):
    """Pure explicit edit step; retain sculpt edits, recompute controls without drift.

    Base and last-evaluated are actual native POINT vector attributes. A direct
    master edit is reconciled into the base rather than replaced by the recipe.
    Locked interface coordinates are byte-exact local float32, not an epsilon.
    """
    validate_edit_schema(candidate)
    n = len(candidate['vertices_world'])
    require(len(current) == len(authored_base) == len(last_evaluated) == n,
            'Direct topology edits require a new recipe; point edits are retained')
    require(len(values) == 7, 'Exactly seven parameter values')
    for row, value in zip(candidate['controls'], values):
        require(math.isfinite(value) and row['min'] <= value <= row['max'],
                'Control value outside authored bounds: ' + row['id'])
    expected = [local(v) for v in candidate['vertices_world']]
    for i in candidate['locked_indices']:
        require(current[i] == authored_base[i] == last_evaluated[i] == expected[i],
                'Locked interface vertex modified: ' + str(i))
    base = [[f32(authored_base[i][axis] + current[i][axis] - last_evaluated[i][axis])
             for axis in range(3)] for i in range(n)]
    out = [row[:] for row in base]
    for i in range(n):
        accum = list(map(float, base[i]))
        for row, value in zip(candidate['controls'], values):
            delta = value - row['default']
            vector = local_vector(row['displacements_world'][i])
            for axis in range(3):
                accum[axis] += delta * vector[axis]
        out[i] = list(map(f32, accum))
        require(all(math.isfinite(v) for v in out[i]), 'Nonfinite edited point')
    require(all(out[i] == expected[i] for i in candidate['locked_indices']),
            'Control changed a locked interface')
    return base, out


def rebuild_from_controls():
    """Explicitly called from EDIT58L.py; never saves or evaluates automatically."""
    raise ValueError(PREPARATION_BLOCKER)
    import bpy
    candidate = get_candidate(); validate_edit_schema(candidate)
    master = bpy.data.objects[MASTER]; export = bpy.data.objects[EXPORT]
    mesh = master.data
    require(mesh is export.data and master.parent is None and export.parent is None,
            'One canonical native mesh shared by master and derived export')
    require([list(face.vertices) for face in mesh.polygons] == candidate['faces'],
            'Topology is bound to oriented canonical triangles')
    identity = [[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]]
    require([list(row) for row in master.matrix_world] == identity and
            [list(row) for row in export.matrix_world] == identity,
            'No whole-bank translation, inherited root transform, or rescale')
    current = read_collection(mesh.vertices, 'co', 'f', 3)
    base = read_collection(mesh.attributes[BASE_ATTRIBUTE].data, 'vector', 'f', 3)
    previous = read_collection(mesh.attributes[LAST_ATTRIBUTE].data, 'vector', 'f', 3)
    handles = [bpy.data.objects[CONTROL_PREFIX+row['id']] for row in candidate['controls']]
    for handle, row in zip(handles, candidate['controls']):
        require(list(handle.location) == local(row['position_world']) and
                list(handle.rotation_euler) == [0., 0., 0.] and list(handle.scale) == [1., 1., 1.],
                'Control transform locked; edit its named scalar value instead')
    values = [float(handle['value']) for handle in handles]
    new_base, points = evaluated_edit(candidate, current, base, previous, values)
    # No data layer is created here. Structural writes all finished before these
    # refreshed attribute lookups, avoiding K's invalidated-RNA-handle hazard.
    write_collection(mesh.vertices, 'co', points, 'f', 3)
    write_collection(mesh.attributes[BASE_ATTRIBUTE].data, 'vector', new_base, 'f', 3)
    write_collection(mesh.attributes[LAST_ATTRIBUTE].data, 'vector', points, 'f', 3)
    mesh.update()
    for handle, value in zip(handles, values):
        handle['last_applied_value'] = value
    bpy.context.scene['edited_after_frozen_build'] = bool(
        points != [local(p) for p in candidate['vertices_world']])
    bpy.context.view_layer.update()
    return dict(vertices=len(points), controls=7, source_saved=False,
                exported=False, rendered=False, locked_interfaces_exact=True)


def internal_text(name, payload, directory):
    import bpy
    require(name in TEXT_NAMES and name not in bpy.data.texts, 'Unique expected internal Text')
    path = directory/name
    with path.open('xb') as handle:
        handle.write(payload); handle.flush(); os.fsync(handle.fileno())
    emit('text_load.begin', name=name, bytes=len(payload))
    text = bpy.data.texts.load(filepath=str(path), internal=True)
    text.name = name
    actual = text.as_string().encode('utf-8')
    fields = dict(name=text.name, bytes=len(actual), sha256=hashlib.sha256(actual).hexdigest(),
                  is_in_memory=text.is_in_memory, filepath=text.filepath,
                  expected_sha256=hashlib.sha256(payload).hexdigest())
    write_json(directory/(name+'.load-fields.json'), fields, exclusive=True)
    if actual != payload:
        (directory/(name+'.unexpected-loaded-bytes')).write_bytes(actual)
    require(text.name == name and text.is_in_memory and text.filepath == '' and actual == payload,
            'Internal editable Text must preserve identical UTF-8 bytes: ' + name)
    text.use_module = False
    emit('text_load.complete', **fields)


def camera_matrix(record):
    raw = bytes.fromhex(record['camera_transform'])
    require(len(raw) == 52 and raw[:4] == struct.pack('<I', 18), 'Actual Transform3D byte record')
    value = struct.unpack('<12f', raw[4:])
    # Godot bytes are the original row-major 3x3 basis followed by its origin.
    # Left multiply by the one fixed world-to-Blender axis map; no look_at fit.
    rows = [list(value[i:i+3]) for i in (0, 3, 6)]
    out = [[0., 0., 0., 0.] for _ in range(4)]
    for j in range(3):
        out[0][j] = rows[0][j]; out[1][j] = -rows[2][j]; out[2][j] = rows[1][j]
    origin = local(value[9:])
    for i in range(3):
        out[i][3] = origin[i]
    out[3][3] = 1.
    return out


def create_source(candidate, binding, contract, out):
    raise ValueError(PREPARATION_BLOCKER)
    import bpy
    from mathutils import Matrix
    validate_edit_schema(candidate)
    emit('factory_reset.begin')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.use_scripts_auto_execute = False
    bpy.context.preferences.filepaths.save_version = 0
    emit('factory_reset.complete')
    scene = bpy.context.scene
    flags = dict(source_version=contract.VERSION, world_integration_allowed=False,
                 world_loaded=False, visual_acceptance=False, weather_acceptance=False,
                 auto_rebuild=False, edited_after_frozen_build=False,
                 anchor_world_json=json.dumps(list(ANCHOR)), scale_one=True)
    for key, value in flags.items():
        scene[key] = value
    collections = {}
    for name in ('L58_SOURCE', 'L58_SEMANTIC_CONTROLS', 'L58_FIXED_INSPECTION'):
        collection = bpy.data.collections.new(name); scene.collection.children.link(collection)
        collections[name] = collection
    embed = out/'embedded-text-inputs'; embed.mkdir()
    files = [('CANDIDATE58L.json', contract.CANDIDATE_PATH.read_bytes()),
             ('RECIPE58L.json', (contract.HERE/'recipe.json').read_bytes()),
             ('BINDINGS58L.json', contract.BINDING_PATH.read_bytes()),
             ('NATIVE58L.py', Path(__file__).read_bytes()),
             ('EDIT58L.py', EDIT_TEXT.encode('utf-8'))]
    for name, payload in files:
        internal_text(name, payload, embed)
    emit('mesh_create.begin')
    mesh = bpy.data.meshes.new(MESH)
    vertices = [local(point) for point in candidate['vertices_world']]
    mesh.from_pydata(vertices, [], candidate['faces']); mesh.update()
    master = bpy.data.objects.new(MASTER, mesh); collections['L58_SOURCE'].objects.link(master)
    export = bpy.data.objects.new(EXPORT, mesh); collections['L58_SOURCE'].objects.link(export)
    export.hide_render = True; export.hide_viewport = True; export.hide_set(True)
    master['edit_contract'] = 'Direct unlocked point edits are retained; then explicitly Run EDIT58L.py. Topology and interfaces fixed.'
    export['derived_from'] = MASTER; export['export_contract'] = 'Same canonical mesh, identity transform, scale one. No export has run.'
    for ob in (master, export):
        ob.lock_location = (True, True, True); ob.lock_rotation = (True, True, True)
        ob.lock_scale = (True, True, True)
    settings = dict(binding['source_inspection_lighting'],
                    material_linear_rgba=binding['material']['linear_rgba'],
                    material_roughness=binding['material']['roughness'])
    material = bpy.data.materials.new(MATERIAL); material.use_nodes = True
    material.diffuse_color = settings['material_linear_rgba']
    material.use_backface_culling = False
    principled = material.node_tree.nodes.get('Principled BSDF')
    principled.inputs['Base Color'].default_value = settings['material_linear_rgba']
    principled.inputs['Roughness'].default_value = settings['material_roughness']
    principled.inputs['Metallic'].default_value = 0.
    principled.inputs['Emission Color'].default_value = (0., 0., 0., 1.)
    principled.inputs['Emission Strength'].default_value = 0.
    mesh.materials.append(material)
    for face in mesh.polygons:
        face.use_smooth = False; face.material_index = 0
    groups = [('CONTROL_'+row['id'], row['weights']) for row in candidate['controls']]
    groups += [(row['name'], [1. if i in set(row['indices']) else 0. for i in range(len(vertices))])
               for row in candidate.get('groups', [])]
    require(len({name for name, _ in groups}) == len(groups), 'Unique semantic vertex groups')
    # Create all deform allocations BEFORE any custom attribute handles exist.
    for name, weights in groups:
        group = master.vertex_groups.new(name=name)
        export.vertex_groups.new(name=name)
        buckets = {}
        for index, weight in enumerate(weights):
            if weight:
                buckets.setdefault(f32(weight), []).append(index)
        for weight, indices in buckets.items():
            group.add(indices, weight, 'REPLACE')
    schemas = [(BASE_ATTRIBUTE, 'FLOAT_VECTOR', 'POINT'),
               (LAST_ATTRIBUTE, 'FLOAT_VECTOR', 'POINT'),
               (LOCK_ATTRIBUTE, 'INT', 'POINT'), (INDEX_ATTRIBUTE, 'INT', 'POINT'),
               (FACE_ATTRIBUTE, 'INT', 'FACE')]
    for name, kind, domain in schemas:
        mesh.attributes.new(name=name, type=kind, domain=domain)
    # Resolve each RNA layer by name only after every structural allocation.
    write_collection(mesh.attributes[BASE_ATTRIBUTE].data, 'vector', vertices, 'f', 3)
    write_collection(mesh.attributes[LAST_ATTRIBUTE].data, 'vector', vertices, 'f', 3)
    locked = set(candidate['locked_indices'])
    write_collection(mesh.attributes[LOCK_ATTRIBUTE].data, 'value', [int(i in locked) for i in range(len(vertices))], 'i')
    write_collection(mesh.attributes[INDEX_ATTRIBUTE].data, 'value', list(range(len(vertices))), 'i')
    write_collection(mesh.attributes[FACE_ATTRIBUTE].data, 'value', list(range(len(candidate['faces']))), 'i')
    for row in candidate['controls']:
        ob = bpy.data.objects.new(CONTROL_PREFIX+row['id'], None)
        collections['L58_SEMANTIC_CONTROLS'].objects.link(ob)
        ob.empty_display_type = 'SPHERE'; ob.empty_display_size = 18.
        ob.location = local(row['position_world']); ob.hide_render = True
        ob.lock_location = ob.lock_rotation = ob.lock_scale = (True, True, True)
        for key in ('id', 'semantic', 'units', 'default', 'min', 'max'):
            ob[key] = row[key]
        ob['value'] = float(row['default']); ob['last_applied_value'] = float(row['default'])
        ob.id_properties_ui('value').update(min=row['min'], max=row['max'],
                                           soft_min=row['min'], soft_max=row['max'],
                                           description=row['semantic']+' ['+row['units']+']')
    emit('mesh_create.complete', vertices=len(vertices), triangles=len(candidate['faces']), groups=len(groups))
    for record in binding['world_cameras']:
        data = bpy.data.cameras.new(CAMERA_PREFIX+record['name'])
        ob = bpy.data.objects.new(data.name, data)
        collections['L58_FIXED_INSPECTION'].objects.link(ob)
        ob.matrix_world = Matrix(camera_matrix(record))
        data.type = 'PERSP'; data.sensor_fit = 'VERTICAL'; data.sensor_height = 32.
        projection = bytes.fromhex(record['camera_projection'])
        require(len(projection) == 68 and projection[:4] == struct.pack('<I', 19), 'Actual Projection byte record')
        p = struct.unpack('<16f', projection[4:])
        data.lens = 16. * p[5]
        data.clip_start = record['near']; data.clip_end = record['far']
        ob['declared_transform_hex'] = record['camera_transform']
        ob['declared_projection_hex'] = record['camera_projection']
    world = bpy.data.worlds.new('L58_K_FIXED_WORLD'); world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = settings['world_linear_rgba']
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = settings['world_strength']; scene.world = world
    light = bpy.data.lights.new('L58_K_FIXED_SUN', 'SUN'); light.energy = settings['sun_energy']; light.angle = settings['sun_angle_radians']
    sun = bpy.data.objects.new(light.name, light); collections['L58_FIXED_INSPECTION'].objects.link(sun)
    sun.rotation_euler = settings['sun_source_rotation_xyz_radians']
    scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 8; scene.cycles.use_denoising = False
    scene.render.threads_mode = 'FIXED'; scene.render.threads = 2
    scene.render.resolution_x = 1179; scene.render.resolution_y = 664; scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = 1.; scene.render.pixel_aspect_y = 1.
    scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGB'; scene.render.image_settings.color_depth = '8'
    scene.render.film_transparent = False; scene.use_nodes = False
    scene.render.use_compositing = False; scene.render.use_sequencer = False
    scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0.; scene.view_settings.gamma = 1.
    scene.camera = bpy.data.objects[CAMERA_PREFIX+binding['world_cameras'][1]['name']]
    bpy.context.view_layer.update()


def capture(candidate, contract):
    import bpy
    scene = bpy.context.scene; master = bpy.data.objects[MASTER]; mesh = master.data
    names = [group.name for group in master.vertex_groups]
    memberships = [[[group.group, float(group.weight)] for group in vertex.groups] for vertex in mesh.vertices]
    weights = [[0.]*len(names) for _ in mesh.vertices]
    # Preserve raw out-of-range / duplicate memberships; validator must reject them.
    for index, entries in enumerate(memberships):
        for group, weight in entries:
            if 0 <= group < len(names):
                weights[index][group] = weight
    attributes = {}
    for name in (BASE_ATTRIBUTE, LAST_ATTRIBUTE, LOCK_ATTRIBUTE, INDEX_ATTRIBUTE, FACE_ATTRIBUTE):
        att = mesh.attributes[name]; kind = att.data_type; domain = att.domain
        values = read_collection(att.data, 'vector', 'f', 3) if kind == 'FLOAT_VECTOR' else read_collection(att.data, 'value', 'i')
        attributes[name] = dict(data_type=kind, domain=domain, values=values)
        del att
    objects = []
    for ob in sorted(bpy.data.objects, key=lambda item: item.name):
        objects.append(dict(name=ob.name, type=ob.type, matrix_world=[list(row) for row in ob.matrix_world],
                            parent=ob.parent.name if ob.parent else None,
                            modifiers=[m.type for m in ob.modifiers], constraints=[x.type for x in ob.constraints],
                            hide_render=ob.hide_render, hide_viewport=ob.hide_viewport, hidden=ob.hide_get(),
                            mesh_name=ob.data.name if ob.type == 'MESH' else None,
                            vertex_group_names=[g.name for g in ob.vertex_groups]))
    controls = []
    for row in candidate['controls']:
        ob = bpy.data.objects[CONTROL_PREFIX+row['id']]
        fields = {key:ob[key] for key in ('id', 'value', 'default', 'min', 'max', 'semantic', 'units', 'last_applied_value')}
        controls.append(dict(name=ob.name, location=list(ob.location), lock_location=list(ob.lock_location),
                             lock_rotation=list(ob.lock_rotation), lock_scale=list(ob.lock_scale), **fields))
    material = bpy.data.materials[MATERIAL]; node = material.node_tree.nodes.get('Principled BSDF')
    mat = dict(name=material.name, use_nodes=material.use_nodes,
               base_color_linear_rgba=list(node.inputs['Base Color'].default_value),
               roughness=float(node.inputs['Roughness'].default_value), metallic=float(node.inputs['Metallic'].default_value),
               backface_culling=material.use_backface_culling,
               node_types=sorted(n.bl_idname for n in material.node_tree.nodes),
               links=sorted([link.from_node.bl_idname, link.from_socket.name, link.to_node.bl_idname, link.to_socket.name]
                            for link in material.node_tree.links),
               emission_color=list(node.inputs['Emission Color'].default_value),
               emission_strength=float(node.inputs['Emission Strength'].default_value))
    cameras = []
    dependency_graph = bpy.context.evaluated_depsgraph_get()
    for ob in sorted((ob for ob in bpy.data.objects if ob.type == 'CAMERA'), key=lambda item:item.name):
        data = ob.data
        projection = ob.calc_matrix_camera(dependency_graph, x=1179, y=664, scale_x=1., scale_y=1.)
        cameras.append(dict(name=ob.name.removeprefix(CAMERA_PREFIX), matrix_world=[list(row) for row in ob.matrix_world],
                            projection_matrix=[list(row) for row in projection],
                            declared_transform_hex=ob['declared_transform_hex'], declared_projection_hex=ob['declared_projection_hex'],
                            type=data.type, sensor_fit=data.sensor_fit, sensor_height=data.sensor_height,
                            lens=data.lens, clip_start=data.clip_start, clip_end=data.clip_end))
    texts = []
    for text in sorted(bpy.data.texts, key=lambda item:item.name):
        payload = text.as_string().encode('utf-8')
        texts.append(dict(name=text.name, sha256=hashlib.sha256(payload).hexdigest(), bytes=len(payload),
                          is_in_memory=text.is_in_memory, filepath=text.filepath, use_module=text.use_module))
    bg = scene.world.node_tree.nodes['Background']; sun = bpy.data.objects['L58_K_FIXED_SUN']
    return dict(version=contract.VERSION, blender_version=list(bpy.app.version), pid=os.getpid(),
                cpu_affinity=sorted(os.sched_getaffinity(0)), opened_filepath=bpy.data.filepath,
                mesh=dict(name=mesh.name, vertices=read_collection(mesh.vertices, 'co', 'f', 3),
                          faces=[list(face.vertices) for face in mesh.polygons], group_names=names,
                          weights=weights, memberships=memberships, attributes=attributes,
                          polygon_normals=read_collection(mesh.polygons, 'normal', 'f', 3),
                          corner_normals=read_collection(mesh.corner_normals, 'vector', 'f', 3),
                          polygon_loop_counts=read_collection(mesh.polygons, 'loop_total', 'i'),
                          polygon_loop_starts=read_collection(mesh.polygons, 'loop_start', 'i'),
                          loop_vertex_indices=read_collection(mesh.loops, 'vertex_index', 'i'),
                          flat=[not x for x in read_collection(mesh.polygons, 'use_smooth', 'b')],
                          material_indices=read_collection(mesh.polygons, 'material_index', 'i'),
                          material_slots=[m.name for m in mesh.materials]),
                objects=objects, controls=controls, material=mat, cameras=cameras, texts=texts,
                canonical_mesh_shared=(master.data is bpy.data.objects[EXPORT].data),
                mesh_names=sorted(bpy.data.meshes.keys()), material_names=sorted(bpy.data.materials.keys()),
                scene_flags={key:scene[key] for key in ('source_version', 'world_integration_allowed', 'world_loaded',
                    'visual_acceptance', 'weather_acceptance', 'auto_rebuild', 'edited_after_frozen_build', 'anchor_world_json', 'scale_one')},
                settings=dict(engine=scene.render.engine, device=scene.cycles.device, samples=scene.cycles.samples,
                    denoising=scene.cycles.use_denoising, threads_mode=scene.render.threads_mode, threads=scene.render.threads,
                    resolution=[scene.render.resolution_x, scene.render.resolution_y], percentage=scene.render.resolution_percentage,
                    pixel_aspect=[scene.render.pixel_aspect_x, scene.render.pixel_aspect_y], view_transform=scene.view_settings.view_transform,
                    look=scene.view_settings.look, exposure=scene.view_settings.exposure, gamma=scene.view_settings.gamma,
                    use_nodes=scene.use_nodes, use_compositing=scene.render.use_compositing, use_sequencer=scene.render.use_sequencer,
                    transparent=scene.render.film_transparent, active_camera=scene.camera.name),
                lighting=dict(world_color=list(bg.inputs['Color'].default_value), world_strength=float(bg.inputs['Strength'].default_value),
                    sun_type=sun.data.type, sun_energy=sun.data.energy, sun_angle=sun.data.angle, sun_rotation=list(sun.rotation_euler)),
                external_libraries=[item.filepath for item in bpy.data.libraries],
                images=[dict(name=item.name, source=item.source, filepath=item.filepath) for item in bpy.data.images],
                autoexec_enabled=bpy.context.preferences.filepaths.use_scripts_auto_execute)


def identity(raw):
    return {key:value for key,value in raw.items() if key not in ('pid', 'cpu_affinity', 'opened_filepath', 'edit_probes')}


def exercise_controls(candidate, contract, baseline, out, label):
    """Mutate every actual native scalar, measure its mesh response, then restore.

    Each intermediate full raw and each probe row is fsynced before validating it.
    A failure stops this stage and preserves the altered state and raw evidence;
    no retry, resave, or optimistic restore is substituted for the failed trial.
    """
    raise ValueError(PREPARATION_BLOCKER)
    import bpy
    probes = []
    locked = candidate['locked_indices']
    for index, row in enumerate(candidate['controls']):
        handle = bpy.data.objects[CONTROL_PREFIX+row['id']]
        start = float(handle['value'])
        direction = 1. if row['max'] > start else -1.
        room = row['max']-start if direction > 0 else start-row['min']
        step = min(1., room*.25)
        require(step > 0, 'Native control needs an in-range response test')
        target = start + direction*step
        emit('control_probe.begin', id=row['id'], before=start, after=target)
        handle['value'] = target
        rebuild_from_controls()
        moved = capture(candidate, contract)
        write_json(out/(label+'-probe-'+str(index)+'-moved-raw.json'), moved, exclusive=True)
        probe = dict(id=row['id'], **{'from':start, 'to':target},
                     vertices_before=baseline['mesh']['vertices'], vertices_after=moved['mesh']['vertices'],
                     locked_before=[baseline['mesh']['vertices'][i] for i in locked],
                     locked_after=[moved['mesh']['vertices'][i] for i in locked],
                     baseline_identity_restored=False)
        write_json(out/(label+'-probe-'+str(index)+'.json'), probe)
        require(probe['vertices_after'] != probe['vertices_before'], 'Control has no actual float32 mesh response')
        require(probe['locked_after'] == probe['locked_before'], 'Control moved locked native interfaces')
        handle['value'] = start
        rebuild_from_controls()
        restored = capture(candidate, contract)
        write_json(out/(label+'-probe-'+str(index)+'-restored-raw.json'), restored, exclusive=True)
        probe['vertices_restored'] = restored['mesh']['vertices']
        probe['baseline_identity_restored'] = identity(restored) == identity(baseline)
        write_json(out/(label+'-probe-'+str(index)+'.json'), probe)
        require(probe['baseline_identity_restored'], 'Actual full source identity did not restore after scalar edit')
        probes.append(probe)
        emit('control_probe.complete', id=row['id'])
    return probes


def main(arguments=None):
    arguments = arguments if arguments is not None else (sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('build', 'verify'))
    parser.add_argument('--out', type=Path)
    parser.add_argument('--admission', type=Path)
    args = parser.parse_args(arguments)
    if args.mode is None:
        print('Inert source adapter. Explicit admitted wrapper stage is required; no native action.', flush=True)
        return 0
    # Unconditional in this frozen revision. No option, report boolean, release
    # token or synthetic candidate may bypass the missing spatial implementation.
    raise ValueError(PREPARATION_BLOCKER)
    # The following provisional integration is intentionally unreachable. It is
    # retained as source-only preparation, not represented as a working pipeline.
    require(args.out is not None and args.admission is not None, 'Only an admitted wrapper stage may execute')
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import contract58l as contract
    admission = strict_json(args.admission.read_text())
    require(admission['state'] == 'admitted_one_shot_not_complete' and admission['wrapper_pid'] == os.getppid() and
            admission['native_script_sha256'] == sha(Path(__file__)) and admission['stage'] == 'source',
            'Active parent admission and identical native source required')
    require(Path(admission['source']).resolve() == contract.SOURCE.resolve() and
            Path(admission['output']).resolve() == args.out.resolve(), 'Admitted source/output paths')
    require(admission['candidate_sha256'] == sha(contract.CANDIDATE_PATH) and
            admission['binding_sha256'] == sha(contract.BINDING_PATH), 'Admitted recipe/camera identity')
    args.out.mkdir(exist_ok=True)
    global _TELEMETRY
    _TELEMETRY = (args.out, args.mode)
    emit('python_entry', mode=args.mode)
    import bpy
    report = dict(version=contract.VERSION, mode=args.mode, pid=os.getpid(), passed=False,
                  state='started', source_saved=False, images=0, world_loaded=False,
                  world_integration_allowed=False, visual_acceptance=False)
    try:
        candidate = contract.read(contract.CANDIDATE_PATH); binding = contract.read(contract.BINDING_PATH)
        contract.check_candidate(candidate); validate_edit_schema(candidate)
        if args.mode == 'build':
            require(not contract.SOURCE.exists(), 'Never overwrite previous native source')
            create_source(candidate, binding, contract, args.out)
        else:
            require(contract.SOURCE.is_file(), 'Saved source required for separate fresh-open process')
            emit('fresh_open.begin', path=str(contract.SOURCE))
            bpy.context.preferences.filepaths.use_scripts_auto_execute = False
            bpy.ops.wm.open_mainfile(filepath=str(contract.SOURCE), load_ui=False, use_scripts=False)
            emit('fresh_open.complete', opened_filepath=bpy.data.filepath)
        emit('capture.begin')
        raw = capture(candidate, contract)
        rawpath = args.out/(args.mode+'-raw.json')
        write_json(rawpath, raw, exclusive=True)
        report.update(raw_path=str(rawpath), raw_sha256=sha(rawpath))
        write_json(args.out/(args.mode+'-result.json'), report)
        emit('raw.persisted', sha256=sha(rawpath), bytes=rawpath.stat().st_size)
        # Persist actual arrays BEFORE pure geometry/material/semantic validation.
        report['validation'] = contract.validate_raw(raw, os.getpid(), candidate=candidate)
        probes = exercise_controls(candidate, contract, raw, args.out, args.mode)
        probepath = args.out/(args.mode+'-edit-probes.json')
        write_json(probepath, probes, exclusive=True)
        report.update(edit_probes_path=str(probepath), edit_probes_sha256=sha(probepath), controls_exercised=7)
        if args.mode == 'build':
            emit('save.begin')
            bpy.ops.wm.save_as_mainfile(filepath=str(contract.SOURCE), compress=True, check_existing=True)
            report['source_saved'] = True
            emit('save.complete', sha256=sha(contract.SOURCE), bytes=contract.SOURCE.stat().st_size)
        report.update(passed=True, state='completed', source_sha256=sha(contract.SOURCE), source_bytes=contract.SOURCE.stat().st_size)
    except BaseException:
        report.update(state='failed', error=traceback.format_exc())
        raise
    finally:
        emit('native_terminal', passed=report['passed'], state=report['state'])
        write_json(args.out/(args.mode+'-result.json'), report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
