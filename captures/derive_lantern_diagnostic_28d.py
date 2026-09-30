from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
old=R/'captures/validation_runs/lantern-diagnostic-28c-20260908T160251Z-c743ec0d33cd491f939180c70c5dd7bf/images'
rows={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in old.glob('*.png')}
(R/'reviews/round-28c-diagnostic-image-identities.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
s=(R/'tools/diagnose_lantern_volume_28c.py').read_text(encoding='utf-8').replace('28c','28d')
s=s.replace('if(debug_mode>3.5)', 'if(debug_mode>3.5 && debug_mode<4.5)')
s=s.replace("shader_path.write_text(shader,encoding='utf-8')", "shader=shader.replace('    ALBEDO=vec3(0.);', '    ALBEDO=vec3(0.);').replace('    if(debug_mode>.5', '    if(debug_mode>4.5){ALBEDO=vec3(1.,.15,.02);EMISSION=vec3(0.);ALPHA=.35;}\\n    if(debug_mode>.5')\n            shader_path.write_text(shader,encoding='utf-8')")
s=s.replace('for debug_mode in [1.,2.,3.,4.,0.]:','for debug_mode in [1.,5.,0.]:')
s=s.replace('range(1,5)', '[1,5]')
s=s.replace('\\t\\tfor mesh in game.find_children', '\\t\\tvar matched:=0\n\\t\\tfor mesh in game.find_children')
s=s.replace('\\t\\t\\t\\tmesh.material_override.set_shader_parameter', '\\t\\t\\t\\tmatched+=1\n\\t\\t\\t\\tprint("OPTICAL ",mesh.get_path()," visible=",mesh.is_visible_in_tree()," layers=",mesh.layers," position=",mesh.global_position," shader=",mesh.material_override.shader.code.length())\n\\t\\t\\t\\tmesh.material_override.set_shader_parameter')
s=s.replace('\\t\\tfor i in range(40)', '\\t\\tassert(matched==8,"Eight real optical mesh overrides required")\n\\t\\tfor i in range(40)')
(R/'tools/diagnose_lantern_volume_28d.py').write_text(s,encoding='utf-8')
print(json.dumps(rows,indent=2))
