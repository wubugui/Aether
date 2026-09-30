"""A second actual-volume study with irregular inner faces and a thinner shelf."""
from pathlib import Path
root=Path('D:/test6'); p=root/'captures'
s=(p/'model_cloud_14a.py').read_text(encoding='utf-8').replace('14a','14b')
s=s.replace('center = (top + bottom) * .5', 'top -= 1.8 * max(0, min(1, (top - 10) / 25))\n    bottom += 5.5 * max(0, min(1, (x + 50) / 35)) * max(0, min(1, (85 - x) / 25))\n    center = (top + bottom) * .5')
s=s.replace('lateral = 0 if j in (0, 4) else math.sin(i * 2.31 + j * 1.44) * min(2.5, radius * .2)', 'lateral = 0 if j in (0, 4) else math.sin(i * 2.31 + j * 1.44) * min(4.5, radius * .3)')
s=s.replace('y = center + radius * math.cos(angle)', 'y = center + radius * math.cos(angle)\n        if j not in (0, 4): y += math.sin(i * 3.41 + j * 2.26) * min(4.8, radius * .3)')
s=s.replace('z = depth * math.sin(angle) * (1.0 if j < 4 else .88)', 'z = depth * math.sin(angle) * (1.0 if j < 4 else .88)\n        if j not in (0, 4): z *= 1 + math.sin(i * 1.13 + j * 2.11) * .19')
dest=p/'model_cloud_14b.py';assert not dest.exists();dest.write_text(s,encoding='utf-8')
preview=(p/'preview_cloud_14a.gd').read_text(encoding='utf-8').replace('14a','14b')
preview=preview.replace('var prior:Node3D=asset.get_node("Model")', 'var material:=ShaderMaterial.new();material.shader=load("res://captures/cloud_surface_14b.gdshader");asset.surface_material=material\n\t\tvar prior:Node3D=asset.get_node("Model")')
(p/'preview_cloud_14b.gd').write_text(preview,encoding='utf-8')
shader=(root/'scripts/cloud_surface.gdshader').read_text(encoding='utf-8')
shader=shader.replace('vec3(.83,.800,.807),vec3(.98,.950,.930)','vec3(.87,.835,.825),vec3(1.,.97,.94)').replace('(sunlight-.4)*.022','(sunlight-.4)*.095')
(p/'cloud_surface_14b.gdshader').write_text(shader,encoding='utf-8')
print('14b native cloud geometry and material candidate authored')
