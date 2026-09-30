"""Use the unshaded color output; require actual runtime volume bindings."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/lantern_volume_28b.gdshader').read_text(encoding='utf-8')
assert s.count('ALBEDO=vec3(0.);EMISSION=warm_color*light_energy;')==1
s=s.replace('ALBEDO=vec3(0.);EMISSION=warm_color*light_energy;', '// Unshaded Compatibility uses ALBEDO as final color.\n    ALBEDO=warm_color*light_energy;EMISSION=vec3(0.);')
(R/'captures/lantern_volume_28e.gdshader').write_text(s,encoding='utf-8')
a=(R/'captures/lantern_lighting_28b.gd').read_text(encoding='utf-8')
a=a.replace(' -> void:\n\tfor mesh in node.find_children', ' -> Array:\n\tvar records:Array=[]\n\tfor mesh in node.find_children')
a=a.replace('func configure(game:', '\t\trecords.append({"path":str(mesh.get_path()),"visible":mesh.is_visible_in_tree(),"layers":mesh.layers,"surfaces":mesh.mesh.get_surface_count(),"kind":kind,"energy":material.get_shader_parameter("light_energy"),"shader_sha256":volume_shader.code.sha256_text()})\n\tassert(records.size()==1,"Exactly one native mesh per optical asset")\n\treturn records\nfunc configure(game:')
a=a.replace('assign_volume(beam,0.,occlusion.texture)', 'var beam_meshes:=assign_volume(beam,0.,occlusion.texture)')
a=a.replace('assign_volume(halo,1.,occlusion.texture)', 'var halo_meshes:=assign_volume(halo,1.,occlusion.texture)')
a=a.replace('"halo_asset":"lantern_halo.glb",', '"halo_asset":"lantern_halo.glb","beam_meshes":beam_meshes,"halo_meshes":halo_meshes,')
(R/'captures/lantern_lighting_28e.gd').write_text(a,encoding='utf-8')
d=(R/'tools/render_lantern_lighting_28b.py').read_text(encoding='utf-8').replace('28b','28e')
d=d.replace('28e disables hardware depth testing for the volume backfaces, retaining explicit fragment scene-depth clipping.', '28e fixes unshaded final color routing to ALBEDO; records and requires one actual bound mesh for each beam and halo. Retains explicit scene depth clipping with hardware depth disabled.')
(R/'tools/render_lantern_lighting_28e.py').write_text(d,encoding='utf-8')
