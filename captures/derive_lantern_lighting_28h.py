"""Consolidate only supported changes:28f optics, beam energy1.3, core shadows on."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
a=(R/'captures/lantern_lighting_28f.gd').read_text(encoding='utf-8')
assert a.count('1.7 if kind>.5 else .65')==1
a=a.replace('1.7 if kind>.5 else .65','1.7 if kind>.5 else 1.3')
(R/'captures/lantern_lighting_28h.gd').write_text(a,encoding='utf-8')
s=(R/'tools/diagnose_lantern_receivers_28g.py').read_text(encoding='utf-8')
s=s.replace('28g','28h').replace('lantern-receiver-28h','lantern-lighting-28h')
s=s.replace('["baseline","core-transmits","beam-boost"]','["beam-only"]')
s=s.replace("['baseline','core-transmits','beam-boost']","['beam-only']")
s=s.replace('''\t\tif variant=="core-transmits":
\t\t\tfor mesh in core_nodes:mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
\t\tif variant=="beam-boost":
\t\t\tfor mesh in optical_meshes:mesh.material_override.set_shader_parameter("light_energy",1.3)
''','')
s=s.replace('Single loaded actual world. Baseline28f; core-transmits changes only four luminous-core shadow casters; beam-boost additionally doubles unshaded beam energy .65 to1.3. Native lights, opaque frame/roof, transparent glass and density geometry stay unchanged.', 'Final28h actual world:28f analytic optical shader, beam energy1.3, original four luminous-core shadow casters ON. All lamp/receiver materials, native light intensities and glass stay28f. Three fixed cameras from one scene.')
s=s.replace("One real GPU scene load; nine fixed-camera A/B/C images isolate source-core shadow blocking from beam intensity. No production or geometry rebuild.","Final28h consolidation: three fixed cameras,28f analytic optical intervals, beam energy1.3, original core shadows ON. No production or geometry rebuild.")
anchor="p=frozen/'preview.gd';s=p.read_text(encoding='utf-8');anchor="
s=s.replace(anchor,"shutil.copy2(root/'captures/lantern_lighting_28h.gd',frozen/'lantern_lighting_28h.gd')\n            p=frozen/'preview.gd';s=p.read_text(encoding='utf-8').replace('lantern_lighting_28f.gd','lantern_lighting_28h.gd');anchor=")
s=s.replace("(1 if variant=='baseline' else 0)",'1')
s=s.replace("(1.3 if variant=='beam-boost' else .65)",'1.3')
s=s.replace('beam-side-final-boost','beam-side-final28h')
s=s.replace('28h RECEIVER COMPARISON','28h FINAL LANTERN VIEWS')
(R/'tools/render_lantern_lighting_28h.py').write_text(s,encoding='utf-8')
