"""Correct stair winding and extend foundations below measured local slope lows."""
from pathlib import Path
root=Path(__file__).resolve().parents[1];target=root/'blender/model_lighthouse_19g.py';assert not target.exists()
text=(root/'blender/model_lighthouse_19f.py').read_text()
changes={"OUT=ROOT/'captures/lighthouse_study_19f'":"OUT=ROOT/'captures/lighthouse_study_19g'",
"mesh('Entry stone step %d'%step,verts,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],stone[1])":"mesh('Entry stone step %d'%step,verts,[tuple(reversed(face)) for face in [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]],stone[1])",
"headstone=material('Deep weathered gallery corbel stone',(.103,.096,.082))":"# Native terrain probes measured up to 0.26m below the origin at these feet.\n# Extend only foundation/step bottoms, keeping all visible top elevations.\nfor obj in parts:\n    if obj.name.startswith(('Broad octagonal foundation','Entry stone step')):\n        for vertex in obj.data.vertices:\n            if abs(vertex.co.z)<.0001:vertex.co.z=-.50\n        obj.data.update()\nheadstone=material('Deep weathered gallery corbel stone',(.103,.096,.082))"}
for old,new in changes.items():
    assert text.count(old)==1,old;text=text.replace(old,new)
text=text.replace("'height_m':24.5,","'top_above_origin_m':24.5,'footing_bottom_m':-.5,")
target.write_text(text);print(target)
