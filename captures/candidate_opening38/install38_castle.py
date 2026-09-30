# -*- coding: utf-8 -*-
# 38b: swap castle_57174 in World38 to the round-37c pale limestone castle (copied to
# captures/candidate_opening38/castle37c.tscn), same position, unit scale, world.tres surface.
# Mirrors tools/render_crownreach37c.gd (position kept, old non-uniform scale dropped).
import io, json, hashlib
P = 'E:/FeiTing/captures/candidate_opening38/World38.tscn'
s = io.open(P, 'r', encoding='utf-8', newline='').read()
NL = u'\r\n' if u'\r\n' in s else u'\n'
ext = u'[ext_resource type="PackedScene" path="res://scenes/prefabs/massif_west_foothill.tscn" id="973_g3t0o"]' + NL
assert s.count(ext) == 1, s.count(ext)
s = s.replace(ext, ext + u'[ext_resource type="PackedScene" path="res://captures/candidate_opening38/castle37c.tscn" id="974_c37c"]' + NL)
old = NL.join([u'[node name="castle_57174" type="Node3D" parent="Settlements" instance=ExtResource("230_0opms")]',
               u'transform = Transform3D(1.2, 0, 0, 0, 0.52, 0, 0, 0, 0.78, 43.288, 18.845, -282.521)',
               u'script = ExtResource("3_ktl4m")', u'asset_kind = "castle"',
               u'surface_material = SubResource("ShaderMaterial_3ao56")']) + NL
new = NL.join([u'[node name="castle_57174" type="Node3D" parent="Settlements" instance=ExtResource("974_c37c")]',
               u'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 43.288, 18.845, -282.521)',
               u'script = ExtResource("3_ktl4m")', u'asset_kind = "castle"',
               u'surface_material = ExtResource("953_iwn5p")']) + NL
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
R = 'E:/FeiTing/captures/candidate_opening38/install-report.json'
r = json.load(open(R))
r['castle_swap'] = {
    'castle_scene': 'res://captures/candidate_opening38/castle37c.tscn',
    'castle_scene_source': 'captures/validation_runs/crownreach37c-20260909T034026Z-7c438c3cd6cd4a1b91e20b5a38d86321/images/castle37c.tscn',
    'castle_scene_sha256': hashlib.sha256(open('E:/FeiTing/captures/candidate_opening38/castle37c.tscn', 'rb').read()).hexdigest(),
    'world38_sha256_after': hashlib.sha256(s.encode('utf-8')).hexdigest(),
    'note': 'castle_57174 instance swapped to 37c castle, transform scale 1 at same origin, surface world.tres'}
json.dump(r, open(R, 'w'), indent=1)
print('ok newline=%r' % NL)
