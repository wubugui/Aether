"""Respond to independent proportion/support rejection using frozen 19b geometry."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lighthouse_19c.py'
assert not target.exists()
text=(root/'blender/model_lighthouse_19b.py').read_text()
assert text.count("OUT=ROOT/'captures/lighthouse_study_19b'")==1
text=text.replace("OUT=ROOT/'captures/lighthouse_study_19b'","OUT=ROOT/'captures/lighthouse_study_19c'")
anchor="for obj in parts:obj['authoring_role']='independent lighthouse architectural part'"
change='''# Coordinated three-dimensional proportion edit, including openings and ladder.
# Compress the shaft 18%, widen its foot 10%, preserve upper lantern dimensions.
for obj in parts:
    matrix=obj.matrix_world.copy()
    for vertex in obj.data.vertices:
        p=matrix @ vertex.co
        widen=1.+.10*(1.-max(0.,min(1.,(p.z-.7)/20.)))
        p.x*=widen;p.y*=widen
        p.z=.7+(p.z-.7)*.82 if .7<p.z<=20.7 else (p.z-3.6 if p.z>20.7 else p.z)
        vertex.co=p
    obj.matrix_world.identity()
    obj.data.update()
headstone=material('Deep weathered gallery corbel stone',(.103,.096,.082))
cone('Thick octagonal gallery support',16.92,.86,2.13,2.92,headstone)
cone('Gallery underside projecting lip',17.37,.12,3.04,3.04,headstone)
'''+anchor
assert text.count(anchor)==1
text=text.replace(anchor,change)
text=text.replace("'height_m':28.1,'base_width_m':7.3","'height_m':24.5,'base_width_m':8.03")
target.write_text(text)
print(target)
