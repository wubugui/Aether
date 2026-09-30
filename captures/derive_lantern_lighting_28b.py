"""Use manual scene-depth clipping for backface volume integration."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'captures/lantern_volume_28a.gdshader').read_text(encoding='utf-8')
p=p.replace('cull_front,depth_draw_never,fog_disabled','cull_front,depth_draw_never,depth_test_disabled,fog_disabled')
(R/'captures/lantern_volume_28b.gdshader').write_text(p,encoding='utf-8')
p=(R/'captures/lantern_lighting_28a.gd').read_text(encoding='utf-8')
(R/'captures/lantern_lighting_28b.gd').write_text(p,encoding='utf-8')
p=(R/'tools/render_lantern_lighting_28a.py').read_text(encoding='utf-8').replace('28a','28b')
p=p.replace("native=root/'captures/lantern_volume_assets_28b';gate=root/'reviews/round-28b-lantern-native-check.json'","native=root/'captures/lantern_volume_assets_28a';gate=root/'reviews/round-28a-lantern-native-check.json'")
p=p.replace('Four new fixed spatial lighthouse beams, editable Blender control volumes,','28b disables hardware depth testing for the volume backfaces, retaining explicit fragment scene-depth clipping. Exact28a editable Blender control volumes and four fixed beams,')
(R/'tools/render_lantern_lighting_28b.py').write_text(p,encoding='utf-8')
print('28b manual scene-depth volume clipping candidate prepared')
