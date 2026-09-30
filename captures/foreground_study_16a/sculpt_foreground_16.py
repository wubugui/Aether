"""Sculpt independent foreground candidates from the verified native assets.

Sparse screen measurements set fixed world-space controls. All sides and the
original seated boundary remain real geometry; Godot owns world assembly.
"""
from pathlib import Path
import hashlib
import json
import math
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
LABEL = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else '16a'
assert LABEL == '16a'
OUT = ROOT / 'captures' / ('foreground_study_' + LABEL)
assert not OUT.exists(), OUT
OUT.mkdir()
catalog = {item['name']: item for item in json.loads((ROOT / 'assets/cliff_kit.json').read_text())}
focal = 941 / (2 * math.tan(math.radians(25)))
pitch = math.radians(-3.526)
camera = np.array([0., 145., 250.])
sun = Vector((-.48, -.30, .82)).normalized()

# Values are (pixel x, pixel y, extra world depth towards the observer).
# Rim/floor points are excluded. The broad upper shelves and middle walls
# acquire distinct depth and unequal crest heights instead of aligned strips.
controls = {
    'cliff_crown': {
        8: (1278, 720, 3), 9: (1308, 726, 9), 10: (1345, 712, 12),
        11: (1382, 731, 6), 12: (1413, 709, 8), 13: (1440, 699, 4),
        14: (1471, 718, 3),
        17: (1334, 674, -2), 18: (1366, 649, -3),
        20: (1427, 639, -2), 21: (1448, 648, -3),
    },
    'cliff_front_columns': {
        4: (1168, 818, 0), 5: (1219, 818, 3),
        6: (1275, 839, -3), 7: (1327, 821, 0),
        9: (1218, 761, 2), 10: (1272, 749, -2),
        13: (1198, 726, 2), 14: (1254, 719, 1),
    },
    'cliff_central_wall': {
        6: (1320, 846, -2), 7: (1352, 866, -7), 8: (1399, 857, 2),
        10: (1282, 776, -1), 11: (1313, 761, -5),
        12: (1344, 786, -8), 13: (1383, 773, 2),
        15: (1281, 733, -3), 16: (1314, 716, -3),
        17: (1351, 730, -8), 18: (1393, 717, -2),
    },
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pigment(hexadecimal):
    return np.array([int(hexadecimal[index:index + 2], 16) / 255 for index in (0, 2, 4)])


def linear(value):
    return np.where(value <= .04045, value / 12.92, ((value + .055) / 1.055) ** 2.4)


def at_depth(u, v, depth):
    y = (470.5 - v) / focal
    ray = np.array([(u - 836) / focal, math.cos(pitch) * y + math.sin(pitch),
                    math.sin(pitch) * y - math.cos(pitch)])
    return camera + ray * ((depth - camera[2]) / ray[2])


records = []
for name, edits in controls.items():
    item = catalog[name]
    source = ROOT / item['native_source']
    source_hash = sha(source)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    obj = bpy.data.objects[name]
    assert np.allclose(np.array(obj.matrix_world), np.eye(4)), name
    mesh = obj.data
    prior = np.array([vertex.co[:] for vertex in mesh.vertices])
    origin = np.array(item['position'])
    floor = {v.index for v in mesh.vertices if v.co.z < -14}
    rim = set()
    for edge in mesh.edges:
        a, b = edge.vertices
        if (a in floor) != (b in floor):
            upper, lower = (b, a) if a in floor else (a, b)
            if np.linalg.norm(prior[upper, :2] - prior[lower, :2]) < .001:
                rim.add(upper)
    assert rim and not (set(edits) & (rim | floor)), name
    changes = []
    for index, (u, v, delta_z) in edits.items():
        old = prior[index]
        world = np.array([old[0], old[2], -old[1]]) + origin
        target = at_depth(u, v, world[2] + delta_z) - origin
        mesh.vertices[index].co = (target[0], -target[2], target[1])
        changes.append({'index': index, 'before': old.tolist(), 'after': list(mesh.vertices[index].co),
                        'target_uv': [u, v], 'depth_offset_m': delta_z})
    mesh.update()
    zones = mesh.attributes['Geological section']
    colors = mesh.color_attributes['Palette']
    changed_faces = []
    for face in mesh.polygons:
        indices = set(face.vertices)
        role = zones.data[face.index].value
        if name == 'cliff_crown':
            # The old nearly vertical foot-to-front face was painted grass.
            # Put meadow on the now deeper upper left shelf, with rock below.
            if indices <= set(range(16)) and indices & set(range(8)) and indices & set(range(8, 16)):
                role = 1
            if indices <= set(range(8, 24)) and indices & set(range(8, 16)) and indices & set(range(16, 24)):
                strip = min(index % 8 for index in indices)
                role = 0 if strip in (0, 1, 2, 6) else 1
        if not (indices & set(edits)) and role == zones.data[face.index].value:
            continue
        zones.data[face.index].value = role
        light = max(0, face.normal.dot(sun))
        if role == 0:
            tone = {'cliff_crown': '9fa969', 'cliff_front_columns': 'abb67c',
                    'cliff_central_wall': 'a4ad73'}[name]
            color = pigment(tone) * (.86 + .16 * light)
        elif role == 2:
            color = pigment('949f74') * (.71 + .25 * light)
        elif name == 'cliff_central_wall':
            color = pigment('606b75') * (1 - light) + pigment('a6aaa2') * light
        else:
            color = pigment('96928e') * (1 - light) + pigment('c4bcaf') * light
        for loop in face.loop_indices:
            colors.data[loop].color = (*linear(color), 1)
        changed_faces.append(face.index)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    assert all(len(edge.link_faces) == 2 for edge in bm.edges), 'Non-manifold ' + name
    assert all(face.calc_area() > 1e-8 for face in bm.faces), 'Degenerate ' + name
    volume = bm.calc_volume(signed=True)
    assert volume > 0, name
    bm.free()
    fresh = np.array([vertex.co[:] for vertex in mesh.vertices])
    assert np.array_equal(prior[sorted(rim | floor)], fresh[sorted(rim | floor)])
    obj['study_version'] = LABEL
    obj['source_native_sha256'] = source_hash
    obj['closed_volume_m3'] = volume
    obj['production_modified'] = False
    obj.vertex_groups.new(name='16a authored shelf and gully controls').add(list(edits), 1, 'REPLACE')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    glb = OUT / (name + '.glb')
    native = OUT / (name + '.blend')
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format='GLB', use_selection=True,
                              export_apply=True, export_vertex_color='ACTIVE')
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    assert sha(source) == source_hash, 'Source modified ' + name
    records.append({'name': name, 'path': str(glb.relative_to(ROOT)),
                    'native_source': str(native.relative_to(ROOT)), 'source_sha256': source_hash,
                    'glb_sha256': sha(glb), 'blend_sha256': sha(native),
                    'vertices': len(mesh.vertices), 'triangles': len(mesh.polygons),
                    'volume_m3': volume, 'unchanged_rim_vertices': len(rim),
                    'unchanged_floor_vertices': len(floor), 'controls': changes,
                    'repainted_faces': changed_faces, 'production_modified': False,
                    'validation_scope': 'Closed edge incidence, positive volume, face area and unchanged native rim/floor. Not a self-intersection or gameplay verdict.'})
    print('FOREGROUND CANDIDATE ' + name, flush=True)
(OUT / 'manifest.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
print('FOREGROUND BUILD COMPLETE ' + str(OUT), flush=True)
