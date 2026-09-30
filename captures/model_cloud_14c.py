"""An independent full cloud volume, authored as unequal cross sections in Blender.

The world placement stays in Godot. Every section has actual front/back depth;
this asset has no camera-facing surfaces, images, or runtime deformation mask.
"""
from pathlib import Path
import bpy, bmesh, math, json, hashlib

ROOT = Path('D:/test6')
OUT = ROOT / 'captures/cloud_study_14c'
assert not OUT.exists()
OUT.mkdir()
bpy.ops.wm.read_factory_settings(use_empty=True)

# Local Godot coordinates: longitudinal x, top/bottom y, depth radius z.
# A high main turret, shallow west shoulder and flattened low shelf.
sections = [
    (-79, -8, -9, .6), (-61, -8, -14, 8),
    (-47, 3, -16, 13), (-36, 11, -19, 18),
    (-26, 12, -19, 19), (-14, 7, -20, 17),
    (-6, 22, -22, 19), (8, 34, -24, 24),
    (25, 40, -26, 28), (39, 35, -25, 28),
    (48, 26, -22, 25), (52, 10, -19, 22),
    (64, 6, -19, 19), (75, -3, -22, 15),
    (84, -15, -20, 6), (88, -18, -18.3, .4),
]
angles = [0, 39, 86, 140, 180, 220, 274, 322]
vertices, faces = [], []
for i, (x, top, bottom, depth) in enumerate(sections):
    top -= 1.8 * max(0, min(1, (top - 10) / 25))
    bottom += 5.5 * max(0, min(1, (x + 50) / 35)) * max(0, min(1, (85 - x) / 25))
    center = (top + bottom) * .5
    radius = (top - bottom) * .5
    for j, degrees in enumerate(angles):
        angle = math.radians(degrees + (0 if j in (0, 4) else math.sin(i * 1.73 + j) * 5))
        # The west/east inner faces do not form repeated straight bands.
        lateral = 0 if j in (0, 4) else math.sin(i * 2.31 + j * 1.44) * min(4.5, radius * .3)
        y = center + radius * math.cos(angle)
        if j not in (0, 4):
            y += math.sin(i * 3.41 + j * 2.26) * min(4.8, radius * .3)
            y = max(bottom + radius * .03, min(top - radius * .03, y))
        z = depth * math.sin(angle) * (1.0 if j < 4 else .88)
        if j not in (0, 4): z *= 1 + math.sin(i * 1.13 + j * 2.11) * .19
        # Blender z-up conversion. Positive Godot z is the near side.
        vertices.append((x + lateral, -z, y))
    if i:
        for j in range(8):
            a, b = (i - 1) * 8 + j, (i - 1) * 8 + (j + 1) % 8
            c, d = i * 8 + (j + 1) % 8, i * 8 + j
            faces.extend([(a, b, d), (b, c, d)] if (i + j) % 2 else [(a, b, c), (a, c, d)])
faces.extend([tuple(reversed(range(8))), tuple(range((len(sections) - 1) * 8, len(sections) * 8))])
mesh = bpy.data.meshes.new('Cumulus turret shoulder and shelf')
mesh.from_pydata(vertices, [], faces)
mesh.update()
obj = bpy.data.objects.new('cloud_primary', mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
for label, indices in [('West shoulder', range(0, 6)), ('Main rising turret', range(6, 11)), ('East lower shelf', range(11, 16))]:
    group = obj.vertex_groups.new(name=label)
    group.add([i * 8 + j for i in indices for j in range(8)], 1, 'REPLACE')
bm = bmesh.new(); bm.from_mesh(mesh)
bmesh.ops.triangulate(bm, faces=list(bm.faces))
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
assert all(len(edge.link_faces) == 2 for edge in bm.edges)
assert min(face.calc_area() for face in bm.faces) > 1e-7
volume = bm.calc_volume(signed=True)
assert volume > 0
bm.to_mesh(mesh); bm.free(); mesh.update()
for face in mesh.polygons:
    face.use_smooth = False
material = bpy.data.materials.new('Cloud warm white volume')
material.diffuse_color = (.84, .84, .83, 1)
material.use_nodes = True
bsdf = material.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (.84, .84, .83, 1)
bsdf.inputs['Roughness'].default_value = 1
mesh.materials.append(material)
obj['authoring'] = 'Complete lofted cloud volume with unequal depth and editable section vertex groups'
obj['world_assembly'] = 'Godot World/Clouds; existing independent prefab and instance transform'
obj['closed_volume_m3'] = volume
target = OUT / 'cloud_primary.glb'
bpy.ops.export_scene.gltf(filepath=str(target), export_format='GLB', use_selection=True, export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'cloud_primary.blend'))
item = {'name': 'cloud_primary', 'instance': 'cloud_primary_57323', 'vertices': len(mesh.vertices),
        'triangles': len(mesh.polygons), 'volume_m3': volume,
        'glb_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'blend_sha256': hashlib.sha256((OUT / 'cloud_primary.blend').read_bytes()).hexdigest(),
        'production_modified': False}
(OUT / 'manifest.json').write_text(json.dumps([item], indent=2), encoding='utf-8')
print(json.dumps(item), flush=True)
