"""Assemble the editable Godot game from the Blender exports."""
from pathlib import Path
import struct,json
ROOT=Path(__file__).resolve().parents[1]
def names(file):
    d=(ROOT/'assets'/file).read_bytes();n=struct.unpack_from('<I',d,12)[0]
    data=json.loads(d[20:20+n]);return [p['name'].replace('.','_') for p in data['nodes'] if 'mesh' in p]
scene='''[gd_scene load_steps=16 format=3]
[ext_resource type="Script" path="res://scripts/game.gd" id="1"]
[ext_resource type="Script" path="res://scripts/open_world.gd" id="2"]
[ext_resource type="PackedScene" path="res://assets/open_world.glb" id="3"]
[ext_resource type="PackedScene" path="res://assets/airship.glb" id="4"]
[ext_resource type="PackedScene" path="res://assets/propeller.glb" id="5"]
[ext_resource type="Material" path="res://materials/world.tres" id="6"]
[ext_resource type="Shader" path="res://scripts/open_sky.gdshader" id="7"]
[ext_resource type="Material" path="res://materials/ship.tres" id="8"]
[ext_resource type="Material" path="res://materials/flag.tres" id="9"]

[sub_resource type="ShaderMaterial" id="SkyMaterial"]
shader = ExtResource("7")
[sub_resource type="Sky" id="Sky"]
sky_material = SubResource("SkyMaterial")
[sub_resource type="Environment" id="Environment"]
background_mode = 2
sky = SubResource("Sky")
ambient_light_source = 3
ambient_light_color = Color(0.84,0.91,1,1)
ambient_light_energy = 0.60
reflected_light_source = 2
tonemap_mode = 0
fog_enabled = true
fog_light_color = Color(0.76,0.85,0.89,1)
fog_light_energy = 1.0
fog_density = 0.00017
fog_sky_affect = 0.0

[sub_resource type="CapsuleShape3D" id="EnvelopeCollision"]
radius = 3.4
height = 13.8
[sub_resource type="BoxShape3D" id="HullCollision"]
size = Vector3(8.3,3.1,2.8)

[node name="Skyfarer" type="Node3D"]
script = ExtResource("1")
[node name="Environment" type="WorldEnvironment" parent="."]
environment = SubResource("Environment")
[node name="Sun" type="DirectionalLight3D" parent="."]
rotation_degrees = Vector3(-58,-42,0)
light_color = Color(1,0.97,0.89,1)
light_energy = 0.85
shadow_enabled = true
shadow_opacity = 0.55
directional_shadow_max_distance = 2000.0
directional_shadow_mode = 2

[node name="World" type="Node3D" parent="."]
script = ExtResource("2")
[node name="Terrain" parent="World" instance=ExtResource("3")]

[node name="Airship" type="CharacterBody3D" parent="."]
position = Vector3(-4.15,136.8,184)
rotation = Vector3(0,0.2268928,0)
collision_layer = 2
collision_mask = 1
motion_mode = 1
max_slides = 8
safe_margin = 0.07
[node name="EnvelopeCollision" type="CollisionShape3D" parent="Airship"]
position = Vector3(0,5,0)
rotation = Vector3(0,0,1.5707963)
shape = SubResource("EnvelopeCollision")
[node name="HullCollision" type="CollisionShape3D" parent="Airship"]
position = Vector3(0,-2.3,0)
shape = SubResource("HullCollision")
[node name="Visuals" type="Node3D" parent="Airship"]
[node name="Model" parent="Airship/Visuals" instance=ExtResource("4")]
'''
for i,name in enumerate(names('airship.glb')):
    material='9' if name=='Flag' else '8'
    scene+=f'\n[node name="{name}" parent="Airship/Visuals/Model/Airship" index="{i}"]\nmaterial_override = ExtResource("{material}")\n'
scene+='''
[node name="Propeller" parent="Airship/Visuals" instance=ExtResource("5")]
position = Vector3(7.3,3.6,0)
rotation = Vector3(0.15,0.34906585,0)
scale = Vector3(1.13,1.13,1.13)
[node name="Propeller_001" parent="Airship/Visuals/Propeller/Propeller" index="0"]
material_override = ExtResource("8")

[node name="Camera" type="Camera3D" parent="."]
position = Vector3(0,145,250)
rotation_degrees = Vector3(-3.5,0,0)
current = true
fov = 50.0
near = 0.35
far = 18000.0

[editable path="World/Terrain"]
[editable path="Airship/Visuals/Model"]
[editable path="Airship/Visuals/Propeller"]
'''
(ROOT/'scenes/game.tscn').write_text(scene,encoding='utf-8')
print('Game scene assembled from independent 3D assets')
