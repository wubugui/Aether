"""Create a new editable builder without overwriting 19a or its evidence."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lighthouse_19b.py'
assert not target.exists()
text=(root/'blender/model_lighthouse_19a.py').read_text()
replacements={
"OUT=ROOT/'captures/lighthouse_study_19a'":"OUT=ROOT/'captures/lighthouse_study_19b'",
"[(.47,.455,.40),(.52,.50,.44),(.57,.54,.47),(.49,.48,.44)]":"[(.195,.184,.158),(.215,.205,.178),(.238,.223,.189),(.206,.199,.179)]",
"(.38,.37,.32)":"(.155,.144,.119)",
"glass=material('Warm lantern glazing',(.68,.42,.14),0,.32)":"glass=material('Clear slightly amber lantern glass',(.25,.20,.12))\nglass.diffuse_color=(.25,.20,.12,.16)\nglass.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=.16\nglass.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.22\nglass.surface_render_method='DITHERED'",
"# Frosted panels are separate recessed solid surfaces; no fake beam geometry.":"# Transparent real panes reveal the central lamp and lens assembly.",
"cone('Lamp reflector',23.18,1.75,.58,.58,core,12)":"cone('Central luminous lamp',23.20,1.38,.16,.16,core,12)\ncone('Lamp bronze base',22.28,.45,.42,.27,iron,12)\ncone('Lamp reflector crown',24.09,.38,.74,.25,iron,12)\nfor k in range(9):\n    z=22.56+k*.15\n    cone('Fresnel lens tier %02d'%k,z,.10,.59+(.10 if k==4 else 0),.56,glass,16)\nfor k in range(4):\n    a=k*math.tau/4\n    bar('Lens cage rod %d'%k,(.67*math.cos(a),.67*math.sin(a),22.50),(.67*math.cos(a),.67*math.sin(a),23.97),.022,iron)",
}
for old,new in replacements.items():
    assert text.count(old)==1,old
    text=text.replace(old,new)
target.write_text(text)
print(target)
