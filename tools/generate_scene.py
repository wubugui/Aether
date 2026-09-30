"""Keep Blender's exported hierarchy visible and editable in Godot."""
from pathlib import Path
import json, struct
root=Path(__file__).resolve().parents[1]
def read_glb(name):
    data=(root/'assets'/name).read_bytes();n=struct.unpack_from('<I',data,12)[0]
    return json.loads(data[20:20+n])
def mesh_names(name):
    doc=read_glb(name)
    return [n['name'].replace('.','_') for n in doc['nodes'] if 'mesh' in n]

text='''[gd_scene load_steps=22 format=3]

[ext_resource type="PackedScene" path="res://assets/world.glb" id="1"]
[ext_resource type="PackedScene" path="res://assets/airship.glb" id="2"]
[ext_resource type="PackedScene" path="res://assets/propeller.glb" id="3"]
[ext_resource type="Shader" path="res://scripts/palette.gdshader" id="4"]
[ext_resource type="Shader" path="res://scripts/sky.gdshader" id="5"]
[ext_resource type="Shader" path="res://scripts/water.gdshader" id="6"]
[ext_resource type="Shader" path="res://scripts/terrain_surface.gdshader" id="7"]
[ext_resource type="Texture2D" path="res://assets/reference.jpg" id="8"]
[ext_resource type="Texture2D" path="res://assets/clean_plate.png" id="9"]
[ext_resource type="Shader" path="res://scripts/wood_surface.gdshader" id="10"]
[ext_resource type="Shader" path="res://scripts/ocean.gdshader" id="11"]

[sub_resource type="ShaderMaterial" id="OpenOcean"]
shader = ExtResource("11")

[sub_resource type="ShaderMaterial" id="WoodSurface"]
shader = ExtResource("10")

[sub_resource type="ShaderMaterial" id="TerrainSurface"]
shader = ExtResource("7")
shader_parameter/surface_original = ExtResource("8")
shader_parameter/surface_occluded = ExtResource("9")

[sub_resource type="ShaderMaterial" id="Palette"]
shader = ExtResource("4")
shader_parameter/haze_density = 0.0

[sub_resource type="ShaderMaterial" id="DetailPalette"]
shader = ExtResource("4")
shader_parameter/haze_density = 0.00028

[sub_resource type="ShaderMaterial" id="ShipPalette"]
shader = ExtResource("4")
shader_parameter/haze_density = 0.0

[sub_resource type="ShaderMaterial" id="SkyMaterial"]
shader = ExtResource("5")

[sub_resource type="Sky" id="Sky"]
sky_material = SubResource("SkyMaterial")

[sub_resource type="Environment" id="Environment"]
background_mode = 2
sky = SubResource("Sky")

[sub_resource type="ShaderMaterial" id="Water"]
shader = ExtResource("6")

[node name="BlenderWorld" type="Node3D"]

[node name="Daylight" type="WorldEnvironment" parent="."]
environment = SubResource("Environment")

[node name="Landscape" parent="." instance=ExtResource("1")]
'''
for i,name in enumerate(mesh_names('world.glb')):
    material='OpenOcean' if name=='OpenOcean' else 'TerrainSurface' if name in ['Water','Terrain','ForegroundCliffs','SnowRange'] else 'DetailPalette' if name in ['Groves','Hamlets'] else 'Palette'
    text+=f'\n[node name="{name}" parent="Landscape/Landscape" index="{i}"]\nmaterial_override = SubResource("{material}")\n'
    if name=='Paths':text+='visible = false\n'
text+='''
[node name="Airship" type="Node3D" parent="."]
position = Vector3(-4.15,136.8,184)
rotation = Vector3(0,0.2268928,0)

[node name="Model" parent="Airship" instance=ExtResource("2")]
'''
for i,name in enumerate(mesh_names('airship.glb')):
    material='WoodSurface' if name=='Gondola' else 'ShipPalette'
    text+=f'\n[node name="{name}" parent="Airship/Model/Airship" index="{i}"]\nmaterial_override = SubResource("{material}")\n'
text+='''
[node name="Propeller" parent="Airship" instance=ExtResource("3")]
position = Vector3(7.3,3.6,0)
rotation = Vector3(0.15,0.34906585,0)
scale = Vector3(1.13,1.13,1.13)

[node name="Propeller_001" parent="Airship/Propeller/Propeller" index="0"]
material_override = SubResource("ShipPalette")

[node name="ReferenceCamera" type="Camera3D" parent="."]
position = Vector3(0,145,250)
rotation = Vector3(-0.0610865,0,0)
current = true
fov = 50.0
near = 0.3
far = 25000.0

[editable path="Landscape"]
[editable path="Airship/Model"]
[editable path="Airship/Propeller"]
'''
(root/'scenes/three_dimensional_preview.tscn').write_text(text,encoding='utf-8')
print('Godot scene generated with editable Blender mesh instances')
