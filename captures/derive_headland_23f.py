from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'blender/model_headland_23e.py').read_text(encoding='utf-8').replace('headland_study_23e','headland_study_23f').replace("'label':'23e'","'label':'23f'")
old='strength=1-smooth(nearest[0][0]/14);target=target*(1-strength)+pad*strength'
new='''# The outside-pad blend vanishes at the shore and reaches the exact pad level at its edge.
        shore_weight=smooth(d/max(.000001,d+nearest[0][0]))
        strength=(1-smooth(nearest[0][0]/14))*shore_weight
        target=target*(1-strength)+pad*strength'''
assert old in code;code=code.replace(old,new)
target=root/'blender/model_headland_23f.py';assert not target.exists();target.write_text(code,encoding='utf-8')
runtime=(root/'captures/headland_runtime_23e.gd').read_text(encoding='utf-8').replace('23e','23f')
(root/'captures/headland_runtime_23f.gd').write_text(runtime,encoding='utf-8')
driver=(root/'tools/render_headland_23e.py').read_text(encoding='utf-8').replace('23e','23f')
# Same five relevant geometry views; old harbor-wide validation remains bound instead of rerun.
(root/'tools/render_headland_23f.py').write_text(driver,encoding='utf-8')
