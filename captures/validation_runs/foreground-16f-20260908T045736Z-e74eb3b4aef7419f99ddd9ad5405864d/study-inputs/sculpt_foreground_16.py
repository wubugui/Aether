"""Sculpt independent foreground candidates from the verified native assets.

Sparse screen measurements set fixed world-space controls. All sides and the
original seated boundary remain real geometry; Godot owns world assembly.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
LABEL = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else '16a'
assert LABEL in ('16a', '16b', '16c', '16d', '16e', '16f')
OUT = ROOT / 'captures' / ('foreground_study_' + LABEL)
assert not OUT.exists(), OUT
OUT.mkdir()
shutil.copy2(__file__, OUT / 'sculpt_foreground_16.py')
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
if LABEL in ('16b', '16c', '16d', '16e', '16f'):
    # Keep the native peak/upper-rock outline. The new shelf below supplies
    # the actual slope break instead of extending meadow onto that outline.
    controls['cliff_crown'] = {
        8: (1278, 720, 3), 9: (1308, 726, 14), 10: (1345, 720, 23),
        11: (1382, 731, 12), 12: (1413, 709, 8), 13: (1440, 699, 4),
        14: (1471, 718, 3),
    }
    controls['cliff_central_wall'].update({
        6: (1323, 842, -1), 7: (1363, 856, -4), 8: (1404, 859, 1),
        10: (1282, 768, 0), 11: (1315, 758, -2),
        12: (1355, 766, -4), 13: (1390, 779, 1),
        17: (1357, 719, -4), 18: (1393, 728, -1),
    })
if LABEL in ('16d', '16e', '16f'):
    # Retract the hanging brow to behind its existing toe. Broaden the
    # shoulder toward the rear with a deeper, complete peak, not an overhang.
    controls['cliff_crown'] = {
        8: (1278, 720, 0), 9: (1308, 726, 0), 10: (1345, 720, 0),
        11: (1382, 731, 0), 12: (1413, 709, 0), 13: (1440, 699, 0),
        14: (1471, 718, 0),
        16: (1290, 694.5, -6), 17: (1336, 662.5, -10),
        18: (1370, 641.5, -14), 19: (1398, 623.5, -16),
        20: (1425, 626.5, -14), 21: (1447, 632.5, -10),
        22: (1466.9, 671.5, -6), 23: (1497.9, 683.5, -4),
    }
if LABEL == '16f':
    controls['cliff_central_wall'].update({
        15: (1281, 751, -3), 16: (1314, 743, -3),
        17: (1357, 745, -4), 18: (1393, 753, -1),
    })


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
        if LABEL in ('16c', '16d', '16e', '16f') and name == 'cliff_crown' and 8 <= index <= 14:
            # Author a coherent cross-slope instead of the 6.65 m drop
            # between the third and fourth columns of 16b's grass shelf.
            heights = [61.2, 64.5, 65., 64.5, 63., 61.28, 56.46] if LABEL == '16c' else [58., 57.5, 58., 58.5, 59.5, 60., 56.46]
            target[1] = heights[index - 8]
        mesh.vertices[index].co = (target[0], -target[2], target[1])
        changes.append({'index': index, 'before': old.tolist(), 'after': list(mesh.vertices[index].co),
                        'survey_uv': [u, v], 'depth_offset_m': delta_z,
                        'world_height_override': float(target[1] + origin[1]) if LABEL in ('16c', '16d', '16e', '16f') and name == 'cliff_crown' and 8 <= index <= 14 else None})
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
                role = 0 if LABEL == '16a' and strip in (0, 1, 2, 6) else 1
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
    shelf_controls = []
    wall_bench_controls = []
    wall_bend_controls = []
    if LABEL in ('16b', '16c', '16d', '16e', '16f') and name == 'cliff_crown':
        bm.verts.ensure_lookup_table()
        front = [bm.verts[index] for index in range(8, 16)]
        ridge = [bm.verts[index] for index in range(16, 24)]
        upper = set(front + ridge)
        strip_faces = [face for face in bm.faces if set(face.verts) <= upper
                       and set(face.verts) & set(front) and set(face.verts) & set(ridge)]
        assert len(strip_faces) == 14
        shelf = []
        for index, (a, b) in enumerate(zip(front, ridge)):
            edge = bm.edges.get((a, b))
            assert edge is not None
            _, vertex = bmesh.utils.edge_split(edge, a, .5)
            width_fraction = [.55, .70, .75, .74, .66, .58, .52, .45][index] if LABEL in ('16c', '16d', '16e', '16f') else .62
            rise = 2. if LABEL in ('16c', '16d', '16e', '16f') and index < 6 else [2., 3., 2.5, 3.5, 2.5, 2., 1.5, 1.][index]
            point = a.co.lerp(b.co, width_fraction)
            point.z = min(a.co.z + rise, b.co.z - .5)
            vertex.co = point
            shelf.append(vertex)
            shelf_controls.append({'column': index, 'front_blender_xyz': list(a.co),
                                   'shelf_blender_xyz': list(point), 'ridge_blender_xyz': list(b.co),
                                   'width_fraction': width_fraction})
        bmesh.ops.delete(bm, geom=strip_faces, context='FACES_ONLY')
        zone_layer = bm.faces.layers.int.get('Geological section')
        added_layer = bm.faces.layers.int.new('16b added shelf')
        for index in range(7):
            for vertices, role in (([front[index], front[index + 1], shelf[index + 1], shelf[index]], 0),
                                   ([shelf[index], shelf[index + 1], ridge[index + 1], ridge[index]], 1)):
                face = bm.faces.new(vertices)
                face[zone_layer] = role
                face[added_layer] = 1
        unused = [edge for edge in bm.edges if not edge.link_faces]
        if unused:
            bmesh.ops.delete(bm, geom=unused, context='EDGES')
        bmesh.ops.triangulate(bm, faces=[face for face in bm.faces if len(face.verts) > 3])
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if LABEL in ('16e', '16f') and name == 'cliff_central_wall':
        bm.verts.ensure_lookup_table()
        middle = [bm.verts[index] for index in range(5, 10)]
        front = [bm.verts[index] for index in range(10, 15)]
        strip = set(middle + front)
        strip_faces = [face for face in bm.faces if set(face.verts) <= strip
                       and set(face.verts) & set(middle) and set(face.verts) & set(front)]
        assert len(strip_faces) == 8
        lower, upper = [], []
        for index, (a, b) in enumerate(zip(middle, front)):
            edge = bm.edges.get((a, b))
            assert edge is not None
            _, lo = bmesh.utils.edge_split(edge, a, .33)
            hi = None
            if LABEL == '16e':
                _, hi = bmesh.utils.edge_split(bm.edges.get((lo, b)), lo, .5)
            point = a.co.lerp(b.co, .52)
            point.z = ([41., 40., 36., 39., 32.] if LABEL == '16e' else [40., 41., 36., 39., 32.])[index]
            point.y += ([-0., -1.5, 0., -1., 0.] if LABEL == '16e' else [0., 0., 3., 0., 0.])[index]
            lo.co = point
            lower.append(lo)
            if hi is not None:
                hi.co = point + Vector((0., [1., 3., 5., 3., 1.][index], 1.25))
                upper.append(hi)
                wall_bench_controls.append({'column': index, 'middle_blender_xyz': list(a.co),
                    'lower_blender_xyz': list(lo.co), 'upper_blender_xyz': list(hi.co),
                    'front_blender_xyz': list(b.co), 'bench_depth_m': [1., 3., 5., 3., 1.][index]})
            else:
                wall_bend_controls.append({'column': index, 'middle_blender_xyz': list(a.co),
                    'bend_blender_xyz': list(lo.co), 'front_blender_xyz': list(b.co)})
        bmesh.ops.delete(bm, geom=strip_faces, context='FACES_ONLY')
        zone_layer = bm.faces.layers.int.get('Geological section')
        added_layer = bm.faces.layers.int.new('Authored wall break')
        for index in range(4):
            pairs = ((middle, lower), (lower, upper), (upper, front)) if LABEL == '16e' else ((middle, lower), (lower, front))
            for a, b in pairs:
                face = bm.faces.new([a[index], a[index + 1], b[index + 1], b[index]])
                face[zone_layer] = 1
                face[added_layer] = 1
        unused = [edge for edge in bm.edges if not edge.link_faces]
        if unused:
            bmesh.ops.delete(bm, geom=unused, context='EDGES')
        bmesh.ops.triangulate(bm, faces=[face for face in bm.faces if len(face.verts) > 3])
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(len(edge.link_faces) == 2 for edge in bm.edges), 'Non-manifold ' + name
    assert all(face.calc_area() > 1e-8 for face in bm.faces), 'Degenerate ' + name
    volume = bm.calc_volume(signed=True)
    assert volume > 0, name
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    if LABEL in ('16b', '16c', '16d', '16e', '16f') and name == 'cliff_crown':
        zones = mesh.attributes['Geological section']
        colors = mesh.color_attributes['Palette']
        for face in mesh.polygons:
            if not mesh.attributes['16b added shelf'].data[face.index].value:
                continue
            light = max(0, face.normal.dot(sun))
            role = zones.data[face.index].value
            color = pigment('a6ac70') * (.86 + .16 * light) if role == 0 else pigment('96928e') * (1 - light) + pigment('c4bcaf') * light
            for loop in face.loop_indices:
                colors.data[loop].color = (*linear(color), 1)
    if LABEL in ('16e', '16f') and name == 'cliff_central_wall':
        colors = mesh.color_attributes['Palette']
        for face in mesh.polygons:
            if not mesh.attributes['Authored wall break'].data[face.index].value:
                continue
            light = max(0, face.normal.dot(sun))
            color = pigment('606b75') * (1 - light) + pigment('a6aaa2') * light
            for loop in face.loop_indices:
                colors.data[loop].color = (*linear(color), 1)
    fresh = np.array([vertex.co[:] for vertex in mesh.vertices])
    fresh_points = {tuple(point) for point in fresh}
    assert all(tuple(prior[index]) in fresh_points for index in rim | floor)
    obj['study_version'] = LABEL
    obj['source_native_sha256'] = source_hash
    obj['closed_volume_m3'] = volume
    obj['production_modified'] = False
    obj.vertex_groups.new(name=LABEL + ' authored shelf and gully controls').add(list(edits), 1, 'REPLACE')
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
                    'shelf_controls': shelf_controls,
                    'wall_bench_controls': wall_bench_controls,
                    'wall_bend_controls': wall_bend_controls,
                    'repainted_faces': changed_faces, 'production_modified': False,
                    'validation_scope': 'Closed edge incidence, positive volume, face area and unchanged native rim/floor. Not a self-intersection or gameplay verdict.'})
    print('FOREGROUND CANDIDATE ' + name, flush=True)
(OUT / 'manifest.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
print('FOREGROUND BUILD COMPLETE ' + str(OUT), flush=True)
