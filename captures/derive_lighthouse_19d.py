"""Flush Blender transforms before baking the coordinated 19c proportion edit."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lighthouse_19d.py'
assert not target.exists()
text=(root/'blender/model_lighthouse_19c.py').read_text()
old="OUT=ROOT/'captures/lighthouse_study_19c'"
assert text.count(old)==1
text=text.replace(old,"OUT=ROOT/'captures/lighthouse_study_19d'")
old='for obj in parts:\n    matrix=obj.matrix_world.copy()'
assert text.count(old)==1
text=text.replace(old,'bpy.context.view_layer.update()\n'+old)
target.write_text(text)
print(target)
